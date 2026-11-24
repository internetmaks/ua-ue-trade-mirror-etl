import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
def _parse_csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings(BaseModel):
    # domyslne parametry wspólne dla UA Customs i Eurostat
    target_year: int = Field(default=int(os.getenv("TARGET_YEAR", "2024")))
    target_currency: str = Field(default=os.getenv("TARGET_CURRENCY", "usd"))
    target_region: str = Field(default=os.getenv("TARGET_REGION", "eu"))
    target_hs_chapter: str = Field(default=os.getenv("TARGET_HS_CHAPTER", "1001"))
    eu_countries: list[str] = Field(
        default_factory=lambda: _parse_csv_env("EU_COUNTRIES", "PL,DE,RO,HU,SK,ES,IT,NL,FR")
    )

    # Źródła danych i limity czasu
    ua_customs_url: str = Field(
        default=os.getenv("UA_CUSTOMS_URL", "https://bi.customs.gov.ua/en/trade/import-export")
    )
    eurostat_base_url: str = Field(
        default=os.getenv(
            "EUROSTAT_BASE_URL",
            "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/2.1/data/ds-045409",
        )
    )
    headless: bool = Field(default=os.getenv("HEADLESS", "false").lower() == "true")
    default_timeout_ms: int = Field(default=int(os.getenv("DEFAULT_TIMEOUT_MS", "20000")))
    download_timeout_ms: int = Field(default=int(os.getenv("DOWNLOAD_TIMEOUT_MS", "60000")))

    # Ścieżki
    raw_dir: Path = Field(default=Path(os.getenv("RAW_DIR", "data/raw")))
    output_dir: Path = Field(default=Path(os.getenv("OUTPUT_DIR", "data/output")))
    log_file: Path = Field(default=Path(os.getenv("LOG_FILE", "logs/pytest.log")))


settings = Settings()
