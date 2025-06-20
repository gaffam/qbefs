"""Backtesting engine."""

import logging
from typing import Dict, Optional

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None


class Backtester:
    """Runs a simple backtest."""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.logger = logging.getLogger(self.__class__.__name__)

    def run_backtest(self, prices: "pl.DataFrame", signals: "pl.DataFrame") -> Optional[Dict]:
        """Run a very small vectorized backtest.

        Parameters
        ----------
        prices : ``pl.DataFrame``
            Price data with a ``date`` column and ticker columns.
        signals : ``pl.DataFrame``
            Target weights for each ticker aligned by date.
        """

        if pl is None:
            self.logger.error("polars is required for backtesting")
            return None

        tickers = [c for c in prices.columns if c != "date"]
        if not tickers:
            self.logger.error("no tickers supplied")
            return None

        prices_pd = prices.to_pandas().set_index("date")
        signals_pd = signals.to_pandas().set_index("date")
        common = prices_pd.index.intersection(signals_pd.index)
        prices_pd = prices_pd.loc[common]
        signals_pd = signals_pd.loc[common].shift().fillna(0)

        returns = prices_pd.pct_change().fillna(0)
        portfolio_returns = (returns * signals_pd).sum(axis=1)
        equity_curve = (1 + portfolio_returns).cumprod() * self.initial_capital

        self.logger.info("backtest finished")
        return {
            "equity_curve": equity_curve,
            "returns": portfolio_returns,
        }
