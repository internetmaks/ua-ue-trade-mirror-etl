from pathlib import Path
import pandas as pd
from pydantic import ValidationError
from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.logger import logger
from ua_ue_trade_mirror_etl.models import UAcustomsRecord


def parse_ua_customs_excel(
    file_path: Path | str,
    year: int = settings.target_year,
    hs_chapter: str = settings.target_hs_chapter,
) -> pd.DataFrame:
    logger.info(f"Parsuje plik Excel: {file_path} (year={year}, hs_chapter={hs_chapter})")
    df = pd.read_excel(file_path, engine="openpyxl")
    logger.debug(f"Wczytano {len(df)} wierszy")

    extracted = df["Country"].astype(str).str.strip().str.extract(r"^([A-Z]{2})\s+(.+)$")
    df["partner_iso2"] = extracted[0]
    df["partner_name"] = extracted[1]

    skipped_countries = df.loc[df["partner_iso2"].isna(), "Country"].tolist()
    if skipped_countries:
        logger.info(f"Pominięto {len(skipped_countries)} wierszy bez kodu ISO: {skipped_countries}")

    df = df.dropna(subset=["partner_iso2"]).copy()

    num_cols = ["Total Value of Goods, USD", "Export, USD", "Import, USD", "Balance, USD"]
    for col in num_cols:
        df[col] = (
            df[col].astype(str)
            .str.replace(r"[\s\xa0]", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    valid_rows = []
    for row in df.to_dict(orient="records"):
        try:
            record = UAcustomsRecord(
                partner_iso2=row["partner_iso2"],
                partner_name=row["partner_name"],
                year=year,
                hs_chapter=hs_chapter,
                total_value_usd=row["Total Value of Goods, USD"],
                export_usd=row["Export, USD"],
                import_usd=row["Import, USD"],
                balance_usd=row["Balance, USD"],
            )
            valid_rows.append(record.model_dump())
        except ValidationError as exc:
            logger.warning(f"Skipping invalid row ({row.get('Country')}): {exc}")

    logger.success(f"Zwalidowano {len(valid_rows)} rekordów z {file_path}")
    return pd.DataFrame(valid_rows)