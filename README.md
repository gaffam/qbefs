# Quant System Skeleton


## Modules

The codebase is organised into themed subpackages to keep related
functionality together.

- **data.fetcher** – Download market data via APIs such as `yfinance`.
- **data.bist** – Helper utilities for Borsa İstanbul specific logic.
- **data.alternative** – Collect alternative data like KAP headlines.
- **features.engineer** – Generate technical indicators from price data.
- **models.alpha** – Train predictive models for alpha generation.
- **backtesting.vectorized** – Run a vectorised backtest over price series.
- **backtesting.event** – Event‑driven backtester with commissions and slippage.
- **trading.live** – Skeleton pieces for integrating with a broker.
- **risk.budgeting** – Portfolio optimisation routines.
- **risk.performance** – Calculate performance metrics.
- **risk.scenario** – Simple stress‑testing utilities.
- **risk.optimizer** – Turkish market specific helpers.
- **main** – Example entry point demonstrating how the modules fit together.
- **main** – Example entry point demonstrating how the modules fit together.

This code is intentionally lightweight and does not aim to provide a complete
trading system.  It serves as a starting point for experimentation and further
expansion.

## Setup

Install the core dependencies and optionally any extras.  Python 3.10 or
newer is recommended.

```bash
pip install -r requirements.txt
```

Some modules rely on additional libraries such as ``TA-Lib`` or ``tensorflow``.
These can be installed separately if required.

Set your API keys using environment variables before running the examples:

```bash
export VERDA_API_KEY=<your_key>
export NEWS_API_KEY=<newsapi_key>
export FRED_API_KEY=<fred_key>
```

## Running the example pipeline

Execute the main entry point which ties together data fetching, feature
engineering, model training and backtesting:

```bash
python -m quant_system.main
```

## Starting the React dashboard

The ``icerberg-dashboard`` folder contains a Vite based React application that
visualises the equity curve and KPIs.  Install dependencies and run the dev
server:

```bash
cd icerberg-dashboard
npm install
npm run dev
```

## Package layout

All Python modules live inside the `quant_system` package.  Each major
component of the pipeline is implemented in its own file so that the system can
grow organically.  The table below summarises the relationship between file
names and their responsibility.

| File | Purpose |
| --- | --- |
| `data/fetcher.py` | Retrieve price and auxiliary data |
| `data/bist.py` | BIST specific helpers |
| `data/alternative.py` | Alternative data collection |
| `features/engineer.py` | Generate technical indicators |
| `models/alpha.py` | Train predictive models |
| `backtesting/vectorized.py` | Run a simple vectorised backtest |
| `backtesting/event.py` | Step through time with slippage and commissions |
| `trading/live.py` | Skeleton for connecting to a broker |
| `risk/budgeting.py` | Optimise portfolio weights |
| `risk/performance.py` | Calculate performance metrics |
