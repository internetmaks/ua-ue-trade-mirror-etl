# UA–EU Trade Mirror ETL

An object-oriented ETL pipeline in Python that collects official foreign trade statistics from the **State Customs Service of Ukraine** and reconciles them against mirror import/export data from **Eurostat Comext** (demonstrated on wheat trade, `HS 1001`).

## Key Capabilities & Architecture

1. **Extract (Automated Web Scraping & API Ingestion):**
   - [`ukraine_customs.py`](src/ua_ue_trade_mirror_etl/extractors/ukraine_customs.py) — **Playwright** scraper built using the **Page Object Model (POM)** pattern to navigate `bi.customs.gov.ua`, apply dynamic filters, and download raw `.xlsx` trade reports with explicit timeout and error handling.
   - [`eurostat_comext.py`](src/ua_ue_trade_mirror_etl/extractors/eurostat_comext.py) — **httpx** client fetching monthly SDMX-CSV series from the Eurostat Comext API (`FLOW 1+2`) and converting EUR values to USD using current rate from **NBP API**.

2. **Transform & Validate (Irregular File Parsing & Schema Enforcement):**
   - [`cleaner.py`](src/ua_ue_trade_mirror_etl/transform/cleaner.py) & [`models.py`](src/ua_ue_trade_mirror_etl/models.py) — parses irregular, multi-header `.xlsx` customs exports (`pandas` + `openpyxl`), normalizes country/commodity codes, and enforces strict type and mathematical consistency checks (`Total ≈ Export + Import`, `Balance ≈ Export - Import`) via **Pydantic**.
   - [`reconciler.py`](src/ua_ue_trade_mirror_etl/transform/reconciler.py) — performs bidirectional mirror reconciliation (`UA Export ↔ EU Import` and `UA Import ↔ EU Export`) and flags bilateral discrepancies exceeding a configurable threshold (`15%`).

3. **Load, Observability & Visualization:**
   - [`storage.py`](src/ua_ue_trade_mirror_etl/storage.py) — exports clean, analysis-ready datasets (`ua_customs_clean.csv`, `trade_mirror.csv`, `anomalies.csv`) to `data/output/`.
   - [`logger.py`](src/ua_ue_trade_mirror_etl/logger.py) — structured logging and log rotation via **loguru** for diagnosing network failures, DOM changes, and validation errors.
   - [`generate_chart.py`](scripts/generate_chart.py) — generates publication-ready comparison charts in **matplotlib** for qualitative and economic analysis.

## Analytical Findings (`HS 1001` — Wheat, 2024)

![UA-EU Wheat Trade Mirror Chart](docs/trade_mirror_chart.png)

- **Spain (`ES`: $980M UA reported vs. $1,109M EU reported, `11.6%` gap) & Germany (`DE`: $21.5M vs. $23.3M, `7.6%` gap):** High mirror consistency; the ~8–12% positive spread on the EU side reflects standard **FOB vs. CIF** valuation differences (freight and insurance costs included in EU import figures).
- **Poland (`PL`: $0.36M), Hungary (`HU`: $0M), Slovakia (`SK`: $0M):** Near-zero EU-reported imports reflect national import bans on Ukrainian grain (transit shipments under customs supervision are excluded from national import statistics).
- **Netherlands (`NL`):** Significantly higher EU-reported imports illustrate the classic **Rotterdam effect** (quasi-transit goods cleared through Dutch customs upon entering the EU single market before onward distribution).

## Project Structure

```text
├── src/ua_ue_trade_mirror_etl/
│   ├── config.py                  # Environment-based configuration (.env + defaults)
│   ├── logger.py                  # Structured logging & rotation (loguru)
│   ├── models.py                  # Pydantic data & validation schemas
│   ├── extractors/                # Playwright POM scraper (UA Customs) + httpx clients (Eurostat / NBP)
│   ├── transform/                 # Irregular .xlsx parser/cleaner + bidirectional mirror reconciler
│   ├── storage.py                 # CSV & anomaly report exporter
│   └── pipeline.py                # End-to-end ETL orchestration
├── scripts/generate_chart.py      # Comparison charts (matplotlib)
├── tests/                         # Offline unit tests (pytest + mocks + .xlsx fixtures)
├── pytest.ini
└── requirements.txt
