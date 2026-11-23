# 🚌 Powered Public Transit Route Optimization (Chicago CTA)

An intelligent, real-time-capable transit route optimization, headway rebalancing, and forecasting engine built on Chicago Transit Authority (CTA) data.

---

## 🌟 Project Highlights
- **Live Transit Tracking**: Real-time bus positions, speed, and schedule deviation via CTA GTFS-RT & Bus Tracker API.
- **Hourly Bottleneck Analysis**: GTFS scheduled capacity vs actual street speeds via Chicago Traffic Tracker.
- **Future-Hour Forecasting**: Multi-step delay and demand forecasting ($t+1$ to $t+24$ hours ahead) using LightGBM and Prophet.
- **Dynamic Headway Optimization**: Proactive frequency adjustments to alleviate bottlenecks before peak congestion hits.
- **Interactive Dashboard**: Streamlit interface with live maps, hourly metrics, and future-hour forecast slider.

---

## 🚀 Setup & Installation

```bash
# Clone the repository
git clone https://github.com/springboardmentor441p-coder/Powered-Public-Transit-Route-Optimization.git
cd Powered-Public-Transit-Route-Optimization

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🖥️ Running the Dashboard

```bash
streamlit run app/dashboard.py
```

---

## 👥 Contributing Guidelines (For Interns / Collaborators)

All interns added as collaborators to this repository must follow the branch workflow below. **Direct commits or pushes to the `main` branch are not allowed.**

> Note: `main` only contains the `LICENSE` and `README.md` — it is not used for active development. There is no need to pull the latest `main` into your branch at any point.

### 1. Branch Naming
- Every intern must create their own branch off `main`, named after themselves.
- Suggested naming convention: `firstname-lastname` or `users/firstname` (all lowercase, hyphen-separated).

### 2. Rules
- ❌ Do **not** push or upload code directly to `main`.
- ❌ Do **not** push code to another intern's branch.
- ✅ Only push/upload code to the branch that carries your own name.
- Keep uploading/pushing your code to your branch regularly as you make progress. No pull requests are required — your branch itself is the deliverable.
