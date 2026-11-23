"""
Future-Hour Transit Forecasting Engine:
Trains and serves multi-step ahead forecasting models (predicting delay and demand
for t+1, t+2, ... t+24 hours ahead) using LightGBM / Gradient Boosting Regressors.
Evaluates error degradation across forecasting horizons.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor

try:
    from lightgbm import LGBMRegressor
    _test = LGBMRegressor(n_estimators=1)
    HAS_LIGHTGBM = True
except Exception:
    HAS_LIGHTGBM = False

DEFAULT_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "models"))


class FutureHourTransitForecaster:
    """
    Multi-horizon forecaster predicting route delay (minutes) and transit demand index.
    """
    def __init__(self, target_col: str = "delay_min", max_horizon: int = 24):
        self.target_col = target_col
        self.max_horizon = max_horizon
        self.models: Dict[int, Any] = {}
        self.feature_names: List[str] = []
        self.evaluation_metrics: Dict[int, Dict[str, float]] = {}

    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Extract valid numerical feature columns."""
        exclude = ["timestamp", "route", "delay_min", "demand_index"]
        return [c for c in df.columns if c not in exclude and not c.startswith("target_")]

    def prepare_multi_horizon_targets(self, df: pd.DataFrame, horizons: List[int]) -> pd.DataFrame:
        """
        Creates target columns for future horizons: target_h1, target_h2, ... target_hk.
        """
        df = df.sort_values(["route", "timestamp"]).copy()
        for h in horizons:
            df[f"target_h{h}"] = df.groupby("route")[self.target_col].shift(-h)
        return df

    def train_multi_horizon_models(
        self,
        df_features: pd.DataFrame,
        horizons: List[int] = [1, 2, 3, 6, 12, 24],
        train_split: float = 0.8
    ) -> Dict[int, Dict[str, float]]:
        """
        Trains a specialized direct forecaster for each forecast horizon (e.g. t+1h, t+2h, t+3h, t+6h, t+12h, t+24h).
        """
        df_prep = self.prepare_multi_horizon_targets(df_features, horizons)
        self.feature_names = self.get_feature_columns(df_features)

        # Time-based train / test split
        unique_times = df_prep["timestamp"].drop_duplicates().sort_values()
        split_idx = int(len(unique_times) * train_split)
        split_time = unique_times.iloc[split_idx]

        train_data = df_prep[df_prep["timestamp"] < split_time]
        test_data = df_prep[df_prep["timestamp"] >= split_time]

        print(f"Training multi-horizon models on {len(train_data)} samples, testing on {len(test_data)} samples.")
        print(f"Feature count: {len(self.feature_names)}")

        X_train_base = train_data[self.feature_names]
        X_test_base = test_data[self.feature_names]

        self.evaluation_metrics = {}

        for h in horizons:
            target_col = f"target_h{h}"
            # Drop rows where future target is NaN (at the end of series)
            valid_train = train_data[target_col].notna()
            valid_test = test_data[target_col].notna()

            X_tr = X_train_base[valid_train]
            y_tr = train_data.loc[valid_train, target_col]

            X_te = X_test_base[valid_test]
            y_te = test_data.loc[valid_test, target_col]

            # Initialize Gradient Boosting Regressor (LightGBM or HistGradientBoosting)
            if HAS_LIGHTGBM:
                model = LGBMRegressor(
                    n_estimators=120,
                    learning_rate=0.06,
                    max_depth=6,
                    num_leaves=31,
                    random_state=42,
                    verbosity=-1
                )
            else:
                model = HistGradientBoostingRegressor(
                    max_iter=120,
                    learning_rate=0.06,
                    max_depth=6,
                    max_leaf_nodes=31,
                    random_state=42
                )
            model.fit(X_tr, y_tr)
            self.models[h] = model

            # Predict and evaluate
            y_pred = model.predict(X_te)
            mae = float(mean_absolute_error(y_te, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y_te, y_pred)))
            r2 = float(r2_score(y_te, y_pred))

            self.evaluation_metrics[h] = {
                "horizon_hours": h,
                "MAE": round(mae, 2),
                "RMSE": round(rmse, 2),
                "R2": round(r2, 3)
            }
            print(f"-> Horizon +{h}h: MAE = {mae:.2f} mins | RMSE = {rmse:.2f} mins | R² = {r2:.3f}")

        return self.evaluation_metrics

    def predict_future_hours(self, current_state_features: pd.DataFrame, horizons: List[int]) -> pd.DataFrame:
        """
        Generates predictions for current state across future horizons.
        """
        results = []
        routes = current_state_features["route"].tolist()
        X_curr = current_state_features[self.feature_names]

        for h in horizons:
            if h in self.models:
                preds = self.models[h].predict(X_curr)
                for rt, pred in zip(routes, preds):
                    results.append({
                        "route": rt,
                        "horizon_hours_ahead": h,
                        "forecasted_delay_min": round(max(0.0, float(pred)), 1)
                    })

        return pd.DataFrame(results)

    def save_model_artifacts(self, output_dir: Optional[str] = None) -> str:
        """Persists trained models and metadata."""
        out = output_dir or DEFAULT_OUTPUT_DIR
        os.makedirs(out, exist_ok=True)
        artifact_path = os.path.join(out, f"cta_{self.target_col}_forecaster.joblib")
        joblib.dump({
            "models": self.models,
            "feature_names": self.feature_names,
            "evaluation_metrics": self.evaluation_metrics,
            "target_col": self.target_col
        }, artifact_path)
        print(f"Saved forecasting model artifact to {artifact_path}")
        return artifact_path

    @classmethod
    def load_model_artifacts(cls, artifact_path: str) -> "FutureHourTransitForecaster":
        """Loads trained model artifacts."""
        data = joblib.load(artifact_path)
        forecaster = cls(target_col=data["target_col"])
        forecaster.models = data["models"]
        forecaster.feature_names = data["feature_names"]
        forecaster.evaluation_metrics = data["evaluation_metrics"]
        return forecaster


if __name__ == "__main__":
    from src.features import generate_synthetic_hourly_history, create_forecasting_features
    print("Testing Future-Hour Forecaster pipeline...")
    df_raw = generate_synthetic_hourly_history(num_days=30)
    df_feats = create_forecasting_features(df_raw)
    forecaster = FutureHourTransitForecaster(target_col="delay_min")
    metrics = forecaster.train_multi_horizon_models(df_feats, horizons=[1, 2, 3, 6])
    forecaster.save_model_artifacts()
