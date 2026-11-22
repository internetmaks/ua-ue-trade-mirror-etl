import re
import pytest
from playwright.sync_api import Page, expect
from logger_config import logger


@pytest.mark.skip_browser("firefox") # type: ignore
def test_has_title(page: Page):
    logger.info("Opening https://playwright.dev/")
    page.goto("https://playwright.dev/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Playwright"))

@pytest.mark.only_browser("chromium")
def test_get_started_link(page: Page):
    logger.info("Opening https://playwright.dev/")
    page.goto("https://playwright.dev/")

    # Click the get started link.
    page.get_by_role("link", name="Get started").click()
    logger.info("clicking the get started link")
    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
    logger.info("checking if heading is \"installation\" ")
