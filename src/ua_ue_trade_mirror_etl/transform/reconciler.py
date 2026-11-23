import pandas as pd
from ua_ue_trade_mirror_etl.logger import logger
from ua_ue_trade_mirror_etl.models import EurostatTradeRecord


def reconcile_trade_mirror(
    ua_df: pd.DataFrame,
    eu_records: list[EurostatTradeRecord],
    tolerance_pct: float = 15.0,
) -> pd.DataFrame:
    # UA exports vs EU imports i UA imports vs EU exports
    if ua_df.empty or not eu_records:
        logger.warning("Brak danych do zestawienia w reconcilerze")
        return pd.DataFrame()

    eu_df = pd.DataFrame([r.model_dump() for r in eu_records])
    #inner join 
    merged = ua_df.merge(
        eu_df,
        left_on="partner_iso2",
        right_on="reporter_iso2",
        suffixes=("_ua", "_eu"),)

    for prefix, col_ua, col_eu in (
        ("ua_export", "export_usd_ua", "import_usd_eu"),
        ("ua_import", "import_usd_ua", "export_usd_eu"),):
        
        gap = (merged[col_ua] - merged[col_eu]).round(2)
        base = merged[[col_ua, col_eu]].max(axis=1).replace(0, pd.NA)
        gap_pct = (gap.abs() / base * 100).fillna(0.0).round(2)

        merged[f"{prefix}_gap_usd"] = gap
        merged[f"{prefix}_gap_pct"] = gap_pct
        merged[f"{prefix}_matches"] = gap_pct <= tolerance_pct

    merged["matches_all"] = merged["ua_export_matches"] & merged["ua_import_matches"]
    logger.info(f"Zestawiono {len(merged)} krajów, zgodnych w obie strony: {int(merged['matches_all'].sum())}")
    return merged
