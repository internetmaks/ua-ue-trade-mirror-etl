from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx
import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from ua_ue_trade_mirror_etl.extractors.eurostat_comext import EurostatComextClient
from ua_ue_trade_mirror_etl.extractors.ukraine_customs import UA_customs_Page


def test_ua_customs_open_reraises_timeout_error() -> None:
    mock_page = MagicMock()
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout 20000ms exceeded")

    customs = UA_customs_Page(mock_page)
    with pytest.raises(PlaywrightTimeoutError, match="Timeout 20000ms exceeded"):
        customs.open()


def test_ua_customs_download_saves_to_target_dir(tmp_path: Path) -> None:
    mock_page = MagicMock()
    mock_download = MagicMock()
    mock_download.suggested_filename = "report.xlsx"

    mock_page.expect_download.return_value.__enter__.return_value.value = mock_download

    customs = UA_customs_Page(mock_page)
    with patch("ua_ue_trade_mirror_etl.extractors.ukraine_customs.expect"):
        saved_path = customs.download(folder=tmp_path)

    assert saved_path == tmp_path / "report.xlsx"
    mock_download.save_as.assert_called_once_with(tmp_path / "report.xlsx")


def test_eurostat_fetch_trade_splits_flows_and_converts_currency() -> None:
    csv_body = "FLOW,OBS_VALUE\n1,100.0\n1,50.0\n2,200.0\n"
    mock_comext_resp = MagicMock()
    mock_comext_resp.text = csv_body

    mock_eur_resp = MagicMock()
    mock_eur_resp.json.return_value = {"rates": [{"mid": 4.4}]}
    mock_usd_resp = MagicMock()
    mock_usd_resp.json.return_value = {"rates": [{"mid": 4.0}]}

    mock_http_client = MagicMock()
    mock_http_client.get.side_effect = [mock_comext_resp, mock_eur_resp, mock_usd_resp]

    with patch("ua_ue_trade_mirror_etl.extractors.eurostat_comext.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http_client
        client = EurostatComextClient()
        record = client.fetch_trade_with_ukraine("pl", hs_chapter="1001", year=2025)

    assert record.reporter_iso2 == "PL"
    assert record.import_usd == pytest.approx(165.0)  # 150 EUR * 1.10
    assert record.export_usd == pytest.approx(220.0)  # 200 EUR * 1.10


def test_eurostat_fetch_trade_reraises_http_500() -> None:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(500, request=request)

    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server error 500", request=request, response=response
    )

    mock_http_client = MagicMock()
    mock_http_client.get.return_value = mock_resp

    with patch("ua_ue_trade_mirror_etl.extractors.eurostat_comext.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value = mock_http_client
        client = EurostatComextClient()
        with pytest.raises(httpx.HTTPStatusError):
            client.fetch_trade_with_ukraine("PL")
