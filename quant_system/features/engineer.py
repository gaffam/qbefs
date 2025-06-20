"""Feature engineering routines for market data."""

import logging
from typing import Optional

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None


class FeatureEngineer:
    """Generates technical and statistical features."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_all_features(self, df: "pl.DataFrame") -> "pl.DataFrame":
        """Generate a richer set of technical features.

        Besides simple returns and a moving average this method also
        calculates RSI, MACD and Bollinger Bands.  If a ``ticker`` column is
        present features are computed per ticker using ``over('ticker')``.
        The input frame must at least contain ``date`` and ``close``.
        """

        if pl is None:
            self.logger.error("polars is required for feature generation")
            return df

        if "close" not in df.columns:
            self.logger.error("input data must contain a 'close' column")
            return df

        group = "ticker" if "ticker" in df.columns else None

        df = df.sort([group, "date"] if group else "date")

        close = pl.col("close")

        # Basic return and moving average
        exprs = [
            (close / close.shift(1).over(group) - 1).alias("return"),
            close.rolling_mean(5).over(group).alias("sma_5"),
        ]

        # --- RSI ---
        delta = close.diff().over(group)
        gain = pl.when(delta > 0).then(delta).otherwise(0.0)
        loss = pl.when(delta < 0).then(-delta).otherwise(0.0)
        avg_gain = gain.ewm_mean(span=14, adjust=False).alias("avg_gain")
        avg_loss = loss.ewm_mean(span=14, adjust=False).alias("avg_loss")
        rsi = (100 - 100 / (1 + (pl.col("avg_gain") / pl.col("avg_loss")))).alias(
            "rsi"
        )

        # --- MACD ---
        ema_fast = close.ewm_mean(span=12, adjust=False).alias("ema_fast")
        ema_slow = close.ewm_mean(span=26, adjust=False).alias("ema_slow")
        macd = (pl.col("ema_fast") - pl.col("ema_slow")).alias("macd")
        macd_signal = pl.col("macd").ewm_mean(span=9, adjust=False).alias(
            "macd_signal"
        )
        macd_hist = (pl.col("macd") - pl.col("macd_signal")).alias("macd_hist")

        # --- Bollinger Bands ---
        ma = close.rolling_mean(20).over(group).alias("bb_middle")
        std = close.rolling_std(20).over(group).alias("bb_std")
        bb_upper = (pl.col("bb_middle") + 2 * pl.col("bb_std")).alias("bb_upper")
        bb_lower = (pl.col("bb_middle") - 2 * pl.col("bb_std")).alias("bb_lower")

        df = df.with_columns(exprs + [gain.alias("gain"), loss.alias("loss")])
        df = df.with_columns([avg_gain, avg_loss])
        df = df.with_columns([rsi])
        df = df.with_columns([ema_fast, ema_slow, macd, macd_signal, macd_hist])
        df = df.with_columns([ma, std, bb_upper, bb_lower])

        return df.drop([
            "gain",
            "loss",
            "avg_gain",
            "avg_loss",
            "ema_fast",
            "ema_slow",
            "bb_std",
        ])
