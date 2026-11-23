import io
import httpx
import pandas as pd
from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.logger import logger
from ua_ue_trade_mirror_etl.models import MirrorTradeRecord


class EurostatComextClient:
    BASE_URL = settings.eurostat_base_url

    def __init__(self, timeout_sec: float = settings.default_timeout_ms / 1000) -> None:
        self.timeout = timeout_sec

    def get_eur_to_usd_rate(self) -> float:
            #dynamiczne przewalutowanie eur na dolara
        with httpx.Client(timeout=10.0) as client:
            eur_pln = client.get("https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json").json()["rates"][0]["mid"]
            usd_pln = client.get("https://api.nbp.pl/api/exchangerates/rates/a/usd/?format=json").json()["rates"][0]["mid"]
        return round(eur_pln / usd_pln, 4)

    def fetch_trade_with_ukraine(
        self,
        reporter_iso2: str,
        hs_chapter: str = settings.target_hs_chapter,
        year: int = settings.target_year,
    ) -> MirrorTradeRecord:
        #import i expott
        sdmx_key = f"M.{reporter_iso2.upper()}.UA.{hs_chapter}.1+2.VALUE_IN_EUROS"
        url = f"{self.BASE_URL}/{sdmx_key}"
        params = {
            "startPeriod": f"{year}-01",
            "endPeriod": f"{year}-12",
            "format": "SDMX-CSV",
        }

        logger.info(f"Querying Eurostat Comext: {url} ({params['startPeriod']}..{params['endPeriod']})")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()

        df = pd.read_csv(io.StringIO(response.text))
        total_eur = pd.to_numeric(df["OBS_VALUE"], errors="coerce").fillna(0.0).sum()

        eur_usd = self.get_eur_to_usd_rate()
        total_usd = round(float(total_eur) * eur_usd, 2)

        logger.success(
            f"Eurostat {reporter_iso2}<-UA (HS {hs_chapter}, {year}): "
            f"{total_eur:,.2f} EUR -> {total_usd:,.2f} USD (rate: {eur_usd})"
        )

        return MirrorTradeRecord(
            source_system="eurostat_comext",
            reporter_iso2=reporter_iso2.upper(),
            year=year,
            hs_chapter=hs_chapter,
            data_status="provisional",
            import_usd=total_usd,
        )
