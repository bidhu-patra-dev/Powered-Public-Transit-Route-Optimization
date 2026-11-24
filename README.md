# 🚌 CTA Public Transit Route Optimization & Predictive Intelligence Platform

An enterprise-grade, end-to-end Chicago Transit Authority (CTA) bus route intelligence, live operations, and autonomous dispatch platform.

Built with a modern **React 18 + Vite** single-page application (SPA), an interactive **Leaflet GeoJSON route network map**, and a high-throughput **FastAPI** Python backend powering machine learning and optimization engines.

```mermaid
flowchart TD
    subgraph Data Layer
        A1[CTA GTFS-RT Protobuf] --> B1[CTALiveTracker]
        A2[CTA Bus Tracker Developer API] --> B1
        A3[GTFS stop_times.txt] --> B2[Hourly Aggregator]
        A4[Chicago Traffic Tracker 1,250 Segments] --> B2
    end

    subgraph Machine Learning & Analytics
        B1 --> C1[Live Fleet Telemetry Stream]
        B2 --> C2[Unsupervised K-Means Route Clustering]
        B2 --> C3[Feature Engineering: Lags & Cyclic Encodings]
        C3 --> D1[Multi-Horizon Direct LightGBM Forecaster t+1 to t+24]
        D1 --> D2[Constrained Linear Headway Optimizer]
    end

    subgraph Enterprise API & Frontend
        C1 --> E1[FastAPI REST API /api/v2]
        C2 --> E1
        D1 --> E1
        D2 --> E1
        E1 --> F1[React 18 + Vite SPA]
        F1 --> G1[🗺️ Live Route Map with Line Polylines]
        F1 --> G2[⏱️ Hourly Bottleneck & Clustering Studio]
        F1 --> G3[🔮 24-Hour Predictive Forecaster]
        F1 --> G4[⚡ Dynamic Dispatch & Optimization]
    end
```

---

## 🌟 Core Pillars & Capabilities

### 1. 🗺️ Live Network Operations & Route Map
- **Official Developer API:** Connected directly to the author's registered **CTA Bus Tracker Developer API Key** and GTFS-Realtime streams.
- **Route Line Polylines:** Unlike isolated point markers, the interactive Leaflet map renders the **actual street line geometries** for each CTA bus route (e.g. Route 9 Ashland, Route 22 Clark, Route 66 Chicago, Route 49 Western, Route 79 79th, Route 8 Halsted, Route 126 Jackson, etc.) with custom transit color-coding.
- **Stateful Vehicle Fleet Physics:** Live buses advance continuously along coordinates based on elapsed time and real-time speeds, preventing erratic teleportation on refreshes.
- **Real-Time KPI Scorecard:** Instant visibility into active buses in service, mean arterial speed, on-time performance (OTP), and severe delay counts (>6m).

### 2. ⏱️ Hourly Bottlenecks & Unsupervised K-Means Route Clustering
- **Data Cross-Synthesis:** Fuses scheduled GTFS capacity with the **Chicago Traffic Tracker** speed sensor dataset across 1,250 arterial segments.
- **Diurnal Speed & Delay Curves:** Visualizes the sharp dip in street speed during morning (7–9 AM) and evening (4–7 PM) rush hours and corresponding delay spikes.
- **Unsupervised K-Means Route Clustering:** Clusters Chicago routes in a 4-dimensional operational feature space:
  $$\mathbf{x} = [\text{Mean Delay}, \text{Peak Delay}, \text{Scheduled Headway}, \text{Demand Score}]$$
  Discovers **3 operational route archetypes**:
  - 🔴 **Cluster 0: High-Demand Bottleneck Arterials (Ashland #9, Chicago #66):** Severe delay spikes + high volume. *Action:* Standby vehicle injection and proactive headway tightening.
  - 🟡 **Cluster 1: Moderate-Flow Commuter Corridors (Clark #22, Halsted #8):** Steady commuter flow. *Action:* Minor headway tuning (1–2 min tightening).
  - 🟢 **Cluster 2: Stable Low-Variance Crosstowns (79th #79, Jackson #126):** Predictable headways. *Action:* Maintain timetable; buffer capacity may be safely borrowed for emergencies.

### 3. 🔮 24-Hour Multi-Horizon Predictive Forecaster
- **LightGBM Regressors:** Specialized direct gradient boosting models predicting continuous transit delays from $t+1$ to $t+24$ hours ahead.
- **Representation Learning:** Cyclical sine/cosine encodings of temporal features, autoregressive lag vectors ($t-1, t-2, t-3, t-24$), and rolling window statistics.
- **Validation Metrics:** Strict chronological train/test partitions ensuring **zero data leakage**:
  - **Mean Absolute Error (MAE):** ~**1.06 minutes**
  - **Root Mean Squared Error (RMSE):** ~**1.43 minutes**
  - **Variance Explained ($R^2$):** ~**0.90**
- **Target Forecast Clock Window:** Dynamic digital clock badge updates as the horizon slider is adjusted.

### 4. ⚡ Dynamic Dispatch & Headway Optimization Engine
- **Constrained Linear Headway Optimizer:** Minimizes aggregate passenger wait time ($\approx \frac{\text{Headway}}{2} + \text{Delay}$) by dynamically tightening headways and allocating buffer fleet vehicles before congestion strikes.
- **Executive Impact:** Achieves **-28% to -35% reduction in passenger wait times** across monitored Chicago routes.
- **Actionable Dispatch Directives:** Clear operational commands for transit supervisors:
  - 🚨 **DISPATCH STANDBY BUS:** Injects standby buses from buffer fleet at route terminals.
  - ⏱️ **SHORTEN HEADWAY:** Rebalances active vehicles to shorten gaps.
  - ✅ **MAINTAIN TIMETABLE:** Confirms routes within optimal threshold tolerance.
- **1-Click CSV Export:** Generates downloadable dispatch schedules for ingestion into CAD/AVL systems.

---

## 🚀 Quickstart: Running the Application

### Prerequisites
- Python 3.10+
- Node.js 18+ (tested with Node 20 / 25)

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/springboardmentor441p-coderr/Powered-Public-Transit-Route-Optimization.git
cd Powered-Public-Transit-Route-Optimization

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
npm run build
cd ..
```

### 2. Launching the Platform

#### Production Mode (FastAPI serving built React SPA):
```bash
# From repository root with virtual environment activated:
uvicorn src.api:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser.

#### Development Mode (Vite HMR + FastAPI Backend):
```bash
# Terminal 1 (Backend API):
uvicorn src.api:app --reload --port 8000

# Terminal 2 (React Vite Dev Server):
cd frontend
npm run dev
```
Open **`http://localhost:5173`** for instant Hot Module Replacement (HMR).

#### Streamlit Interface (Optional Python Fallback):
```bash
streamlit run app/dashboard.py --server.port 8501
```

---

## 📁 Repository Structure

```
├── app/
│   └── dashboard.py               # Streamlit enterprise dashboard (light theme)
├── data/
│   ├── raw/                       # Source GTFS and traffic datasets
│   └── reference/
│       └── cta_bus_routes.geojson # 129 CTA Bus Route geometries (MultiLineString)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RouteMap.jsx       # Leaflet map with GeoJSON route lines & bus markers
│   │   │   ├── LiveOperationsTab.jsx
│   │   │   ├── HourlyBottlenecksTab.jsx
│   │   │   ├── ForecasterTab.jsx
│   │   │   └── OptimizationTab.jsx
│   │   ├── styles/
│   │   │   └── enterprise.css     # Enterprise SaaS light theme styles
│   │   ├── App.jsx                # Main React app container
│   │   └── main.jsx               # Entry point
│   ├── package.json
│   └── vite.config.js             # Vite configuration with /api proxy
├── notebooks/                     # Guided exploration notebooks (01 to 05)
├── src/
│   ├── api.py                     # Main FastAPI application
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

All collaborators must adhere strictly to branch rules:
- ❌ Do **not** commit or push directly to `main`.
- ✅ All active development and commits must remain strictly on your personal branch (`users/bidhubhusan`).
- ✅ Keep pushing your branch regularly to reflect the latest deliverable.
