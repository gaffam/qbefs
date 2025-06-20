"""Data fetching utilities including Kaggle, GitHub and Verda APIs."""

import logging
import os
import zipfile
from io import BytesIO
from typing import Dict, List, Optional

import requests

try:
    import polars as pl
except ImportError:  # pragma: no cover - optional dependency
    pl = None


class DataFetcher:
    """Fetches data from various sources."""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        # initialization of APIs can be added here

    def fetch_yfinance(self, tickers: List[str], start_date: str, end_date: str) -> Optional["pl.DataFrame"]:
        """Fetch historical prices using ``yfinance``.

        Parameters
        ----------
        tickers: list of ticker symbols
        start_date: ISO formatted date string
        end_date: ISO formatted date string

        Returns
        -------
        ``pl.DataFrame`` with columns ``date`` and tickers or ``None`` on failure.
        """
        try:
            import yfinance as yf
        except Exception:  # pragma: no cover - optional dependency
            self.logger.error("yfinance is not available")
            return None

        self.logger.info("Downloading data via yfinance")
        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.error("yfinance download failed: %s", exc)
            return None

        if data.empty:
            self.logger.error("No data returned from yfinance")
            return None

        if "Adj Close" in data:
            prices = data["Adj Close"].reset_index()
        else:
            prices = data["Close"].reset_index()

        if pl is None:
            self.logger.error("polars is required for returned data")
            return None

        return pl.from_pandas(prices).rename({"Date": "date"})

    def download_kaggle_dataset(self, dataset: str, path: str = "./data", unzip: bool = True) -> bool:
        """Download a dataset from Kaggle using :mod:`kaggle` API.

        The function authenticates with Kaggle using the user's credentials
        (typically from ``~/.kaggle/kaggle.json``) and downloads the requested
        dataset to ``path``.  When ``unzip`` is ``True`` the archive is
        extracted and the original zip file removed.
        """
        try:
            from kaggle import KaggleApi  # type: ignore
        except Exception:  # pragma: no cover - optional dependency
            self.logger.error("kaggle package is required for this method")
            return False

        api = KaggleApi()
        try:
            api.authenticate()
        except Exception as exc:  # pragma: no cover - requires valid creds
            self.logger.error("Kaggle authentication failed: %s", exc)
            return False

        os.makedirs(path, exist_ok=True)
        self.logger.info("Downloading %s to %s", dataset, path)
        try:
            api.dataset_download_files(dataset, path=path, quiet=True)
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.error("Kaggle download failed: %s", exc)
            return False

        zip_name = os.path.join(path, dataset.split("/")[-1] + ".zip")
        if unzip and os.path.exists(zip_name):
            try:
                with zipfile.ZipFile(zip_name, "r") as zf:
                    zf.extractall(path)
                os.remove(zip_name)
            except Exception as exc:  # pragma: no cover
                self.logger.error("Failed to unzip dataset: %s", exc)
        return True

    def fetch_github_data(self, url: str, auth_token: Optional[str] = None) -> Optional["pl.DataFrame"]:
        """Fetch a raw data file from GitHub.

        The file type is inferred from the extension and must be CSV, Parquet
        or JSON.  ``None`` is returned on failure.
        """

        headers = {"Accept": "application/vnd.github.v3.raw"}
        if auth_token:
            headers["Authorization"] = f"token {auth_token}"

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.error("GitHub request failed: %s", exc)
            return None

        if pl is None:
            self.logger.error("polars is required for returned data")
            return None

        content = BytesIO(resp.content)
        try:
            if url.endswith(".csv"):
                df = pl.read_csv(content)
            elif url.endswith(".parquet"):
                df = pl.read_parquet(content)
            elif url.endswith(".json"):
                df = pl.read_json(content)
            else:
                self.logger.error("Unknown file extension for %s", url)
                return None
        except Exception as exc:  # pragma: no cover
            self.logger.error("Failed to parse GitHub data: %s", exc)
            return None

        return df


class VerdaAPI:
    """Simplified client for interacting with a hypothetical Verda API."""

    BASE_URL = "https://api.verda.com.tr/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_eod_data(self, tickers: List[str], start_date: str, end_date: str) -> Optional["pl.DataFrame"]:
        """Fetch end-of-day data using ``yfinance``.

        Parameters
        ----------
        tickers: list of ticker symbols
        start_date: ISO date string
        end_date: ISO date string

        Returns
        -------
        ``pl.DataFrame`` containing OHLCV fields for each ticker.  ``None`` is
        returned on failure.
        """
        try:
            import yfinance as yf
        except Exception:  # pragma: no cover - optional dependency
            self.logger.error("yfinance is not available")
            return None

        if pl is None:
            self.logger.error("polars is required for returned data")
            return None

        frames = []
        for ticker in tickers:
            try:
                data = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    auto_adjust=False,
                    progress=False,
                )
            except Exception as exc:  # pragma: no cover - network dependent
                self.logger.error("download failed for %s: %s", ticker, exc)
                continue

            if data.empty:
                self.logger.warning("no data for %s", ticker)
                continue

            df = data.reset_index().rename(
                columns={
                    "Date": "date",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Adj Close": "adj_close",
                    "Volume": "volume",
                }
            )
            df["ticker"] = ticker
            frames.append(pl.from_pandas(df))

        if not frames:
            self.logger.error("no EOD data returned")
            return None

        return pl.concat(frames)
