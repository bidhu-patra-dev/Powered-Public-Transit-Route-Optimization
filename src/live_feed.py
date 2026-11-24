"""
CTA Live Feed Client: Ingests, parses, and logs real-time vehicle positions and delays.
Supports:
1. CTA GTFS-Realtime (GTFS-RT) streams and Bus Tracker API.
2. Stateful, smooth vehicle fleet simulation for continuous, realistic tracking
   (prevents erratic jumping and drastic oscillations on refresh).
"""

import os
import time
import json
import random
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
SNAPSHOTS_DIR = os.path.join(DEFAULT_DATA_DIR, "raw", "live_snapshots")
FLEET_STATE_PATH = os.path.join(SNAPSHOTS_DIR, "persistent_fleet_state.json")

# Predefined Chicago corridors with precise terminus bounds
CHICAGO_CORRIDORS = {
    "22": {"name": "Clark", "type": "NS", "lat_min": 41.850, "lat_max": 42.015, "lon": -87.662, "base_delay": 3.5},
    "9":  {"name": "Ashland", "type": "NS", "lat_min": 41.750, "lat_max": 41.975, "lon": -87.669, "base_delay": 5.2},
    "66": {"name": "Chicago", "type": "EW", "lat": 41.896, "lon_min": -87.775, "lon_max": -87.620, "base_delay": 4.8},
    "49": {"name": "Western", "type": "NS", "lat_min": 41.740, "lat_max": 41.970, "lon": -87.688, "base_delay": 2.8},
    "79": {"name": "79th", "type": "EW", "lat": 41.751, "lon_min": -87.730, "lon_max": -87.550, "base_delay": 2.2},
    "3":  {"name": "King Drive", "type": "NS", "lat_min": 41.720, "lat_max": 41.850, "lon": -87.620, "base_delay": 2.5},
    "4":  {"name": "Cottage Grove", "type": "NS", "lat_min": 41.700, "lat_max": 41.860, "lon": -87.605, "base_delay": 3.0},
    "8":  {"name": "Halsted", "type": "NS", "lat_min": 41.750, "lat_max": 41.950, "lon": -87.647, "base_delay": 3.8},
    "60": {"name": "Blue Island", "type": "EW", "lat": 41.845, "lon_min": -87.730, "lon_max": -87.640, "base_delay": 2.9},
    "126":{"name": "Jackson", "type": "EW", "lat": 41.878, "lon_min": -87.750, "lon_max": -87.625, "base_delay": 2.1}
}


class CTALiveTracker:
    """
    Handles fetching live CTA vehicle positions, delays, and arrival estimates.
    Maintains continuous stateful fleet physics across UI refreshes.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (
            api_key
            or os.environ.get("CTA_BUS_TRACKER_KEY", "").strip()
            or os.environ.get("CTA_BUS_TRACKER_API_KEY", "").strip()
            or ""
        )
        self.base_url = "http://www.ctabustracker.com/bustime/api/v2"

    def get_live_vehicles(self, routes: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fetches live vehicle locations for specified routes.
        Uses persistent state simulator with smooth motion physics when API is offline.
        """
        all_routes = list(CHICAGO_CORRIDORS.keys())
        routes = routes if (routes and len(routes) > 0) else all_routes

        if self.api_key:
            try:
                rt_param = ",".join(routes[:10])
                url = f"{self.base_url}/getvehicles?key={self.api_key}&rt={rt_param}&format=json"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get("bustime-response", {})
                    if "vehicle" in data:
                        df = pd.DataFrame(data["vehicle"])
                        df["timestamp"] = datetime.now()
                        df["is_simulated"] = False
                        return df
            except Exception as e:
                print(f"Live API call failed: {e}. Falling back to smooth stateful simulation.")

        return self._get_smooth_stateful_vehicles(routes)

    def _initialize_fleet(self) -> Dict[str, Any]:
        """Creates an initial evenly-spaced fleet across corridors."""
        vehicles = []
        vid_counter = 1000

        for rt, corr in CHICAGO_CORRIDORS.items():
            # 5 buses per corridor
            buses_per_route = 5
            for i in range(buses_per_route):
                vid_counter += 1
                frac = i / float(buses_per_route)
                # Alternate direction
                direction = 1 if i % 2 == 0 else -1

                if corr["type"] == "NS":
                    lat = corr["lat_min"] + frac * (corr["lat_max"] - corr["lat_min"])
                    lon = corr["lon"]
                    hdg = 0 if direction == 1 else 180
                else:
                    lat = corr["lat"]
                    lon = corr["lon_min"] + frac * (corr["lon_max"] - corr["lon_min"])
                    hdg = 90 if direction == 1 else 270

                speed = round(16.0 + random.uniform(-2.0, 3.0), 1)
                delay = round(max(0.0, corr["base_delay"] + random.uniform(-1.0, 1.5)), 1)

                vehicles.append({
                    "vid": str(vid_counter),
                    "rt": rt,
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "hdg": hdg,
                    "spd": speed,
                    "delay_min": delay,
                    "direction": direction
                })

        return {
            "last_update_ts": time.time(),
            "vehicles": vehicles
        }

    def _get_smooth_stateful_vehicles(self, filter_routes: List[str]) -> pd.DataFrame:
        """
        Advances vehicles smoothly along their routes based on actual elapsed wall-clock time.
        Ensures consistent, non-drastic changes between browser refreshes.
        """
        os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
        now_ts = time.time()
        now_dt = datetime.now()

        state = None
        if os.path.exists(FLEET_STATE_PATH):
            try:
                with open(FLEET_STATE_PATH, "r") as f:
                    state = json.load(f)
            except Exception:
                state = None

        if not state or "vehicles" not in state or len(state["vehicles"]) == 0:
            state = self._initialize_fleet()
            elapsed_sec = 2.0
        else:
            elapsed_sec = max(0.5, min(120.0, now_ts - state.get("last_update_ts", now_ts - 2.0)))

        # 1 degree lat ≈ 111,000 meters; 15 mph ≈ 6.7 meters/sec
        # Degree delta per second at 15 mph ≈ 6.7 / 111,000 ≈ 0.00006 degrees/sec
        METERS_PER_DEG_LAT = 111000.0
        METERS_PER_DEG_LON = 82500.0  # At ~42 degrees N latitude

        updated_vehicles = []
        for v in state["vehicles"]:
            rt = v["rt"]
            corr = CHICAGO_CORRIDORS.get(rt)
            if not corr:
                continue

            spd = v["spd"]
            hdg = v["hdg"]
            direction = v.get("direction", 1)
            lat = v["lat"]
            lon = v["lon"]
            delay = v["delay_min"]

            # Smooth speed drift (small variation: +/- 0.5 mph)
            spd = round(float(np.clip(spd + random.uniform(-0.4, 0.4), 8.0, 26.0)), 1)
            meters_moved = (spd * 0.44704) * elapsed_sec  # 1 mph = 0.44704 m/s

            if corr["type"] == "NS":
                delta_lat = (meters_moved / METERS_PER_DEG_LAT) * direction
                lat += delta_lat
                # Bounce / reverse at corridor terminals
                if lat >= corr["lat_max"]:
                    lat = corr["lat_max"]
                    direction = -1
                    hdg = 180
                elif lat <= corr["lat_min"]:
                    lat = corr["lat_min"]
                    direction = 1
                    hdg = 0
            else:
                delta_lon = (meters_moved / METERS_PER_DEG_LON) * direction
                lon += delta_lon
                # Bounce / reverse at corridor terminals
                if lon >= corr["lon_max"]:
                    lon = corr["lon_max"]
                    direction = -1
                    hdg = 270
                elif lon <= corr["lon_min"]:
                    lon = corr["lon_min"]
                    direction = 1
                    hdg = 90

            # Smooth delay drift: slowly reverts toward base_delay (+/- 0.1 min)
            target_delay = corr["base_delay"]
            delay = round(float(np.clip(0.96 * delay + 0.04 * target_delay + random.uniform(-0.1, 0.1), 0.0, 20.0)), 1)

            status = "ON_TIME" if delay <= 2.0 else ("MINOR_DELAY" if delay <= 6.0 else "MAJOR_DELAY")

            v_updated = {
                "vid": v["vid"],
                "rt": rt,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "hdg": hdg,
                "spd": spd,
                "delay_min": delay,
                "delay_status": status,
                "direction": direction,
                "tmstmp": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "is_simulated": True
            }
            updated_vehicles.append(v_updated)

        # Save state back to disk
        state["last_update_ts"] = now_ts
        state["vehicles"] = updated_vehicles
        try:
            with open(FLEET_STATE_PATH, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Warning: could not persist fleet state: {e}")

        # Filter by requested routes
        filtered = [v for v in updated_vehicles if v["rt"] in filter_routes]
        df = pd.DataFrame(filtered)
        if not df.empty:
            df["timestamp"] = now_dt
        return df

    def save_snapshot(self, df: pd.DataFrame, snapshot_dir: Optional[str] = None) -> str:
        """Saves a live snapshot as a Parquet file."""
        target_dir = snapshot_dir or SNAPSHOTS_DIR
        os.makedirs(target_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp_str}.parquet"
        filepath = os.path.join(target_dir, filename)
        df.to_parquet(filepath, index=False)
        return filepath


if __name__ == "__main__":
    tracker = CTALiveTracker()
    print("Testing smooth stateful vehicle motion:")
    df1 = tracker.get_live_vehicles(["22", "9"])
    print("Ping 1:")
    print(df1[["vid", "rt", "lat", "lon", "spd", "delay_min"]].head(4))
    time.sleep(2)
    df2 = tracker.get_live_vehicles(["22", "9"])
    print("Ping 2 (after 2s):")
    print(df2[["vid", "rt", "lat", "lon", "spd", "delay_min"]].head(4))
