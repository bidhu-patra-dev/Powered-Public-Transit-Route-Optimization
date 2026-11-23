"""
Dynamic Route & Schedule Optimizer:
Uses future-hour predicted congestion and delays to proactively rebalance
transit vehicle headways and prioritize high-impact express routing.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple


class DynamicRouteOptimizer:
    """
    Proactively adjusts scheduled headways based on forecasted delays and demand.
    Minimizes aggregate passenger wait time and prevent bus bunching.
    """
    def __init__(self, fleet_buffer_pct: float = 0.20):
        # Buffer fleet percentage available for peak dynamic insertion
        self.fleet_buffer_pct = fleet_buffer_pct

    def optimize_headways(
        self,
        current_schedule: pd.DataFrame,
        forecasted_delays: pd.DataFrame,
        target_max_delay: float = 6.0
    ) -> pd.DataFrame:
        """
        Computes optimized headway and vehicle allocation per route for future hours.
        Parameters:
        - current_schedule: DataFrame with ['route', 'scheduled_headway_min', 'scheduled_trips', 'demand_index']
        - forecasted_delays: DataFrame with ['route', 'forecasted_delay_min', 'horizon_hours_ahead']
        """
        merged = current_schedule.merge(forecasted_delays, on="route", how="inner").copy()

        # Bottleneck severity score: combines high demand and high predicted delay
        # Normalizes demand_index around 100
        demand_weight = merged["demand_index"] / merged["demand_index"].mean()
        merged["bottleneck_score"] = (merged["forecasted_delay_min"] * demand_weight).round(2)

        # Baseline expected passenger wait time (minutes) = (Headway / 2) + Expected Delay
        merged["baseline_avg_wait_min"] = (
            (merged["scheduled_headway_min"] / 2.0) + merged["forecasted_delay_min"]
        ).round(1)

        # Optimization rule:
        # If predicted delay exceeds threshold (> 5 mins), shorten headway by injecting frequency
        # Extra frequency is proportional to bottleneck score
        def calc_optimized_headway(row):
            delay = row["forecasted_delay_min"]
            current_hw = row["scheduled_headway_min"]
            if delay >= 8.0:
                # Severe bottleneck: inject 30-40% more service (reduce headway)
                new_hw = max(4.0, current_hw * 0.65)
            elif delay >= 5.0:
                # Moderate delay: inject 15-20% more service
                new_hw = max(5.0, current_hw * 0.82)
            elif delay <= 2.0 and row["demand_index"] < 60:
                # Under-utilized route with negligible delay: can slightly relax headway to free buses
                new_hw = min(20.0, current_hw * 1.15)
            else:
                new_hw = current_hw
            return round(new_hw, 1)

        merged["optimized_headway_min"] = merged.apply(calc_optimized_headway, axis=1)
        merged["optimized_trips"] = (60.0 / merged["optimized_headway_min"]).round().astype(int)

        # Recomputed passenger wait time after proactive adjustment
        # Faster headway mitigates passenger backlog and bunching:
        mitigated_delay = merged["forecasted_delay_min"] * (
            merged["optimized_headway_min"] / merged["scheduled_headway_min"]
        )
        merged["optimized_avg_wait_min"] = (
            (merged["optimized_headway_min"] / 2.0) + mitigated_delay
        ).round(1)

        # Quantify savings
        merged["wait_time_saved_min"] = (
            merged["baseline_avg_wait_min"] - merged["optimized_avg_wait_min"]
        ).round(1)
        merged["pct_wait_reduction"] = (
            (merged["wait_time_saved_min"] / merged["baseline_avg_wait_min"]) * 100
        ).round(1)

        # Recommended operational action
        def get_action(row):
            if row["wait_time_saved_min"] >= 4.0:
                return "DISPATCH_STANDBY_BUS"
            elif row["wait_time_saved_min"] >= 2.0:
                return "SHORTEN_HEADWAY"
            elif row["optimized_headway_min"] > row["scheduled_headway_min"]:
                return "REALLOCATE_VEHICLE"
            else:
                return "MAINTAIN_SCHEDULE"

        merged["action"] = merged.apply(get_action, axis=1)

        return merged.sort_values("bottleneck_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    print("Testing Dynamic Route Optimizer...")
    sched = pd.DataFrame({
        "route": ["22", "9", "66", "49", "79"],
        "scheduled_headway_min": [10.0, 8.0, 10.0, 12.0, 10.0],
        "scheduled_trips": [6, 8, 6, 5, 6],
        "demand_index": [180, 220, 195, 120, 140]
    })
    delays = pd.DataFrame({
        "route": ["22", "9", "66", "49", "79"],
        "forecasted_delay_min": [7.5, 9.2, 8.1, 3.2, 4.0],
        "horizon_hours_ahead": [1, 1, 1, 1, 1]
    })
    optimizer = DynamicRouteOptimizer()
    plan = optimizer.optimize_headways(sched, delays)
    print(plan[["route", "scheduled_headway_min", "optimized_headway_min", "baseline_avg_wait_min", "optimized_avg_wait_min", "wait_time_saved_min", "action"]])
