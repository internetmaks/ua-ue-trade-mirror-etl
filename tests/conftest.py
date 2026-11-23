from pathlib import Path
import pytest

@pytest.fixture
def sample_xlsx() -> Path:
    return Path(__file__).parent / "fixtures" / "sample_ua_customs.xlsx"
