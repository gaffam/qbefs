"""Portfolio optimisation using model-based expected returns."""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd

try:
    from pypfopt import EfficientFrontier, risk_models, expected_returns
    from pypfopt.objective_functions import L2_reg
except Exception:  # pragma: no cover - optional dependency
    EfficientFrontier = None
    risk_models = None
    expected_returns = None
    L2_reg = None


class RiskBudgeting:
    """Mean-variance optimisation helper based on PyPortfolioOpt."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def optimize_mvo(
        self, prices: pd.DataFrame, alpha_scores: pd.Series
    ) -> Optional[Dict[str, float]]:
        """Return optimal portfolio weights using alpha scores as expected returns.

        Parameters
        ----------
        prices : pandas.DataFrame
            Historical price data indexed by date.
        alpha_scores : pandas.Series
            Series of model predictions keyed by ticker.
        """
        if EfficientFrontier is None:
            self.logger.error("pypfopt is required for optimization")
            return None

        try:
            self.logger.info("Starting MVO portfolio optimization")
            prices = prices.dropna(how="all")
            cov = risk_models.sample_cov(prices, frequency=252)
            mu = alpha_scores.reindex(prices.columns).fillna(0.0)
            ef = EfficientFrontier(mu, cov, weight_bounds=(0, 1))
            ef.add_objective(L2_reg, gamma=0.5)
            ef.max_sharpe()
            weights = ef.clean_weights()
            self.logger.info("MVO optimization complete")
            return weights
        except Exception as exc:  # pragma: no cover - optimization can fail
            self.logger.error("Optimization failed: %s", exc)
            return None
