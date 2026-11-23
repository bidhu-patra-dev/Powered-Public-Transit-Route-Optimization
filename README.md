# 🚌 CTA Public Transit Route Optimization

RouteRanker & Transit AI is an end-to-end Chicago Transit Authority (CTA) bus-demand exploration, real-time operations, and intelligent dispatch platform.

It combines:
1. **Live Network Operations:** Real-time bus GPS tracking, live arterial speeds, and schedule deviation alerts via CTA GTFS-RT & Bus Tracker feeds.
2. **Hourly Bottleneck Studio:** Scheduled GTFS timetables synthesized with the Chicago Traffic Tracker across 1,250 arterial road segments.
3. **24-Hour AI Forecaster:** Multi-horizon gradient boosted models predicting arrival delays and passenger congestion up to 24 hours in advance.
4. **Dynamic Headway Optimizer:** Autonomous dispatch recommendations (standby vehicle injection, headway shortening) reducing passenger wait times by ~28–35%.
5. **Retrospective Route Planning:** Route-level ridership evidence, mentor v3 model evaluations, and bounded trip-allocation scenarios.

---

## 🚀 Running the Streamlit Dashboard

To launch the real-time operations interface:

```bash
cd /Users/bidhubhusanpatra/Documents/Powered-Public-Transit-Route-Optimization
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the dashboard
streamlit run app/dashboard.py
```
View the dashboard in your browser at `http://localhost:8501`.

---

## 📓 Guided Notebook Workflows

- **`notebooks/01_data_ingestion_and_live_stream.ipynb`**: CTA GTFS static ingestion & live telemetry logging.
- **`notebooks/02_hourly_eda_and_traffic_analysis.ipynb`**: Arterial speed degradation and diurnal delay profiling.
- **`notebooks/04_future_hour_forecasting_models.ipynb`**: Training multi-horizon LightGBM regressors with cyclic and lag features.
- **`notebooks/05_dynamic_route_optimization.ipynb`**: Proactive headway rebalancing and passenger wait-time impact modeling.
- **`notebooks/cta_ridership_colab.ipynb`**: Colab workflow following the mentor's v3 evaluation guide.

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
