import pandas as pd
import pytest
from ua_ue_trade_mirror_etl.models import EurostatTradeRecord
from ua_ue_trade_mirror_etl.transform.reconciler import reconcile_trade_mirror


def test_reconcile_real_2025_ua_and_eu_data(ua_2025_df: pd.DataFrame) -> None:
    # Real 2025 Eurostat values for LT, DE, NL (HS 1001)
    eu_records = [
        EurostatTradeRecord(reporter_iso2="LT", year=2025, hs_chapter="1001", import_usd=571866.79, export_usd=0.0),
        EurostatTradeRecord(reporter_iso2="DE", year=2025, hs_chapter="1001", import_usd=5324347.38, export_usd=451519.53),
        EurostatTradeRecord(reporter_iso2="NL", year=2025, hs_chapter="1001", import_usd=9266971.74, export_usd=0.0),
    ]

    result = reconcile_trade_mirror(ua_2025_df, eu_records, tolerance_pct=15.0)
    assert len(result) == 3

    lt = result[result["partner_iso2"] == "LT"].iloc[0]
    assert lt["ua_export_gap_pct"] == pytest.approx(2.57)
    assert bool(lt["matches_all"]) is True

    de = result[result["partner_iso2"] == "DE"].iloc[0]
    assert de["ua_export_gap_pct"] == pytest.approx(8.96)
    assert de["ua_import_gap_pct"] == pytest.approx(0.47)
    assert bool(de["matches_all"]) is True

    nl = result[result["partner_iso2"] == "NL"].iloc[0]
    assert nl["ua_export_gap_pct"] == pytest.approx(81.84)
    assert bool(nl["matches_all"]) is False


def test_reconcile_handles_empty_input() -> None:
    empty_res = reconcile_trade_mirror(pd.DataFrame(), [])
    assert empty_res.empty
