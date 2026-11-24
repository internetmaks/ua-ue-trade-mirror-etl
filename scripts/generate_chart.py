from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ua_ue_trade_mirror_etl.config import settings
from ua_ue_trade_mirror_etl.logger import logger


def generate_trade_mirror_chart(
    csv_path: Path | str = settings.output_dir / "trade_mirror.csv",
    chart_path: Path | str = settings.output_dir / "trade_mirror_chart.png",
) -> Path | None:
    """Generate UA vs EU trade mirror bar charts in mln USD with values and match status."""
    src = Path(csv_path)
    if not src.exists():
        logger.warning(f"Brak pliku CSV do wykresu: {src}")
        return None

    df = pd.read_csv(src)
    if df.empty:
        return None

    export_out = Path(chart_path)
    export_out.parent.mkdir(parents=True, exist_ok=True)
    charts = [
        (export_out, "export_usd_ua", "import_usd_eu", "ua_export_gap_pct", "ua_export_matches", "UA Export", "EU Import", "Eksport UA vs Import UE"),
        (export_out.with_name("trade_mirror_import_chart.png"), "import_usd_ua", "export_usd_eu", "ua_import_gap_pct", "ua_import_matches", "UA Import", "EU Export", "Import UA vs Eksport UE"),
    ]

    for out_path, col_ua, col_eu, gap_col, match_col, label_ua, label_eu, title in charts:
        sub = df.sort_values(col_ua).reset_index(drop=True)
        plot_df = (sub[[col_ua, col_eu]] / 1e6).rename(columns={col_ua: label_ua, col_eu: label_eu})
        plot_df.index = [
            f"{r['partner_iso2']} ({r[gap_col]:.1f}%)" for _, r in sub.iterrows()
        ]

        ax = plot_df.plot.barh(figsize=(10, 5), title=title, xlabel="mln USD", color=["#2563eb", "#f97316"])
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2fM", padding=3, fontsize=8)
        for tick, is_ok in zip(ax.get_yticklabels(), sub[match_col]):
            tick.set_color("#15803d" if is_ok else "#b91c1c")
            tick.set_fontweight("bold")

        ax.set_xlim(right=max(float(plot_df.to_numpy().max()), 0.1) * 1.18)
        ax.grid(axis="x", alpha=0.3)
        ax.figure.tight_layout()
        ax.figure.savefig(out_path, dpi=150)
        plt.close(ax.figure)
        logger.success(f"Wygenerowano wykres: {out_path}")

    return export_out


if __name__ == "__main__":
    generate_trade_mirror_chart()
