"""Top-level package for the quant system."""

"""Convenience imports for the quant system subpackages."""

from .data.fetcher import DataFetcher, VerdaAPI
from .data.alternative import AlternativeDataEngine
from .data.bist import BISTDataHandler

from .features.engineer import FeatureEngineer

from .models.alpha import AlphaModelBuilder

from .risk.budgeting import RiskBudgeting
from .risk.performance import BISTPerformanceAnalyzer
from .risk.scenario import ScenarioAnalyzer
from .risk.optimizer import TurkishMarketOptimizer

from .backtesting.vectorized import Backtester
from .backtesting.event import EventBacktester

from .trading.live import LiveTradingSystem, BrokerInterface

__all__ = [
    "DataFetcher",
    "VerdaAPI",
    "AlternativeDataEngine",
    "BISTDataHandler",
    "FeatureEngineer",
    "AlphaModelBuilder",
    "RiskBudgeting",
    "Backtester",
    "EventBacktester",
    "LiveTradingSystem",
    "BrokerInterface",
    "TurkishMarketOptimizer",
    "ScenarioAnalyzer",
    "BISTPerformanceAnalyzer",
]
