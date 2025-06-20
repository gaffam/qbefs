"""Utilities specific to BIST market."""

import logging
from typing import List, Dict

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None


class BISTDataHandler:
    """Handles BIST specific data operations."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # load static list of BIST100 tickers.  This is intentionally short and
        # can be extended easily.
        self.bist100_constituents = self._load_constituents()

    def _load_constituents(self) -> List[str]:
        """Return a hard coded list of BIST100 constituents."""
        self.logger.debug("Loading BIST100 constituents")
        return [
            "AKBNK.IS",
            "ARCLK.IS",
            "ASELS.IS",
            "GARAN.IS",
            "THYAO.IS",
            "EREGL.IS",
            "TUPRS.IS",
            "SAHOL.IS",
            "KCHOL.IS",
        ]

    def adjust_for_bist_specifics(self, df: "pl.DataFrame") -> "pl.DataFrame":
        """Add simple BIST specific columns."""
        self.logger.debug("Adjusting dataframe for BIST specifics")
        if pl is None or "ticker" not in df.columns:
            return df
        return df.with_columns(
            pl.col("ticker").is_in(self.bist100_constituents).alias("is_bist100")
        )
