from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/kpis")
def get_kpis():
    return {
        "cagr": 28.5,
        "sharpe": 1.82,
        "max_drawdown": -12.3,
        "position_count": 5,
    }

@app.get("/api/equity-curve")
def get_equity_curve():
    dates = pd.to_datetime(pd.date_range("2023-01-01", periods=100, freq="D"))
    portfolio_value = 100000 * (1 + np.random.randn(100).cumsum() * 0.005).cumprod()
    benchmark_value = 100000 * (1 + np.random.randn(100).cumsum() * 0.003).cumprod()
    data = []
    for i in range(100):
        data.append({
            "date": dates[i].strftime('%Y-%m-%d'),
            "portfolio": portfolio_value[i],
            "benchmark": benchmark_value[i],
        })
    return data
