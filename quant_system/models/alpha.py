"""Building machine learning models for alpha generation."""

import logging
from typing import Optional, Tuple, List

import numpy as np

try:
    import polars as pl
except ImportError:  # pragma: no cover
    pl = None


class AlphaModelBuilder:
    """Builds and trains ML models for classification."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.feature_names: List[str] = []

    def prepare_data(
        self, df: "pl.DataFrame", target_col: str = "target"
    ) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """Convert a ``pl.DataFrame`` into train/test arrays for classification.

        The frame is split 80/20 without shuffling and no scaling is applied.
        Feature column names are stored for later prediction.
        """

        if pl is None:
            self.logger.error("polars is required to prepare data")
            return None

        feature_cols = [c for c in df.columns if c not in {"date", "ticker", target_col}]
        if not feature_cols:
            self.logger.error("no feature columns found")
            return None

        self.feature_names = feature_cols

        X = df.select(feature_cols).to_numpy()
        y = df[target_col].to_numpy()
        split = int(len(X) * 0.8)
        return X[:split], X[split:], y[:split], y[split:]

    def build_model(self):
        """Return an ``LGBMClassifier`` if possible, otherwise a simple RF."""
        try:
            from lightgbm import LGBMClassifier
            model = LGBMClassifier(n_estimators=200)
            self.logger.debug("LGBMClassifier model created")
        except Exception:
            from sklearn.ensemble import RandomForestClassifier
            self.logger.warning("lightgbm unavailable, using RandomForest")
            model = RandomForestClassifier(n_estimators=100)
        return model

    def train_model(self, model, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Fit the model and log feature importances if available."""
        if hasattr(model, "fit"):
            model.fit(X_train, y_train)
            self.logger.info("model training complete")
            self._log_feature_importances(model)

    def predict_proba(self, model, X: np.ndarray) -> np.ndarray:
        """Return probability predictions from the model."""
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)[:, 1]
        if hasattr(model, "predict"):
            preds = model.predict(X)
            return np.asarray(preds, dtype=float)
        self.logger.error("model does not support prediction")
        return np.zeros(X.shape[0])

    def _log_feature_importances(self, model) -> None:
        """Log feature importances if the model exposes them."""
        if not hasattr(model, "feature_importances_") or not self.feature_names:
            return

        try:
            importances = model.feature_importances_
            pairs = sorted(
                zip(self.feature_names, importances), key=lambda x: x[1], reverse=True
            )
            self.logger.info("Feature importances:")
            for name, score in pairs:
                self.logger.info("  %s: %.4f", name, score)
        except Exception as exc:
            self.logger.warning("could not log feature importances: %s", exc)
