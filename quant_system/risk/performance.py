"""Performance analysis utilities."""

import logging
from typing import Dict

import numpy as np
import pandas as pd


class BISTPerformanceAnalyzer:
    """Calculates basic performance statistics from returns."""

    def __init__(self, returns: pd.Series, risk_free_rate: float = 0.0):
        self.logger = logging.getLogger(self.__class__.__name__)
        if not isinstance(returns, pd.Series):
            raise TypeError("returns must be a pandas Series")
        self.returns = returns.fillna(0.0)
        self.risk_free_rate = risk_free_rate

    def calculate_all_metrics(self) -> Dict:
        """Return Sharpe, Sortino, max drawdown and CAGR."""
        r = self.returns
        rf_daily = self.risk_free_rate / 252
        excess = r - rf_daily

        mean_excess = excess.mean()
        std = r.std()
        sharpe = (mean_excess / std) * np.sqrt(252) if std > 0 else np.nan

        downside_std = r[r < 0].std()
        sortino = (mean_excess / downside_std) * np.sqrt(252) if downside_std > 0 else np.nan

        equity = (1 + r).cumprod()
        running_max = equity.cummax()
        drawdowns = equity / running_max - 1
        max_drawdown = drawdowns.min()

        total_return = equity.iloc[-1]
        years = len(r) / 252
        cagr = total_return ** (1 / years) - 1 if years > 0 else np.nan

        self.logger.info(
            "Performance - Sharpe: %.2f Sortino: %.2f MDD: %.2f%% CAGR: %.2f%%",
            sharpe,
            sortino,
            max_drawdown * 100,
            cagr * 100,
        )

        return {
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": max_drawdown,
            "cagr": cagr,
        }
