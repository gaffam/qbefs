from quant_system.risk.scenario import ScenarioAnalyzer


def test_scenario_analyzer():
    sc = ScenarioAnalyzer()
    res = sc.stress_test_portfolio({"A": 0.5, "B": 0.5}, "crash")
    assert res["scenario"] == "crash"
    assert res["expected_return"] < 0
