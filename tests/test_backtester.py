import polars as pl
from quant_system.backtesting.vectorized import Backtester


def test_backtester_runs():
    prices = pl.DataFrame({
        "date": [1, 2, 3],
        "AAA": [10.0, 10.5, 11.0],
        "BBB": [20.0, 20.5, 20.0],
    })
    signals = pl.DataFrame({
        "date": [1, 2, 3],
        "AAA": [0.5, 0.5, 0.5],
        "BBB": [0.5, 0.5, 0.5],
    })
    bt = Backtester()
    res = bt.run_backtest(prices, signals)
    assert res is not None
    assert "equity_curve" in res
