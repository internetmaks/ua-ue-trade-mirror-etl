import pandas as pd
import pytest
from pydantic import ValidationError
from ua_ue_trade_mirror_etl.models import EurostatTradeRecord, UAcustomsRecord


def test_real_ua_rows_pass_pydantic_validation(ua_2025_df: pd.DataFrame) -> None:
    assert len(ua_2025_df) == 21
    records = [UAcustomsRecord(**row) for row in ua_2025_df.to_dict(orient="records")]
    assert records[0].partner_iso2 == "ES"
    assert records[0].source_system == "ua_customs"


def test_real_row_with_corrupted_total_raises_validation_error(ua_2025_df: pd.DataFrame) -> None:
    first_row = ua_2025_df.iloc[0].to_dict()
    first_row["total_value_usd"] = first_row["total_value_usd"] + 500.0

    with pytest.raises(ValidationError, match="total_value_usd"):
        UAcustomsRecord(**first_row)


def test_real_row_with_corrupted_balance_raises_validation_error(ua_2025_df: pd.DataFrame) -> None:
    first_row = ua_2025_df.iloc[0].to_dict()
    first_row["balance_usd"] = first_row["balance_usd"] - 500.0

    with pytest.raises(ValidationError, match="balance_usd"):
        UAcustomsRecord(**first_row)


def test_eurostat_trade_record_accepts_real_2025_pl_values() -> None:
    record = EurostatTradeRecord(
        reporter_iso2="PL",
        year=2025,
        hs_chapter="1001",
        export_usd=38164.03,
        import_usd=738799.45,
    )
    assert record.source_system == "eurostat_comext"
    assert record.data_status == "provisional"
