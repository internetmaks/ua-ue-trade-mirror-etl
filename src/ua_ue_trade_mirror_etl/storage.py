from pathlib import Path
import pandas as pd
from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.logger import logger


def df_to_csv(
    df: pd.DataFrame,
    filename: str,
    output_dir: Path | str = settings.output_dir,
)-> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True,exist_ok=True)
    target_path = target_dir / filename

    if df.empty:
        logger.warning(f"dataframe pusty:{target_path}")

    df.to_csv(target_path, index=False, encoding="utf-8")
    logger.success(f"zapisano df do {target_path}")
    return target_path

def save_anomalies(
    reconciled_df: pd.DataFrame,
    filename: str = "anomalies.csv",
    output_dir: Path | str = settings.output_dir,
) -> Path | None:
    
    if reconciled_df.empty or "matches_all" not in reconciled_df.columns:
        logger.info("Brak danych do zapisu anomalii")
        return None
    anomalies = reconciled_df[~reconciled_df["matches_all"]]
    if anomalies.empty:
        logger.info("Brak anomalii ")
        return None
    
    return df_to_csv(anomalies, filename=filename, output_dir=output_dir)