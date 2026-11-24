from pathlib import Path
import re
from playwright.sync_api import Locator, Page, expect
from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.logger import logger


class UA_customs_Page:
    URL = settings.ua_customs_url
    DEFAULT_TIMEOUTS_MS = settings.default_timeout_ms
    DOWNLOAD_TIMEOUT_MS = settings.download_timeout_ms
    # lokalizatory
    def __init__(self, page: Page):
        self.page = page

        self.main_table = page.get_by_role("grid").first
        self.no_selections_banner = page.get_by_text(
            re.compile(r"No selections applied|Вибірки не застосовані|Выборки не применены")
        )
        self.Year = page.get_by_test_id("collapsed-title-Year").locator("div").filter(has_text=re.compile(r"^Year$"))
        self.Currency = page.get_by_test_id("collapsed-title-Currency").locator("div").filter(has_text=re.compile(r"^Currency$"))
        self.Region = page.get_by_test_id("collapsed-title-Region").locator("div").filter(has_text=re.compile(r"^Region$"))
        self.HS_Chapter = page.get_by_test_id("collapsed-title-HS Chapter").locator("div").filter(has_text=re.compile(r"^HS Chapter$"))

        self.search_filter_region = page.get_by_role(
            "region",
            name=re.compile(r"Search Results Filter|Фильтр результатов поиска|Фільтр результатів пошуку"),
        )
        self.search_input = page.get_by_test_id("search-input-field")
        self.confirm_button = page.get_by_test_id("actions-toolbar-confirm")
        self.download_button = page.get_by_role("button", name="Download")
    # akcje
    def open(self):
        logger.info(f"Otwieram stronę: {self.URL}")
        self.page.goto(self.URL)
        expect(self.main_table).to_be_visible(timeout=self.DEFAULT_TIMEOUTS_MS)
        logger.success("Strona załadowana")

    def select_year(self, year: str | int):
        logger.info(f"Wybieram rok: {year}")
        self._select_from_filter(self.Year, str(year))

    def select_currency(self, currency: str):
        logger.info(f"Wybieram walutę: {currency}")
        self._select_from_filter(self.Currency, str(currency))

    def select_region(self, region: str):
        logger.info(f"Wybieram kraj: {region}")
        self._select_from_filter(self.Region, region)

    def select_hs_chapter(self, hs_chapter: str):
        logger.info(f"Wybieram HS Chapter: {hs_chapter}")
        self._select_from_filter(self.HS_Chapter, hs_chapter)

    def _wait_for_recalculation(self) -> None:
        #czekaj az silnik BI nalozy filtry
        expect(self.search_filter_region).to_be_hidden(timeout=self.DEFAULT_TIMEOUTS_MS)
        expect(self.no_selections_banner).to_be_hidden(timeout=self.DEFAULT_TIMEOUTS_MS)
        expect(self.page.locator('[aria-busy="true"]')).to_have_count(0, timeout=self.DEFAULT_TIMEOUTS_MS)
        expect(self.main_table).to_be_visible(timeout=self.DEFAULT_TIMEOUTS_MS)
        self.page.wait_for_timeout(1000)

    def _select_from_filter(self, filter_locator: Locator, value: str):
        logger.debug(f"Otwieram filtr {filter_locator} i wpisuję: {value}")
        filter_locator.click()
        expect(self.search_filter_region).to_be_visible(timeout=self.DEFAULT_TIMEOUTS_MS)
        self.search_input.click()
        self.search_input.fill(value)

        matching_row = self.search_filter_region.get_by_role(
            "row", name=re.compile(re.escape(value), re.IGNORECASE)
        ).first
        expect(matching_row).to_be_visible(timeout=self.DEFAULT_TIMEOUTS_MS)

        self.search_input.press("Enter")
        expect(self.search_filter_region.locator('[aria-selected="true"]').first).to_be_visible(
            timeout=self.DEFAULT_TIMEOUTS_MS
        )
        self.confirm_button.click()
        self._wait_for_recalculation()
        logger.debug(f"Zatwierdzono wartość filtra {filter_locator}: {value}")

    def download(self, folder: str | Path = settings.raw_dir) -> Path:
        logger.info("pobieram dane")
        self._wait_for_recalculation()
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

