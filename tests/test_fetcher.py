import polars as pl
from quant_system.data.fetcher import DataFetcher
from unittest.mock import patch, MagicMock


def test_fetch_github_data_csv():
    csv_bytes = b"a,b\n1,2\n3,4\n"
    mock_resp = MagicMock()
    mock_resp.content = csv_bytes
    mock_resp.raise_for_status = lambda: None
    with patch("requests.get", return_value=mock_resp):
        fetcher = DataFetcher({})
        df = fetcher.fetch_github_data("https://example.com/file.csv")
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (2, 2)
