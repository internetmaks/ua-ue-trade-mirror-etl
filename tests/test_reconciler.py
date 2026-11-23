import pandas as pd
import pytest
from ua_ue_trade_mirror_etl.models import EurostatTradeRecord
from ua_ue_trade_mirror_etl.transform.reconciler import reconcile_trade_mirror


def test_reconcile_trade_mirror_checks_both_directions() -> None:
    ua_df = pd.DataFrame([
        {
            "partner_iso2": "PL",
            "partner_name": "Poland",
            "year": 2025,
            "hs_chapter": "1001",
            "export_usd": 100.0,
            "import_usd": 50.0,
        },
        {
            "partner_iso2": "DE",
            "partner_name": "Germany",
            "year": 2025,
            "hs_chapter": "1001",
            "export_usd": 200.0,
            "import_usd": 100.0,
        },
    ])
    eu_records = [
        EurostatTradeRecord(reporter_iso2="PL", year=2025, hs_chapter="1001", import_usd=95.0, export_usd=80.0),
        EurostatTradeRecord(reporter_iso2="DE", year=2025, hs_chapter="1001", import_usd=190.0, export_usd=95.0),
    ]

    result = reconcile_trade_mirror(ua_df, eu_records, tolerance_pct=15.0)
    assert len(result) == 2

    pl = result[result["partner_iso2"] == "PL"].iloc[0]
    assert bool(pl["ua_export_matches"]) is True
    assert bool(pl["ua_import_matches"]) is False
    assert bool(pl["matches_all"]) is False

    de = result[result["partner_iso2"] == "DE"].iloc[0]
    assert de["ua_export_gap_usd"] == pytest.approx(10.0)
    assert bool(de["matches_all"]) is True


def test_reconcile_handles_zeros_and_empty_inputs() -> None:
    empty_res = reconcile_trade_mirror(pd.DataFrame(), [])
    assert empty_res.empty

    ua_df = pd.DataFrame([
        {"partner_iso2": "PL", "partner_name": "Poland", "year": 2025, "hs_chapter": "1001", "export_usd": 0.0, "import_usd": 0.0}
    ])
    eu_records = [
        EurostatTradeRecord(reporter_iso2="PL", year=2025, hs_chapter="1001", import_usd=0.0, export_usd=0.0)
    ]

    res = reconcile_trade_mirror(ua_df, eu_records)
    assert res.iloc[0]["ua_export_gap_pct"] == 0.0
    assert bool(res.iloc[0]["matches_all"]) is True
