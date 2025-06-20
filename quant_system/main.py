"""Entry point for running the quant system."""

import logging

import polars as pl

from .data.fetcher import DataFetcher, VerdaAPI
from .data.bist import BISTDataHandler
from .data.alternative import AlternativeDataEngine

from .features.engineer import FeatureEngineer

from .models.alpha import AlphaModelBuilder

from .backtesting.vectorized import Backtester

from .risk.budgeting import RiskBudgeting


logger = logging.getLogger("quant_system")


def main() -> None:
    """Minimal execution example using the various modules."""

    config = {
        "start": "2020-01-01",
        "end": "2020-06-01",
        "verda_api_key": "",
    }

    handler = BISTDataHandler()
    tickers = handler.bist100_constituents[:2]
    config["tickers"] = tickers + ["XU100.IS"]
    benchmark = "XU100.IS"

    logger.info("Quant system started")
    fetcher = DataFetcher(config)
    fe = FeatureEngineer()
    alpha = AlphaModelBuilder()
    backtester = Backtester()
    alt_data = AlternativeDataEngine(config)

    verda = VerdaAPI(config.get("verda_api_key", ""))
    prices_raw = verda.get_eod_data(config["tickers"], config["start"], config["end"])
    if prices_raw is None:
        logger.error("Unable to fetch prices; aborting")
        return

    prices = prices_raw.pivot(index="date", columns="ticker", values="close").sort("date")
    prices_no_bench = prices.select(["date"] + tickers)

    # compute 5-day forward relative performance vs benchmark
    benchmark_close = prices_raw.filter(pl.col("ticker") == benchmark).select(["date", "close"]).rename({"close": "bm_close"})
    data_no_bench = prices_raw.filter(pl.col("ticker") != benchmark).join(benchmark_close, on="date")
    data_no_bench = data_no_bench.sort(["ticker", "date"])
    data_no_bench = data_no_bench.with_columns([
        pl.col("close").shift(-5).over("ticker").alias("fwd_close"),
        pl.col("bm_close").shift(-5).alias("bm_fwd_close"),
    ])
    data_no_bench = data_no_bench.with_columns([
        ((pl.col("fwd_close") / pl.col("close")) - 1).alias("fwd_ret"),
        ((pl.col("bm_fwd_close") / pl.col("bm_close")) - 1).alias("bm_fwd_ret"),
    ])
    data_no_bench = data_no_bench.with_columns(
        (pl.col("fwd_ret") > pl.col("bm_fwd_ret")).cast(pl.Int8).alias("target")
    )

    # --- Fetch and process KAP headlines ---
    kap_df = alt_data.fetch_kap_headlines(tickers)
    kap_scores = None
    if kap_df is not None:
        kap_df = kap_df.with_columns(
            pl.col("headline")
            .apply(alt_data.analyze_sentiment_simple)
            .alias("sentiment_score")
        )
        kap_scores = kap_df.group_by("ticker").agg(pl.col("sentiment_score").mean())

    features = fe.generate_all_features(data_no_bench)
    if kap_scores is not None:
        features = features.join(kap_scores, on="ticker", how="left").with_columns(
            pl.col("sentiment_score").fill_null(0.0)
        )
    features = features.drop_nulls()

    data = alpha.prepare_data(features, target_col="target")
    if data:
        X_train, X_test, y_train, y_test = data
        model = alpha.build_model()
        if model is not None:
            alpha.train_model(model, X_train, y_train)

    signals = None
    alpha_dict = {}
    if data:
        X_full = features.select(alpha.feature_names).to_numpy()
        preds = alpha.predict_proba(model, X_full)
        features = features.with_columns(pl.Series("alpha", preds))

        # store model outputs keyed by date
        alpha_frame = features.select(["date", "ticker", "alpha"])
        pivot = (
            alpha_frame.to_pandas()
            .pivot(index="date", columns="ticker", values="alpha")
            .fillna(0.0)
        )
        alpha_dict = {
            str(d): {t: float(val) for t, val in row.items()}
            for d, row in pivot.to_dict("index").items()
        }

        # optimize weights using last available alphas
        last_day = alpha_frame["date"].max()
        last_alphas = (
            alpha_frame.filter(pl.col("date") == last_day)
            .to_pandas()
            .set_index("ticker")
        )["alpha"]

        prices_pd = prices_no_bench.to_pandas().set_index("date")
        optimizer = RiskBudgeting()
        weights = optimizer.optimize_mvo(prices_pd, last_alphas)

        if weights:
            df = prices_no_bench.to_pandas().set_index("date")
            for t in tickers:
                df[t] = weights.get(t, 0.0)
            signals = pl.from_pandas(df.reset_index())

    if signals is None:
        signals = prices.select("date", *tickers).with_columns(
            [pl.lit(1 / len(tickers)).alias(t) for t in tickers]
        )

    results = backtester.run_backtest(prices_no_bench, signals)
    if results:
        logger.info("Equity curve:\n%s", results["equity_curve"].tail())
        logger.debug("Alpha outputs per date: %s", alpha_dict)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
