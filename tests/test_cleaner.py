from pathlib import Path
import pandas as pd
import pytest
from ua_ue_trade_mirror_etl.transform.cleaner import parse_ua_customs_excel


def test_parse_ua_customs_excel_parses_poland(sample_xlsx: Path) -> None:
    
    df = parse_ua_customs_excel(sample_xlsx, year=2025, hs_chapter="1001")
    assert not df.empty
    assert "PL" in df["partner_iso2"].values

    poland = df[df["partner_iso2"] == "PL"].iloc[0]
    assert poland["partner_name"] == "Poland"
    assert poland["export_usd"] > 0


def test_parse_skips_non_iso_and_invalid_rows(tmp_path: Path) -> None:
    fake_xlsx = tmp_path / "dirty.xlsx"
    pd.DataFrame([
        {"Country": "-", "Total Value of Goods, USD": 0, "Export, USD": 0, "Import, USD": 0, "Balance, USD": 0},
        {"Country": "Unspecified", "Total Value of Goods, USD": 100, "Export, USD": 100, "Import, USD": 0, "Balance, USD": 100},
        {"Country": "DE Germany", "Total Value of Goods, USD": 999, "Export, USD": 10, "Import, USD": 5, "Balance, USD": 5},
        {"Country": "PL Poland", "Total Value of Goods, USD": 150, "Export, USD": 100, "Import, USD": 50, "Balance, USD": 50},
    ]).to_excel(fake_xlsx, index=False)

    df = parse_ua_customs_excel(fake_xlsx, year=2025, hs_chapter="1001")

    assert len(df) == 1
    assert df.iloc[0]["partner_iso2"] == "PL"


def test_parse_cleans_whitespace_and_commas(tmp_path: Path) -> None:
    fake_xlsx = tmp_path / "formatted.xlsx"
    pd.DataFrame([
        {
            "Country": "  PL\xa0Poland ",
            "Total Value of Goods, USD": "1\xa0500,50",
            "Export, USD": "1 000,25",
            "Import, USD": "500,25",
            "Balance, USD": "500,00",
        }
    ]).to_excel(fake_xlsx, index=False)

    df = parse_ua_customs_excel(fake_xlsx, year=2025, hs_chapter="1001")

    assert len(df) == 1
    row = df.iloc[0]
    assert row["total_value_usd"] == pytest.approx(1500.50)
    assert row["export_usd"] == pytest.approx(1000.25)
    assert row["import_usd"] == pytest.approx(500.25)
    assert row["balance_usd"] == pytest.approx(500.00)
