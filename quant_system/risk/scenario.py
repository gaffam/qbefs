"""Stress testing utilities."""

import logging
from typing import Dict


class ScenarioAnalyzer:
    """Runs basic scenario based stress tests."""

    SCENARIOS = {
        "crash": -0.30,
        "rally": 0.20,
        "mild_bear": -0.10,
        "mild_bull": 0.10,
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def stress_test_portfolio(self, weights: Dict[str, float], scenario_name: str) -> Dict:
        """Estimate portfolio return under a pre-defined market shock."""
        shock = self.SCENARIOS.get(scenario_name)
        if shock is None:
            self.logger.error("unknown scenario %s", scenario_name)
            return {}

        expected_return = sum(w * shock for w in weights.values())
        self.logger.info(
            "Scenario %s implies portfolio return of %.2f%%",
            scenario_name,
            expected_return * 100,
        )
        return {"scenario": scenario_name, "expected_return": expected_return}
