"""
Feature Engineering for Hourly Transit Time-Series:
Extracts cyclic temporal features, lag features, rolling statistics,
and live state conditioning for future-hour forecasting models.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


def add_cyclic_temporal_features(df: pd.DataFrame, hour_col: str = "hour", dow_col: Optional[str] = None) -> pd.DataFrame:
    """
    Adds cyclical sine and cosine encodings for hour of day and day of week.
    """
    df = df.copy()
    if hour_col in df.columns:
        df["sin_hour"] = np.sin(2 * np.pi * df[hour_col] / 24.0)
        df["cos_hour"] = np.cos(2 * np.pi * df[hour_col] / 24.0)

    if dow_col and dow_col in df.columns:
        df["sin_dow"] = np.sin(2 * np.pi * df[dow_col] / 7.0)
        df["cos_dow"] = np.cos(2 * np.pi * df[dow_col] / 7.0)
        df["is_weekend"] = df[dow_col].isin([5, 6]).astype(int)
    else:
        df["is_weekend"] = 0

    return df


def generate_synthetic_hourly_history(
    routes: Optional[List[str]] = None,
    num_days: int = 45,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates a realistic historical hourly transit time-series dataset for Chicago routes.
    Includes diurnal congestion peaks (7-9 AM, 4-6 PM), weekend dips, weather shocks, and delays.
    """
    np.random.seed(seed)
    routes = routes or ["22", "9", "66", "49", "79", "3", "4", "8", "60", "126"]

    start_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=num_days)
    date_range = pd.date_range(start=start_date, periods=num_days * 24, freq="h")

    records = []
    # Base route congestion sensitivity factors
    route_sensitivity = {
        "22": 1.2,  # Clark - dense north side corridor
        "9": 1.3,   # Ashland - major high-traffic arterial
        "66": 1.4,  # Chicago Ave - downtown / river bottleneck
        "49": 1.1,  # Western - long arterial
        "79": 1.0,  # 79th - south side heavy ridership
        "3": 0.9,   # King Drive
        "4": 1.0,   # Cottage Grove
        "8": 1.1,   # Halsted
        "60": 1.0,  # Blue Island
        "126": 1.2  # Jackson - loop egress
    }

    for dt in date_range:
        hour = dt.hour
        dow = dt.day_of_week
        is_weekend = int(dow in [5, 6])

        # Base diurnal arterial speed pattern in Chicago (mph)
        # Rush hours: 7-9 AM and 4-6 PM
        if 7 <= hour <= 9:
            base_speed = 13.5 - 2.5 * (1 - is_weekend)
            rush_hour_factor = 2.0
        elif 16 <= hour <= 18:
            base_speed = 12.0 - 3.0 * (1 - is_weekend)
            rush_hour_factor = 2.5
        elif 10 <= hour <= 15:
            base_speed = 18.0 - 1.5 * (1 - is_weekend)
            rush_hour_factor = 1.0
        elif 20 <= hour <= 23:
            base_speed = 22.0
            rush_hour_factor = 0.5
        else:  # Night
            base_speed = 28.0
            rush_hour_factor = 0.2

        # Occasional weather impact (rain/snow shock in Chicago)
        weather_shock = 1 if (np.random.rand() < 0.08 and 11 <= dt.month <= 3) else 0

        for rt in routes:
            sens = route_sensitivity.get(rt, 1.0)
            noise = np.random.normal(0, 1.0)
            speed = max(5.0, base_speed - (weather_shock * 4.0) / sens + noise)

            # Scheduled trips by hour (GTFS pattern)
            base_trips = 6 if (6 <= hour <= 21) else 2
            if rush_hour_factor > 1.5:
                base_trips = 8
            if is_weekend:
                base_trips = max(2, int(base_trips * 0.75))

            # Scheduled headway
            scheduled_headway = round(60.0 / base_trips, 1)

            # Observed delay in minutes
            # Congestion delay increases non-linearly when speed drops below 18 mph
            speed_deficit = max(0.0, 22.0 - speed)
            expected_delay = (
                (speed_deficit * 0.6 * sens) +
                (rush_hour_factor * 1.5) +
                (weather_shock * 3.5) +
                np.random.exponential(scale=1.2)
            )
            expected_delay = round(max(0.0, expected_delay), 2)

            # Demand index (proxy for passenger boardings)
            demand_index = int(
                (base_trips * 35) * (rush_hour_factor if not is_weekend else 0.8) +
                np.random.normal(0, 15)
            )
            demand_index = max(10, demand_index)

            records.append({
                "timestamp": dt,
                "route": rt,
                "hour": hour,
                "dayofweek": dow,
                "is_weekend": is_weekend,
                "avg_speed_mph": round(speed, 1),
                "scheduled_trips": base_trips,
                "scheduled_headway_min": scheduled_headway,
                "weather_shock": weather_shock,
                "delay_min": expected_delay,
                "demand_index": demand_index
            })

    df = pd.DataFrame(records)
    return df


def create_forecasting_features(
    df: pd.DataFrame,
    lags: List[int] = [1, 2, 3, 24],
    rolling_windows: List[int] = [3, 6]
) -> pd.DataFrame:
    """
    Constructs multi-step lag and rolling window features per route for time-series forecasting.
    """
    df = df.sort_values(["route", "timestamp"]).copy()

    # Add cyclic features
    df = add_cyclic_temporal_features(df, hour_col="hour", dow_col="dayofweek")

    # Grouped lag features
    for lag in lags:
        df[f"delay_lag_{lag}h"] = df.groupby("route")["delay_min"].shift(lag)
        df[f"speed_lag_{lag}h"] = df.groupby("route")["avg_speed_mph"].shift(lag)
        df[f"demand_lag_{lag}h"] = df.groupby("route")["demand_index"].shift(lag)

    # Grouped rolling statistics
    for w in rolling_windows:
        df[f"delay_roll_mean_{w}h"] = (
            df.groupby("route")["delay_min"]
            .transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        )
        df[f"delay_roll_std_{w}h"] = (
            df.groupby("route")["delay_min"]
            .transform(lambda s: s.shift(1).rolling(w, min_periods=1).std().fillna(0))
        )
        df[f"speed_roll_mean_{w}h"] = (
            df.groupby("route")["avg_speed_mph"]
            .transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
        )

    # Drop early warm-up rows with NaNs from lag 24
    df_clean = df.dropna().reset_index(drop=True)
    return df_clean


if __name__ == "__main__":
    print("Testing Feature Engineering Module...")
    df_hist = generate_synthetic_hourly_history(num_days=3)
    df_feat = create_forecasting_features(df_hist)
    print(f"Engineered {len(df_feat.columns)} features over {len(df_feat)} rows.")
