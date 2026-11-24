import importlib.util
from pathlib import Path
from playwright.sync_api import sync_playwright
from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.extractors.eurostat_comext import EurostatComextClient
from ua_ue_trade_mirror_etl.extractors.ukraine_customs import UA_customs_Page
from ua_ue_trade_mirror_etl.logger import logger
from ua_ue_trade_mirror_etl.storage import df_to_csv, save_anomalies
from ua_ue_trade_mirror_etl.transform.cleaner import parse_ua_customs_excel
from ua_ue_trade_mirror_etl.transform.reconciler import reconcile_trade_mirror


def extract_ua_customs() -> Path:
    #odpala playwright wedlug configu
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.headless)
        page = browser.new_page()
        try:
            customs = UA_customs_Page(page)
            customs.open()
            customs.select_year(settings.target_year)
            customs.select_currency(settings.target_currency)
            customs.select_region(settings.target_region)
            customs.select_hs_chapter(settings.target_hs_chapter)
            return customs.download(settings.raw_dir)
        finally:
            page.close()
            browser.close()


@logger.catch(reraise=True)
def run_pipeline(raw_xlsx_path: Path | None = None) -> Path:
    #jak nie ma xlxsa to scrapuje
    logger.info("Startuje pipeline UA-UE trade mirror ETL")

    if raw_xlsx_path is None:
        raw_xlsx_path = extract_ua_customs()
    #parsowanie xlxsa
    ua_df = parse_ua_customs_excel(raw_xlsx_path)
    df_to_csv(ua_df, "ua_customs_clean.csv")
    #laczy z api eurostatu i pobiera 
    eurostat = EurostatComextClient()
    eu_records = [eurostat.fetch_trade_with_ukraine(iso2) for iso2 in settings.eu_countries]
    #porownuje dane z UA i EU w obie strony import/export
    reconciled_df = reconcile_trade_mirror(ua_df, eu_records)
    #zapisuje polaczone pliki csv
    output_path = df_to_csv(reconciled_df, "trade_mirror.csv")
    save_anomalies(reconciled_df)

    chart_script = Path(__file__).resolve().parents[2] / "scripts" / "generate_chart.py"
    if chart_script.exists():
        spec = importlib.util.spec_from_file_location("generate_chart", chart_script)
        if spec and spec.loader:
            chart_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(chart_mod)
            chart_mod.generate_trade_mirror_chart(csv_path=output_path)

    logger.success(f"Pipeline zakończony: {output_path}")
    return output_path


if __name__ == "__main__":
    run_pipeline()
