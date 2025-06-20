"""Event-driven backtester with transaction costs and slippage."""

from __future__ import annotations

import logging
from typing import Callable, Dict, Optional

import numpy as np
import pandas as pd

try:
    import polars as pl
except Exception:  # pragma: no cover - optional dep
    pl = None


class EventBacktester:
    """Simulates rebalancing over time with costs and slippage."""

    def __init__(
        self,
        initial_capital: float = 100_000,
        commission_bps: float = 10.0,
        slippage_bps: float = 5.0,
    ) -> None:
        self.initial_capital = initial_capital
        self.commission = commission_bps / 10000
        self.slippage = slippage_bps / 10000
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(
        self,
        prices: "pl.DataFrame",
        weight_func: Callable[[pd.DataFrame], Dict[str, float]],
        frequency: str = "W-FRI",
    ) -> Optional[Dict[str, pd.Series]]:
        """Backtest by calling ``weight_func`` at each rebalance date.

        Parameters
        ----------
        prices : pl.DataFrame
            Price data with ``date`` column.
        weight_func : callable
            Function that accepts a pandas price frame up to the rebalance
            date and returns a dict of target weights by ticker.
        frequency : str
            Pandas offset string for rebalancing.
        """
        if pl is None:
            self.logger.error("polars is required for backtesting")
            return None

        tickers = [c for c in prices.columns if c != "date"]
        if not tickers:
            self.logger.error("no tickers provided")
            return None

        prices_pd = prices.to_pandas().set_index("date").sort_index()
        rebalance_dates = (
            pd.date_range(prices_pd.index.min(), prices_pd.index.max(), freq=frequency)
            .intersection(prices_pd.index)
        )
        if len(rebalance_dates) == 0:
            self.logger.error("no rebalance dates found")
            return None

        current_weights = {t: 0.0 for t in tickers}
        cash = self.initial_capital
        equity_curve = []
        positions = {t: 0.0 for t in tickers}
        last_date = prices_pd.index[0]

        for d in rebalance_dates:
            price_slice = prices_pd.loc[:d]
            if len(price_slice) < 2:
                continue
            # apply daily returns since last_date
            period_prices = price_slice.loc[last_date:d]
            returns = period_prices.pct_change().fillna(0)
            for date, row in returns.iloc[1:].iterrows():
                cash += cash * 0  # cash earns no interest
                for t in tickers:
                    positions[t] *= 1 + row[t]
                value = cash + sum(positions[t] * period_prices.loc[date, t] for t in tickers)
                equity_curve.append((date, value))
            last_date = d

            target_weights = weight_func(price_slice)
            if not target_weights:
                continue
            # normalise
            tw = np.array([target_weights.get(t, 0.0) for t in tickers])
            tw = tw / (np.abs(tw).sum() + 1e-12)
            current_price = prices_pd.loc[d]
            portfolio_value = cash + sum(positions[t] * current_price[t] for t in tickers)
            target_value = portfolio_value * tw
            trades_value = target_value - np.array([positions[t] * current_price[t] for t in tickers])

            # apply trades with slippage and commission
            for i, t in enumerate(tickers):
                trade_val = trades_value[i]
                if abs(trade_val) < 1e-8:
                    continue
                direction = np.sign(trade_val)
                price = current_price[t] * (1 + self.slippage * direction)
                units = trade_val / price
                cost = abs(units * price) * self.commission
                cash -= units * price + cost
                positions[t] += units

        # final valuation
        final_prices = prices_pd.iloc[-1]
        final_value = cash + sum(positions[t] * final_prices[t] for t in tickers)
        equity_curve.append((prices_pd.index[-1], final_value))
        curve = pd.Series(dict(equity_curve)).sort_index()
        returns = curve.pct_change().fillna(0)
        self.logger.info("event backtest completed")
        return {"equity_curve": curve, "returns": returns}

