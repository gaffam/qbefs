"""Helpers for Turkish market specific calculations."""

import logging
from typing import Dict


class TurkishMarketOptimizer:
    """Applies BIST specific adjustments."""

    @staticmethod
    def get_free_data_sources() -> Dict[str, str]:
        return {
            "KAP": "https://www.kap.org.tr/tr/",
            "BIST": "https://www.borsaistanbul.com/tr/",
        }
