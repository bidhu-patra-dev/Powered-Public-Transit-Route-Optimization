"""
CTA Data Loader: Downloads, extracts, and parses Chicago Transit Authority (CTA) datasets.
Datasets covered:
1. CTA GTFS Static Feed (routes, stops, trips, stop_times, shapes, calendar)
2. CTA Bus Ridership (Daily Totals by Route from Chicago Data Portal)
3. Chicago Traffic Tracker (Historical / Real-time Congestion Estimates by Segments)
"""

import os
import zipfile
import requests
import pandas as pd
from typing import Dict, Optional

CTA_GTFS_URL = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"
# Chicago Data Portal Socrata API / CSV export endpoints
CTA_BUS_RIDERSHIP_URL = "https://data.cityofchicago.org/api/views/jyb9-n7fm/rows.csv?accessType=DOWNLOAD"
CHICAGO_TRAFFIC_CURRENT_URL = "https://data.cityofchicago.org/api/views/n4j6-wkkf/rows.csv?accessType=DOWNLOAD"

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))


def download_file(url: str, dest_path: str, chunk_size: int = 1024 * 1024) -> str:
    """Download a file with streaming support."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"File already exists: {dest_path}")
        return dest_path

    print(f"Downloading {url} to {dest_path}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    print(f"Downloaded successfully: {dest_path} ({os.path.getsize(dest_path)} bytes)")
    return dest_path


def load_cta_gtfs(data_dir: Optional[str] = None, force_download: bool = False) -> Dict[str, pd.DataFrame]:
    """
    Downloads (if not present) and parses CTA GTFS static feed text files.
    Returns dictionary with keys: routes, stops, trips, stop_times, shapes, calendar.
    """
    base_dir = data_dir or DEFAULT_DATA_DIR
    gtfs_dir = os.path.join(base_dir, "raw", "gtfs")
    zip_path = os.path.join(base_dir, "raw", "google_transit.zip")

    os.makedirs(gtfs_dir, exist_ok=True)

    # Check if extracted files exist
    expected_files = ["routes.txt", "stops.txt", "trips.txt", "stop_times.txt", "shapes.txt"]
    extracted = all(os.path.exists(os.path.join(gtfs_dir, f)) for f in expected_files)

    if force_download or not extracted:
        download_file(CTA_GTFS_URL, zip_path)
        print("Extracting GTFS zip archive...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(gtfs_dir)
        print(f"Extracted GTFS files into {gtfs_dir}")

    gtfs_tables = {}
    for filename in os.listdir(gtfs_dir):
        if filename.endswith(".txt"):
            table_name = filename.replace(".txt", "")
            file_path = os.path.join(gtfs_dir, filename)
            # Parse CSV
            try:
                # low_memory=False avoids mixed dtype warnings on large GTFS files
                gtfs_tables[table_name] = pd.read_csv(file_path, low_memory=False)
                print(f"Loaded GTFS table '{table_name}': {len(gtfs_tables[table_name])} records")
            except Exception as e:
                print(f"Warning: Failed to parse {filename}: {e}")

    return gtfs_tables


def load_bus_ridership(data_dir: Optional[str] = None, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Loads CTA Bus Ridership (Daily Totals by Route).
    Downloads from Chicago Data Portal if not already present.
    """
    base_dir = data_dir or DEFAULT_DATA_DIR
    csv_path = os.path.join(base_dir, "raw", "cta_bus_ridership.csv")

    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        download_file(CTA_BUS_RIDERSHIP_URL, csv_path)

    df = pd.read_csv(csv_path, nrows=sample_rows, parse_dates=["date"] if "date" in pd.read_csv(csv_path, nrows=1).columns else None)
    if "date" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    print(f"Loaded Bus Ridership: {len(df)} records")
    return df


def load_traffic_congestion(data_dir: Optional[str] = None, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Loads Chicago Traffic Tracker Congestion Estimates by Segments.
    """
    base_dir = data_dir or DEFAULT_DATA_DIR
    csv_path = os.path.join(base_dir, "raw", "chicago_traffic_congestion.csv")

    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        download_file(CHICAGO_TRAFFIC_CURRENT_URL, csv_path)

    df = pd.read_csv(csv_path, nrows=sample_rows)
    print(f"Loaded Traffic Congestion: {len(df)} records")
    return df


if __name__ == "__main__":
    print("Testing data loader module...")
    # Quick probe of GTFS download and loading
    tables = load_cta_gtfs()
    print(f"GTFS keys: {list(tables.keys())}")
