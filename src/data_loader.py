"""Loading, validation, and download helpers for Chicago CTA bus ridership and transit data."""

import os
import zipfile
from pathlib import Path
from typing import Dict, Optional, Union
import requests
import pandas as pd

CTA_GTFS_URL = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"
CTA_BUS_RIDERSHIP_URL = "https://data.cityofchicago.org/api/views/jyb9-n7fm/rows.csv?accessType=DOWNLOAD"
CHICAGO_TRAFFIC_CURRENT_URL = "https://data.cityofchicago.org/api/views/n4j6-wkkf/rows.csv?accessType=DOWNLOAD"

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))


def download_file(url: str, dest_path: str, chunk_size: int = 1024 * 1024) -> str:
    """Download a file with streaming support."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    return dest_path


def load_bus_ridership(path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Load validated route/date boardings with canonical columns.

    CTA's public export uses ``route``, ``date``, ``daytype``, and ``rides``.
    Exact duplicate records are removed; conflicting duplicates and malformed
    observations fail loudly so they can be investigated instead of summed.
    """
    if path is None:
        path = os.path.join(DEFAULT_DATA_DIR, "raw", "cta_bus_ridership.csv")
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            download_file(CTA_BUS_RIDERSHIP_URL, str(path))

    frame = pd.read_csv(path, dtype="string", keep_default_na=False)
    by_lower = {str(column).strip().lower(): column for column in frame.columns}
    aliases = {
        "date": ("date", "service_date"),
        "route": ("route", "route_name", "bus_route"),
        "daytype": ("daytype", "day_type"),
        "rides": ("rides", "ridership", "total_rides", "boardings", "daily_boardings"),
    }
    rename = {}
    missing = []
    for canonical, options in aliases.items():
        match = next((by_lower[name] for name in options if name in by_lower), None)
        if match is None:
            missing.append(f"{canonical} ({', '.join(options)})")
        else:
            rename[match] = canonical
    if missing:
        raise ValueError(f"CSV is missing required columns: {'; '.join(missing)}. Found: {list(frame.columns)}")

    frame = frame.rename(columns=rename)[["date", "route", "daytype", "rides"]].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["route"] = frame["route"].str.strip()
    frame["daytype"] = frame["daytype"].str.strip().str.upper()
    frame["rides"] = pd.to_numeric(frame["rides"].str.replace(",", "", regex=False), errors="coerce")

    invalid = (
        frame["date"].isna()
        | frame["route"].eq("")
        | ~frame["daytype"].isin(["W", "A", "U"])
        | frame["rides"].isna()
        | (frame["rides"] < 0)
        | (frame["rides"] % 1 != 0)
    )
    if invalid.any():
        raise ValueError(f"Found {int(invalid.sum())} invalid ridership rows; inspect source before training")

    frame["date"] = frame["date"].dt.normalize()
    frame["rides"] = frame["rides"].astype("int64")
    frame = frame.drop_duplicates()
    conflicts = frame.duplicated(["route", "date"], keep=False)
    if conflicts.any():
        examples = frame.loc[conflicts, ["route", "date", "daytype", "rides"]].head(8).to_dict("records")
        raise ValueError(f"Conflicting route/date observations found; quarantine and resolve them. Examples: {examples}")
    return frame.sort_values(["date", "route"]).reset_index(drop=True)


def load_cta_gtfs(data_dir: Optional[str] = None, force_download: bool = False) -> Dict[str, pd.DataFrame]:
    """
    Downloads (if not present) and parses CTA GTFS static feed text files.
    Returns dictionary with keys: routes, stops, trips, stop_times, shapes, calendar.
    """
    base_dir = data_dir or DEFAULT_DATA_DIR
    gtfs_dir = os.path.join(base_dir, "raw", "gtfs")
    zip_path = os.path.join(base_dir, "raw", "google_transit.zip")

    os.makedirs(gtfs_dir, exist_ok=True)
    expected_files = ["routes.txt", "stops.txt", "trips.txt", "stop_times.txt", "shapes.txt"]
    extracted = all(os.path.exists(os.path.join(gtfs_dir, f)) for f in expected_files)

    if force_download or not extracted:
        download_file(CTA_GTFS_URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(gtfs_dir)

    gtfs_tables = {}
    for filename in os.listdir(gtfs_dir):
        if filename.endswith(".txt"):
            table_name = filename.replace(".txt", "")
            file_path = os.path.join(gtfs_dir, filename)
            try:
                gtfs_tables[table_name] = pd.read_csv(file_path, low_memory=False)
            except Exception as e:
                print(f"Warning: Failed to parse {filename}: {e}")

    return gtfs_tables


def load_traffic_congestion(data_dir: Optional[str] = None, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """Loads Chicago Traffic Tracker Congestion Estimates by Segments."""
    base_dir = data_dir or DEFAULT_DATA_DIR
    csv_path = os.path.join(base_dir, "raw", "chicago_traffic_congestion.csv")

    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        download_file(CHICAGO_TRAFFIC_CURRENT_URL, csv_path)

    df = pd.read_csv(csv_path, nrows=sample_rows)
    return df
