"""Skeleton classes for running a live trading loop."""

from __future__ import annotations

import logging
from typing import List, Any, Dict

import yfinance as yf


class BrokerInterface:
    """Minimal interface used by :class:`LiveTradingSystem`."""

    def __init__(self, cash: float = 100000.0) -> None:
        self.cash = cash
        self.positions: Dict[str, float] = {}

    def get_positions(self) -> Dict[str, float]:
        """Return current positions."""
        return self.positions

    def get_cash(self) -> float:
        """Return available cash."""
        return self.cash

    def place_order(self, symbol: str, qty: float) -> None:
        """Submit an order.  Very naive market order implementation."""
        self.positions[symbol] = self.positions.get(symbol, 0.0) + qty


class LiveTradingSystem:
    """Illustrative live trading system."""

    def __init__(self, symbols: List[str], model: Any, broker: BrokerInterface):
        self.symbols = symbols
        self.model = model
        self.broker = broker
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self) -> None:
        """Run one iteration of the trading loop."""
        self.logger.info("live trading start")
        positions = self.broker.get_positions()
        cash = self.broker.get_cash()
        self.logger.debug("positions=%s cash=%.2f", positions, cash)

        latest = {}
        for sym in self.symbols:
            try:
                data = yf.download(sym, period="1d", progress=False)
                if not data.empty:
                    latest[sym] = float(data["Close"].iloc[-1])
            except Exception as exc:  # pragma: no cover - network dependent
                self.logger.error("price fetch failed for %s: %s", sym, exc)

        if not latest:
            self.logger.error("no prices retrieved; aborting iteration")
            return

        preds = []
        for sym in self.symbols:
            price = latest.get(sym)
            if price is None:
                preds.append(0.0)
                continue
            try:
                pred = float(self.model.predict([[price]])[0])
            except Exception as exc:  # pragma: no cover
                self.logger.error("model prediction failed: %s", exc)
                pred = 0.0
            preds.append(pred)

        for sym, pred in zip(self.symbols, preds):
            if pred > 0:
                self.logger.info("buy signal for %s", sym)
                self.broker.place_order(sym, 1)

        self.logger.info("live trading iteration complete")

