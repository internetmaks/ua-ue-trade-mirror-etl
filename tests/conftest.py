from pathlib import Path
import pandas as pd
import pytest
from ua_ue_trade_mirror_etl.transform.cleaner import parse_ua_customs_excel


@pytest.fixture
def sample_xlsx() -> Path:
    return Path(__file__).parent / "fixtures" / "sample_ua_customs.xlsx"


@pytest.fixture
def sample_filtered_xlsx() -> Path:
    return Path(__file__).parent / "fixtures" / "sample_ua_2025_eu_1001.xlsx"


@pytest.fixture
def ua_2025_df(sample_filtered_xlsx: Path) -> pd.DataFrame:
    return parse_ua_customs_excel(sample_filtered_xlsx, year=2025, hs_chapter="1001")
