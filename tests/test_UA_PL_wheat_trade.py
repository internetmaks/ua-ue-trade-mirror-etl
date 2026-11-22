
from playwright.sync_api import Page
from utils.logger_config import logger
from pages.ua_customs_import_export import UA_customs_Page


@logger.catch(reraise=True)
def test_example(page: Page) -> None:
    UAcustoms=UA_customs_Page(page) 
    UAcustoms.open()
    UAcustoms.select_year("2025")
    UAcustoms.select_currency("usd")
    UAcustoms.select_region("eu")
    UAcustoms.select_hs_chapter("1001")
    UAcustoms.download()