# UA–UE Trade Mirror ETL

Potok ETL porównujący statystyki handlu zagranicznego publikowane przez **Służbę Celną Ukrainy** z danymi lustrzanymi z **Eurostat Comext** (na przykładzie pszenicy `HS 1001`).

## Co robi projekt
1. **Extract:**
   - [ukraine_customs.py](src/ua_ue_trade_mirror_etl/extractors/ukraine_customs.py) — scraper **Playwright** (wzorzec Page Object Model) pobierający eksport `.xlsx` z portalu `bi.customs.gov.ua`.
   - [eurostat_comext.py](src/ua_ue_trade_mirror_etl/extractors/eurostat_comext.py) — klient **httpx** pobierający dane miesięczne SDMX-CSV z API Eurostat Comext (`FLOW 1+2`) i przeliczający EUR → USD po średnim rocznym kursie z **API NBP**.
2. **Transform & Validate:**
   - [cleaner.py](src/ua_ue_trade_mirror_etl/transform/cleaner.py) + [models.py](src/ua_ue_trade_mirror_etl/models.py) — czyszczenie `.xlsx` (`pandas` + `openpyxl`) oraz walidacja spójności matematycznej (`Total ≈ Export + Import`, `Balance ≈ Export - Import`) w **Pydantic**.
   - [reconciler.py](src/ua_ue_trade_mirror_etl/transform/reconciler.py) — dwukierunkowe zestawienie `UA Export ↔ EU Import` oraz `UA Import ↔ EU Export` i flagowanie rozbieżności przekraczających próg (`15%`).
3. **Load & Visualize:**
   - [storage.py](src/ua_ue_trade_mirror_etl/storage.py) — zapis `ua_customs_clean.csv`, `trade_mirror.csv` i `anomalies.csv` w `data/output/`.
   - [generate_chart.py](scripts/generate_chart.py) — generowanie wykresów porównawczych w **matplotlib** (`trade_mirror_chart.png`, `trade_mirror_import_chart.png`).

## Przykładowe wnioski z danych (`HS 1001`, 2024)
- **Hiszpania (`ES`: `980M` vs `1109M`, gap `11.6%`)** i **Niemcy (`DE`: `21.5M` vs `23.3M`, gap `7.6%`)** dobrze zgadzają się w lustrze (różnica wynika głównie z wyceny **FOB vs CIF** — frachtu i ubezpieczenia).
- **Polska (`PL`: `0.36M`), Węgry (`HU`: `0M`), Słowacja (`SK`: `0M`)** — śladowy lub zerowy import pszenicy z UA odzwierciedla obowiązujące krajowe embargo (tranzyt nie wlicza się do importu).
- **Holandia (`NL`)** — wyższy import w Eurostacie pokazuje klasyczny **efekt portu w Rotterdamie** (odprawa celna przy wejściu do UE dla towarów jadących dalej).

## Struktura projektu
```text
├── src/ua_ue_trade_mirror_etl/
│   ├── config.py                  # Ustawienia (.env + wartości domyślne)
│   ├── logger.py                  # Logowanie (loguru: konsola + logs/pytest.log)
│   ├── models.py                  # Schematy Pydantic
│   ├── extractors/                # Playwright (UA Customs) + httpx (Eurostat / NBP)
│   ├── transform/                 # Cleaner (.xlsx) + Reconciler (Mirror Gap)
│   ├── storage.py                 # Zapis CSV i anomalii
│   └── pipeline.py                # Orkiestracja całego ETL
├── scripts/generate_chart.py      # Wykresy PNG (matplotlib)
├── tests/                         # Testy jednostkowe offline (pytest + mocki + fixture .xlsx)
├── pytest.ini
└── requirements.txt
```

## Uruchomienie

```bash
# 1. Środowisko i zależności
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Testy jednostkowe offline (13 testów)
pytest

# 3. Pełny pipeline ETL (+ wygenerowanie wykresów)
PYTHONPATH=src python -m ua_ue_trade_mirror_etl.pipeline
```

Konfigurację (`TARGET_YEAR`, `TARGET_HS_CHAPTER`, `EU_COUNTRIES`, `HEADLESS`) można nadpisać w pliku `.env` (zobacz [config.py](src/ua_ue_trade_mirror_etl/config.py)).
