import pytest
from pydantic import ValidationError
from ua_ue_trade_mirror_etl.models import EurostatTradeRecord, UAcustomsRecord


def test_ua_customs_record_validates_consistent_math() -> None:
    record = UAcustomsRecord(
        partner_iso2="PL",
        partner_name="Poland",
        year=2025,
        hs_chapter="1001",
        total_value_usd=150.0,
        export_usd=100.0,
        import_usd=50.0,
        balance_usd=50.0,
    )
    assert record.source_system == "ua_customs"
    assert record.partner_iso2 == "PL"


def test_ua_customs_record_rejects_total_mismatch() -> None:
    with pytest.raises(ValidationError, match="total_value_usd"):
        UAcustomsRecord(
            partner_iso2="PL",
            partner_name="Poland",
            year=2025,
            hs_chapter="1001",
            total_value_usd=999.0,
            export_usd=100.0,
            import_usd=50.0,
            balance_usd=50.0,
        )


def test_ua_customs_record_rejects_balance_mismatch() -> None:
    with pytest.raises(ValidationError, match="balance_usd"):
        UAcustomsRecord(
            partner_iso2="PL",
            partner_name="Poland",
            year=2025,
            hs_chapter="1001",
            total_value_usd=150.0,
            export_usd=100.0,
            import_usd=50.0,
            balance_usd=999.0,
        )


def test_eurostat_trade_record_defaults() -> None:
    record = EurostatTradeRecord(
        reporter_iso2="PL",
        year=2025,
        hs_chapter="1001",
        export_usd=200.0,
        import_usd=300.0,
    )
    assert record.source_system == "eurostat_comext"
    assert record.data_status == "provisional"
