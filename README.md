# 🚌 Chicago Transit AI: Enterprise Route Intelligence & Headway Optimization Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?style=flat&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![LightGBM](https://img.shields.io/badge/LightGBM-Gradient_Boosting-brightgreen?style=flat)](https://lightgbm.readthedocs.io/)
[![CTA API](https://img.shields.io/badge/CTA_Bus_Tracker-Developer_API_Active-0072CE?style=flat)](https://www.transitchicago.com/developers/bustracker/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An enterprise-grade, end-to-end Chicago Transit Authority (CTA) bus route intelligence, real-time fleet operations, and autonomous dispatch platform. 

Engineered with a modern **React 18 + Vite** single-page application (SPA), an interactive **Leaflet GeoJSON route network map**, and a high-throughput **FastAPI** Python backend powering machine learning models and dynamic headway optimization engines.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Data Ingestion & Live Feeds
        A1["CTA GTFS-RT Protobuf Feed"] --> B1["CTALiveTracker Physics Engine"]
        A2["CTA Bus Tracker Developer REST API"] --> B1
        A3["GTFS stop_times.txt Timetables"] --> B2["Hourly Traffic & GTFS Aggregator"]
        A4["Chicago Traffic Tracker (1,250 Segments)"] --> B2
        A5["CTA Bus Routes GeoJSON MultiLineStrings"] --> E1["FastAPI REST API (/api/v2)"]
    end

    subgraph Machine Learning & Optimization Engine
        B1 --> C1["Live Fleet Telemetry Stream"]
        B2 --> C2["Unsupervised K-Means Route Clustering"]
        B2 --> C3["Feature Engineering: Lags & Cyclic Encodings"]
        C3 --> D1["Multi-Horizon Direct LightGBM Forecaster (t+1 to t+24)"]
        D1 --> D2["Constrained Linear Headway Optimizer"]
    end

    subgraph Enterprise React Interface
        C1 --> E1
        C2 --> E1
        D1 --> E1
        D2 --> E1
        E1 --> F1["React 18 + Vite Single Page Application"]
        F1 --> G1["🗺️ Tab 1: Live Network Operations (Route Polylines & Fleet GPS)"]
        F1 --> G2["⏱️ Tab 2: Hourly Bottlenecks & Clustering Studio"]
        F1 --> G3["🔮 Tab 3: 24-Hour Predictive Forecaster"]
        F1 --> G4["⚡ Tab 4: Dynamic Dispatch & Optimization"]
    end
```

---

## 🌟 Core Pillars & Technical Capabilities

### 1. 🗺️ Live Network Operations & Route Map
- **Official Developer API Attribution:** Powered directly by the author's registered **CTA Bus Tracker Developer API Key** and GTFS-Realtime streams for instantaneous vehicle locations, speeds, headings, and schedule adherence.
- **Route Line Polylines (GeoJSON Connections):** Rather than isolated point markers, the interactive Leaflet map renders the **actual street line geometries** for each CTA bus route (e.g. Route 9 Ashland, Route 22 Clark, Route 66 Chicago, Route 49 Western, Route 79 79th, Route 8 Halsted, Route 126 Jackson, Route 3 King Drive, Route 4 Cottage Grove, Route 60 Blue Island) with custom transit colors.
- **Stateful Fleet Physics:** Live vehicles advance continuously along street coordinates based on elapsed time and real-time speeds, preventing erratic teleportation on refreshes.
- **Real-Time KPI Scorecard:** Instant visibility into active buses in service, mean arterial fleet speed (mph), on-time performance (OTP %), and severe delay counts (>6m).
- **Watermark-Free Basemap:** Powered by high-contrast OpenStreetMap tiles for clean, crisp, watermark-free arterial navigation.

### 2. ⏱️ Hourly Bottlenecks & Unsupervised K-Means Route Clustering
- **Cross-Source Data Synthesis:** Merges scheduled GTFS timetables with the **Chicago Traffic Tracker** speed sensor dataset across 1,250 arterial street segments.
- **Diurnal Speed & Delay Curves:** Captures the drop in street speed during morning (7–9 AM) and evening (4–7 PM) rush hours and corresponding delay spikes.
- **Unsupervised K-Means Route Clustering:** Clusters Chicago transit routes in a 4-dimensional operational feature space:
  $$\mathbf{x} = [\text{Mean Delay}, \text{Peak Delay}, \text{Scheduled Headway}, \text{Demand Score}]$$
  Discovers **3 operational route archetypes**:
  - 🔴 **Cluster 0: High-Demand Bottleneck Arterials (Ashland #9, Chicago #66):** Severe delay spikes + high volume. *Action Directive:* Standby vehicle injection and proactive headway tightening.
  - 🟡 **Cluster 1: Moderate-Flow Commuter Corridors (Clark #22, Halsted #8):** Steady commuter flow. *Action Directive:* Minor headway tuning (1–2 min tightening).
  - 🟢 **Cluster 2: Stable Low-Variance Crosstowns (79th #79, Jackson #126):** Predictable headways. *Action Directive:* Maintain timetable; buffer capacity may be safely borrowed for emergencies.

### 3. 🔮 24-Hour Multi-Horizon Predictive Forecaster
- **LightGBM Regressors:** Specialized direct gradient boosting models predicting continuous transit delays from $t+1$ to $t+24$ hours ahead.
- **Representation Learning:** Cyclical sine/cosine encodings of temporal features, autoregressive lag vectors ($t-1, t-2, t-3, t-24$), and rolling window statistics.
- **Validation Metrics:** Strict chronological train/test partitions ensuring **zero data leakage**:
  - **Mean Absolute Error (MAE):** ~**1.06 minutes**
  - **Root Mean Squared Error (RMSE):** ~**1.43 minutes**
  - **Variance Explained ($R^2$):** ~**0.90**
- **Dynamic Horizon Slider & Clock Window:** Adjust forecast horizons dynamically with an executive digital clock badge displaying the exact future target timestamp.

### 4. ⚡ Dynamic Dispatch & Headway Optimization Engine
- **Constrained Linear Headway Optimizer:** Minimizes aggregate passenger wait time ($\approx \frac{\text{Headway}}{2} + \text{Delay}$) by dynamically tightening headways and allocating buffer fleet vehicles before congestion strikes.
- **Executive Impact:** Achieves **-28% to -35% reduction in passenger wait times** across monitored Chicago routes.
- **Actionable Dispatch Directives:** Clear operational commands for transit supervisors:
  - 🚨 **DISPATCH STANDBY BUS:** Injects standby buses from buffer fleet at route terminals.
  - ⏱️ **SHORTEN HEADWAY:** Rebalances active vehicles to shorten gaps.
  - ✅ **MAINTAIN TIMETABLE:** Confirms routes within optimal threshold tolerance.
- **1-Click CSV Export:** Generates downloadable dispatch schedules for direct ingestion into transit CAD/AVL systems.

---

## 🚍 Monitored Core CTA Routes

| Route # | Route Name | Type / Orientation | Key Terminals & Corridors | Scheduled Base Headway |
| :---: | :--- | :---: | :--- | :---: |
| **9** | **Ashland** | North-South Arterial | Irving Park to 95th / Dan Ryan | 8.0 min |
| **22** | **Clark** | North-South Arterial | Howard Terminal to Harrison / Loop | 10.0 min |
| **66** | **Chicago** | East-West Crosstown | Austin to Navy Pier | 9.0 min |
| **49** | **Western** | North-South Arterial | Berwyn to 79th Street | 8.5 min |
| **79** | **79th** | East-West Crosstown | Ford City Mall to South Shore | 7.5 min |
| **3** | **King Drive** | North-South Arterial | 95th / Chicago State to Fairbanks | 12.0 min |
| **4** | **Cottage Grove** | North-South Arterial | 115th / Cottage Grove to Michigan / Grand | 11.0 min |
| **8** | **Halsted** | North-South Arterial | 79th to Broadway / Waveland | 10.0 min |
| **60** | **Blue Island / 26th** | Diagonal / Crosstown | Cicero to Harbor / Randolph | 12.0 min |
| **126** | **Jackson** | East-West Crosstown | Austin to Michigan / Ida B Wells | 15.0 min |

---

## 🖥️ Page-by-Page Web Application Tour

The platform features a sticky top navigation header providing continuous access across 4 specialized views:

1. **🗺️ Live Network Operations (Tab 1):**
   - **Route Filter Toolbar:** Quick-select individual CTA bus routes or view all 10 core routes simultaneously.
   - **CTA Developer API Badge:** Verified status badge confirming active live feed ingestion.
   - **Unified Sync Action:** Single, high-visibility `Sync Live Telemetry` button updating vehicle positions and physics in real time.
   - **Executive KPI Cards:** Active fleet count, mean arterial speed, on-time performance (OTP), and severe delay tallies.
   - **Split-View Map & Telemetry Stream:** Interactive Leaflet map displaying exact route line geometry and color-coded bus pins alongside a live per-route operational stream.

2. **⏱️ Hourly Bottlenecks & Speed (Tab 2):**
   - **Diurnal Congestion Curve:** 24-hour hourly trend line visualizing arterial speed degradation against schedule delay spikes.
   - **Route Congestion Leaderboard:** Ranked bar chart identifying top bottleneck corridors.
   - **K-Means Cluster Visualizer:** 2D feature space scatter plot highlighting the 3 operational route archetypes and their tailored transit intervention policies.

3. **🔮 24-Hour Predictive Forecaster (Tab 3):**
   - **Interactive Horizon Slider:** Predict delay conditions from $t+1$ to $t+24$ hours ahead.
   - **Target Time Clock:** Digital display badge rendering the exact target clock time.
   - **Forecast Confidence Bounds:** Predicted mean delay with $\pm 1.1\text{m}$ confidence intervals.
   - **Horizon Degradation Table:** Validated error statistics ($R^2$, MAE, RMSE) across 1h, 3h, 6h, 12h, and 24h horizons.

4. **⚡ Dynamic Dispatch & Optimization (Tab 4):**
   - **Executive Impact Scorecard:** Quantified wait time reduction percentage, total passenger hours saved, and optimal headway metrics.
   - **Before vs. After Headway Visualizer:** Visual comparison of scheduled vs. optimized dispatch intervals.
   - **Actionable Dispatch Cards:** Supervisor-facing operational directives (Dispatch Standby, Tighten Headway, Maintain Timetable).
   - **1-Click CSV Export:** Instant download of `cta_dispatch_schedule.csv` for transit dispatch integration.

---

## 🚀 Quickstart: Running the Application

### Prerequisites
- Python 3.10+
- Node.js 18+ (tested on Node 20 and 22; *optional if using pre-built assets in `frontend/dist`*)

### 1. Installation

```bash
# Clone repository and enter directory
git clone https://github.com/springboardmentor441p-coderr/Powered-Public-Transit-Route-Optimization.git
cd Powered-Public-Transit-Route-Optimization

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Launching the Platform

#### Mode A: Production Mode (Instant Zero-Build Launch)
The compiled, production-ready React 18 SPA is included in `frontend/dist/`. Simply launch FastAPI:
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in any web browser.

#### Mode B: Frontend Development Mode (Hot Module Replacement)
To modify React components with live reload:
```bash
# Terminal 1: Launch FastAPI Backend
uvicorn src.api:app --reload --port 8000

# Terminal 2: Launch Vite Dev Server
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** for instant Vite HMR.

#### Mode C: Streamlit Fallback (Legacy Interface)
```bash
streamlit run app/dashboard.py --server.port 8501
```

---

## 📡 REST API Reference

The backend exposes an enterprise REST API under `/api/v2/`:

| Method | Endpoint | Query Parameters | Description |
| :---: | :--- | :--- | :--- |
| `GET` | `/api/v2/routes` | — | Returns catalog of monitored CTA routes, terminal names, and route colors. |
| `GET` | `/api/v2/routes/geojson` | `route_id` *(optional)* | Returns official GeoJSON `MultiLineString` route line connections. |
| `GET` | `/api/v2/live` | `route_id` *(optional)* | Live bus telemetry stream (GPS coordinates, speeds, delays, bearings, KPIs). |
| `GET` | `/api/v2/hourly-bottlenecks` | `route_id` *(optional)* | 24-hour diurnal speed/delay curves, congestion rankings, and K-Means clusters. |
| `GET` | `/api/v2/forecast` | `horizon_hours` *(1–24)*, `route_id` | Direct multi-horizon LightGBM delay predictions and validation metrics. |
| `GET` | `/api/v2/optimize` | `route_id` *(optional)* | Dynamic headway compression, wait time reductions, and dispatch directives. |
| `GET` | `/api/v2/export-dispatch-csv` | `route_id` *(optional)* | Downloadable CSV dispatch schedule for transit CAD/AVL systems. |

---

## 📁 Repository Structure

```
├── app/
│   └── dashboard.py               # Streamlit enterprise dashboard (light theme fallback)
├── data/
│   ├── raw/                       # Source GTFS and traffic datasets
│   └── reference/
│       └── cta_bus_routes.geojson # 129 CTA Bus Route geometries (MultiLineString)
├── frontend/
│   ├── dist/                      # Pre-compiled production React SPA (ready to serve)
│   ├── src/
│   │   ├── components/
│   │   │   ├── RouteMap.jsx       # Leaflet map with GeoJSON route lines & bus markers
│   │   │   ├── LiveOperationsTab.jsx
│   │   │   ├── HourlyBottlenecksTab.jsx
│   │   │   ├── ForecasterTab.jsx
│   │   │   └── OptimizationTab.jsx
│   │   ├── styles/
│   │   │   └── enterprise.css     # Enterprise light-theme design system
│   │   ├── App.jsx                # Main React app container with sticky header
│   │   └── main.jsx               # React DOM entry point
│   ├── package.json
│   └── vite.config.js             # Vite configuration with /api proxy
├── notebooks/                     # Guided exploration notebooks (01 to 05)
├── src/
│   ├── api.py                     # Main FastAPI application & static mount
│   ├── api_v2.py                  # V2 REST router powering the React platform
│   ├── live_feed.py               # CTA GTFS-RT & Bus Tracker stateful physics client
│   ├── features.py                # Cyclic temporal encodings and lag pipelines
│   ├── optimizer.py               # Dynamic headway optimization engine
│   └── models/
│       └── forecaster.py          # Multi-horizon direct LightGBM models
├── Dockerfile                     # Multi-stage Docker build (Node web build + Python)
├── render.yaml                    # Cloud deployment specification
└── requirements.txt               # Python package dependencies
```

---

## 👥 Branch Workflow & Contributing Guidelines

- ❌ Do **not** commit or push directly to `main`.
- ✅ All active development and commits must remain strictly on your personal branch (`users/bidhubhusan`).
- ✅ Keep pushing your branch regularly to reflect the latest deliverable.
