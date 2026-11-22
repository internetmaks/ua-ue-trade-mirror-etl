from pathlib import Path
import re
from playwright.sync_api import Locator, Page, expect
from utils.logger_config import logger


class UA_customs_Page:
    URL = "https://bi.customs.gov.ua/en/trade/import-export"
    DEFAULT_TIMEOUTS_MS = 20000
    DOWNLOAD_TIMEOUT_MS = 60000
    #lokalizatory
    def __init__(self, page: Page):
        self.page = page

        self.main_table = page.get_by_role("application", name="Таблиця \xa0 Country") #nie przetłumaczony ARIA
        self.Year = page.get_by_test_id("collapsed-title-Year").locator("div").filter(has_text=re.compile(r"^Year$"))
        self.Currency = page.get_by_test_id("collapsed-title-Currency").locator("div").filter(has_text=re.compile(r"^Currency$"))
        self.Country = page.get_by_test_id("collapsed-title-Country").locator("div").filter(has_text=re.compile(r"^Country$"))
        self.HS_Chapter = page.get_by_test_id("collapsed-title-HS Chapter").locator("div").filter(has_text=re.compile(r"^HS Chapter$"))

        self.search_filter_region = page.get_by_role("region", name="Фильтр результатов поиска")#nie przetłumaczony ARIA
        self.search_input = page.get_by_test_id("search-input-field")
        self.download_button = page.get_by_role("button", name="Download")
    #akcje
    def open(self):
        logger.info(f"Otwieram stronę: {self.URL}")
        self.page.goto(self.URL)
        expect(self.main_table,timeout=self.DEFAULT_TIMEOUTS_MS).to_be_visible()
        logger.success("Strona załadowana")

    def select_year(self, year: str | int):
        logger.info(f"Wybieram rok: {year}")
        self._select_from_filter(self.Year, str(year))

    def select_currency(self, currency: str):
        logger.info(f"Wybieram walutę: {currency}")
        self._select_from_filter(self.Currency, str(currency))

    def select_country(self, country: str):
        logger.info(f"Wybieram kraj: {country}")
        self._select_from_filter(self.Country, country)

    def select_hs_chapter(self, hs_chapter: str):
        logger.info(f"Wybieram HS Chapter: {hs_chapter}")
        self._select_from_filter(self.HS_Chapter, hs_chapter)

    def _select_from_filter(self, filter_locator: Locator, value: str):
        logger.debug(f"Otwieram filtr {filter_locator} i wpisuję: {value}")
        filter_locator.click()
        expect(self.search_filter_region,timeout=self.DEFAULT_TIMEOUTS_MS).to_be_visible()
        self.search_input.click()
        self.search_input.fill(value)
    
        matching_row = self.search_filter_region.get_by_role(
            "row", name=re.compile(re.escape(value), re.IGNORECASE)).first
        expect(matching_row,timeout=self.DEFAULT_TIMEOUTS_MS).to_be_visible()
    
        self.search_input.press("Enter")
        expect(self.main_table,timeout=self.DEFAULT_TIMEOUTS_MS).to_be_visible()
        logger.debug(f"Zatwierdzono wartość filtra {filter_locator}: {value}")

    def download(self, folder: str = "downloads") -> Path:
        logger.info("pobieram dane")
        Path(folder).mkdir(parents=True, exist_ok=True)
        with self.page.expect_download(timeout=self.DOWNLOAD_TIMEOUT_MS) as download_info:
            with self.page.expect_popup(timeout=self.DOWNLOAD_TIMEOUT_MS) as popup_info:
                self.download_button.click()
            popup_info.value
        download = download_info.value
        path = Path(folder) / download.suggested_filename
        download.save_as(path)
        logger.success(f"Zapisano pobrane dane: {path}")
        return path
