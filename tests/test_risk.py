import pandas as pd
import numpy as np
from quant_system.risk.budgeting import RiskBudgeting


def test_optimize_mvo():
    prices = pd.DataFrame({
        "A": [1, 1.1, 1.2, 1.3],
        "B": [2, 2.1, 2.2, 2.3],
    })
    scores = pd.Series({"A": 0.1, "B": 0.2})
    rb = RiskBudgeting()
    weights = rb.optimize_mvo(prices, scores)
    assert weights is not None
    assert abs(sum(weights.values()) - 1) < 1e-6
