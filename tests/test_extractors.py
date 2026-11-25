from pathlib import Path
import pytest
from playwright.sync_api import Page
from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.extractors.eurostat_comext import EurostatComextClient
from ua_ue_trade_mirror_etl.extractors.ukraine_customs import UA_customs_Page
from ua_ue_trade_mirror_etl.transform.cleaner import parse_ua_customs_excel

pytestmark = pytest.mark.integration


def test_nbp_eur_to_usd_rate_real_api() -> None:
    client = EurostatComextClient()
    rate = client.get_eur_to_usd_rate()
    assert 0.5 < rate < 2.0


def test_eurostat_fetch_trade_real_api_pl_2025() -> None:
    client = EurostatComextClient()
    record = client.fetch_trade_with_ukraine("PL", hs_chapter="1001", year=2025)

    assert record.reporter_iso2 == "PL"
    assert record.year == 2025
    assert record.hs_chapter == "1001"
    assert record.import_usd > 0
    assert record.export_usd >= 0


def test_ua_customs_scraper_downloads_real_xlsx(page: Page, tmp_path: Path) -> None:
    customs = UA_customs_Page(page)
    customs.open()
    customs.select_year(settings.target_year)
    customs.select_currency(settings.target_currency)
    customs.select_region(settings.target_region)
    customs.select_hs_chapter(settings.target_hs_chapter)
    downloaded = customs.download(folder=tmp_path)

    assert downloaded.exists()
    assert downloaded.suffix == ".xlsx"
    df = parse_ua_customs_excel(downloaded, year=settings.target_year, hs_chapter=settings.target_hs_chapter)
    assert not df.empty
