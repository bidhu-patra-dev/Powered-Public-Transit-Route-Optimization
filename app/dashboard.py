"""
Streamlit Web Dashboard for CTA Transit Optimization:
Features:
1. Live Transit Map & Real-time Vehicle Tracking (CTA Bus Tracker / GTFS-RT)
2. Hourly Capacity, Speed & Bottleneck Analysis (GTFS + Chicago Traffic Tracker)
3. Future-Hour Forecasting (LightGBM Multi-Horizon Delay & Demand Predictions)
4. Dynamic Route & Headway Optimization (Proactive Wait Time Reduction)
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.live_feed import CTALiveTracker
from src.features import generate_synthetic_hourly_history, create_forecasting_features
from src.models.forecaster import FutureHourTransitForecaster
from src.optimizer import DynamicRouteOptimizer

st.set_page_config(
    page_title="Chicago CTA Transit Optimizer",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚌 Chicago Transit Authority (CTA) Route Optimizer & Forecaster")
st.markdown(
    "**End-to-End Transit Intelligence:** Live GPS tracking, hourly congestion analytics, "
    "future-hour ML delay forecasting, and proactive headway rebalancing."
)

# Sidebar controls
st.sidebar.markdown("## 🚌 **CTA Transit AI**")
st.sidebar.header("Navigation & Settings")
page = st.sidebar.radio(
    "Go to Module:",
    [
        "🔴 Live Transit Tracking",
        "⏱️ Hourly Bottleneck Analysis",
        "🔮 Future-Hour Forecasting",
        "⚡ Dynamic Headway Optimization"
    ]
)

ALL_ROUTES = ["22", "9", "66", "49", "79", "3", "4", "8", "60", "126"]

selected_routes = st.sidebar.multiselect(
    "Filter Corridors:",
    options=ALL_ROUTES,
    default=["22", "9", "66", "49", "79"]
)

# Robust fallback: if user clears the filter, default gracefully to all corridors
active_corridors = selected_routes if (selected_routes and len(selected_routes) > 0) else ALL_ROUTES
if not selected_routes:
    st.sidebar.caption("ℹ️ Showing all corridors by default.")

# Shared data caches
@st.cache_data(ttl=10)
def get_live_data(routes):
    tracker = CTALiveTracker()
    return tracker.get_live_vehicles(routes=routes)

@st.cache_data(ttl=3600)
def get_historical_hourly_data():
    raw = generate_synthetic_hourly_history(num_days=30)
    return raw

@st.cache_resource
def get_trained_forecaster():
    raw = get_historical_hourly_data()
    feats = create_forecasting_features(raw)
    forecaster = FutureHourTransitForecaster(target_col="delay_min")
    forecaster.train_multi_horizon_models(feats, horizons=[1, 2, 3, 6, 12, 24])
    return forecaster, feats

# -------------------------------------------------------------------------------------------------
# PAGE 1: LIVE TRANSIT TRACKING
# -------------------------------------------------------------------------------------------------
if page == "🔴 Live Transit Tracking":
    st.subheader("🔴 Live Vehicle Tracking & Schedule Adherence (GTFS-RT / Bus Tracker)")
    
    col_refresh, col_snap = st.columns([1, 4])
    if col_refresh.button("🔄 Refresh Live Feed"):
        st.cache_data.clear()

    df_live = get_live_data(active_corridors)
    
    # Summary KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_vehicles = len(df_live)
    avg_speed = df_live["spd"].mean() if not df_live.empty else 0
    delayed_buses = (df_live["delay_status"] != "ON_TIME").sum() if not df_live.empty else 0
    major_delayed = (df_live["delay_status"] == "MAJOR_DELAY").sum() if not df_live.empty else 0

    kpi1.metric("Active Buses in Service", f"{total_vehicles}")
    kpi2.metric("Average Fleet Speed", f"{avg_speed:.1f} mph")
    kpi3.metric("Delayed Vehicles (>2m)", f"{delayed_buses}", delta=f"{delayed_buses/max(1,total_vehicles)*100:.0f}% of fleet", delta_color="inverse")
    kpi4.metric("Severe Delays (>7m)", f"{major_delayed}", delta_color="inverse")

    st.markdown("### Live Chicago Transit Map")
    if not df_live.empty:
        # Color mapping for delay status
        color_map = {
            "ON_TIME": "#2ecc71",     # green
            "MINOR_DELAY": "#f39c12", # orange
            "MAJOR_DELAY": "#e74c3c"  # red
        }
        # Use px.scatter_map (Plotly v6+) or fallback to px.scatter_mapbox
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_live,
                lat="lat",
                lon="lon",
                color="delay_status",
                color_discrete_map=color_map,
                size=[12]*len(df_live),
                hover_name="vid",
                hover_data={
                    "rt": True,
                    "spd": ":.1f mph",
                    "delay_min": ":.1f min",
                    "delay_status": True,
                    "lat": False,
                    "lon": False
                },
                zoom=10.5,
                center={"lat": 41.8781, "lon": -87.66},
                map_style="carto-positron",
                title="Real-Time Bus GPS Locations & Delay Status"
            )
        else:
            fig_map = px.scatter_mapbox(
                df_live,
                lat="lat",
                lon="lon",
                color="delay_status",
                color_discrete_map=color_map,
                size=[12]*len(df_live),
                hover_name="vid",
                hover_data={
                    "rt": True,
                    "spd": ":.1f mph",
                    "delay_min": ":.1f min",
                    "delay_status": True,
                    "lat": False,
                    "lon": False
                },
                zoom=10.5,
                center={"lat": 41.8781, "lon": -87.66},
                mapbox_style="carto-positron",
                title="Real-Time Bus GPS Locations & Delay Status"
            )
        fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=550)
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("### Live Fleet Telemetry Table")
        st.dataframe(
            df_live[["vid", "rt", "spd", "delay_min", "delay_status", "lat", "lon", "tmstmp"]]
            .rename(columns={
                "vid": "Vehicle ID",
                "rt": "Route #",
                "spd": "Speed (mph)",
                "delay_min": "Delay (mins)",
                "delay_status": "Status",
                "tmstmp": "Last Ping"
            }),
            use_container_width=True
        )

# -------------------------------------------------------------------------------------------------
# PAGE 2: HOURLY BOTTLENECK ANALYSIS
# -------------------------------------------------------------------------------------------------
elif page == "⏱️ Hourly Bottleneck Analysis":
    st.subheader("⏱️ Hourly Transit Bottlenecks & Speed Degradation")
    st.markdown("Combines GTFS scheduled capacity and Chicago Traffic Tracker speed sensors.")

    df_hist = get_historical_hourly_data()
    df_filtered = df_hist[df_hist["route"].isin(active_corridors)]

    # Hourly aggregations
    hourly_agg = df_filtered.groupby("hour").agg({
        "avg_speed_mph": "mean",
        "delay_min": "mean",
        "scheduled_trips": "mean",
        "demand_index": "mean"
    }).reset_index()

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_speed = go.Figure()
        fig_speed.add_trace(go.Scatter(
            x=hourly_agg["hour"],
            y=hourly_agg["avg_speed_mph"],
            mode="lines+markers",
            name="Traffic Speed (mph)",
            line=dict(color="#3498db", width=3)
        ))
        fig_speed.add_trace(go.Bar(
            x=hourly_agg["hour"],
            y=hourly_agg["delay_min"],
            name="Avg Delay (mins)",
            marker_color="#e74c3c",
            opacity=0.6,
            yaxis="y2"
        ))
        fig_speed.update_layout(
            title="Arterial Street Speed vs Transit Delay by Hour",
            xaxis=dict(title="Hour of Day (0–23)", tickmode="linear", dtick=2),
            yaxis=dict(title="Speed (mph)", side="left"),
            yaxis2=dict(title="Delay (minutes)", overlaying="y", side="right"),
            legend=dict(x=0.05, y=0.95),
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_speed, use_container_width=True)

    with col_chart2:
        fig_demand = px.line(
            df_filtered.groupby(["hour", "route"])["delay_min"].mean().reset_index(),
            x="hour",
            y="delay_min",
            color="route",
            title="Hourly Delay Breakdown Across Corridors",
            labels={"hour": "Hour of Day", "delay_min": "Average Delay (mins)"},
            template="plotly_white"
        )
        fig_demand.update_layout(height=420, template="plotly_white")
        st.plotly_chart(fig_demand, use_container_width=True)

    st.markdown("### Peak vs Off-Peak Headway Regularity")
    headway_table = df_filtered.groupby("route").agg({
        "scheduled_headway_min": "mean",
        "delay_min": ["mean", "max"],
        "demand_index": "mean"
    }).round(1)
    headway_table.columns = ["Scheduled Headway (min)", "Avg Delay (min)", "Max Delay (min)", "Hourly Demand Index"]
    st.dataframe(headway_table, use_container_width=True)

# -------------------------------------------------------------------------------------------------
# PAGE 3: FUTURE-HOUR FORECASTING
# -------------------------------------------------------------------------------------------------
elif page == "🔮 Future-Hour Forecasting":
    st.subheader("🔮 Multi-Step Future-Hour Transit Delay & Demand Forecaster")
    st.markdown(
        "Predicts transit delays for upcoming hours ($t+1$ to $t+24$) using multi-horizon LightGBM regressors "
        "trained on lag states, rolling statistics, and cyclic time encodings."
    )

    with st.spinner("Loading forecasting models..."):
        forecaster, feats = get_trained_forecaster()

    horizon_slider = st.slider("Select Forecast Horizon (Hours Ahead):", min_value=1, max_value=24, value=3, step=1)
    
    # Display model evaluation metrics across horizons
    st.markdown("### Model Forecast Accuracy Degradation Across Horizons")
    metrics_list = []
    for h, m in forecaster.evaluation_metrics.items():
        metrics_list.append({
            "Horizon": f"+{h} Hour(s) Ahead",
            "MAE (mins)": m["MAE"],
            "RMSE (mins)": m["RMSE"],
            "R² Score": m["R2"]
        })
    st.dataframe(pd.DataFrame(metrics_list), use_container_width=True)

    # Predict current state across selected routes
    st.markdown(f"### Predicted Route Delays for +{horizon_slider} Hour(s) Ahead")
    # Take latest state of each route
    latest_state = feats.sort_values("timestamp").groupby("route").last().reset_index()
    latest_state = latest_state[latest_state["route"].isin(active_corridors)]

    # Generate predictions
    closest_h = min([1, 2, 3, 6, 12, 24], key=lambda x: abs(x - horizon_slider))
    pred_df = forecaster.predict_future_hours(latest_state, horizons=[closest_h])

    if not pred_df.empty:
        fig_pred = px.bar(
            pred_df,
            x="route",
            y="forecasted_delay_min",
            color="forecasted_delay_min",
            color_continuous_scale="Reds",
            title=f"Forecasted Delay (mins) for Horizon +{closest_h}h",
            labels={"forecasted_delay_min": "Forecasted Delay (mins)", "route": "CTA Route"},
            template="plotly_white"
        )
        fig_pred.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig_pred, use_container_width=True)
    else:
        st.info("No route predictions available for the selected corridor filter.")

# -------------------------------------------------------------------------------------------------
# PAGE 4: DYNAMIC HEADWAY OPTIMIZATION
# -------------------------------------------------------------------------------------------------
elif page == "⚡ Dynamic Headway Optimization":
    st.subheader("⚡ Dynamic Route & Headway Optimization Engine")
    st.markdown(
        "Proactively rebalances transit headway before predicted delays hit. "
        "Shortens headways on bottleneck corridors to prevent passenger backlog and bus bunching."
    )

    forecaster, feats = get_trained_forecaster()
    latest_state = feats.sort_values("timestamp").groupby("route").last().reset_index()
    latest_state = latest_state[latest_state["route"].isin(active_corridors)]

    # Get predictions for next hour (t+1)
    preds = forecaster.predict_future_hours(latest_state, horizons=[1])

    sched_df = latest_state[["route", "scheduled_headway_min", "scheduled_trips", "demand_index"]].copy()
    optimizer = DynamicRouteOptimizer()
    optimized_plan = optimizer.optimize_headways(sched_df, preds)

    # Optimization KPIs
    total_wait_saved = optimized_plan["wait_time_saved_min"].sum()
    avg_pct_reduction = optimized_plan["pct_wait_reduction"].mean()

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric("Average Wait Time Reduction", f"{avg_pct_reduction:.1f}%")
    col_kpi2.metric("Cumulative Wait Savings", f"{total_wait_saved:.1f} mins / passenger")
    col_kpi3.metric("Critical Interventions", f"{(optimized_plan['wait_time_saved_min'] >= 2.0).sum()} Corridors")

    st.markdown("### Proactive Dispatch & Headway Rebalancing Plan")
    st.dataframe(
        optimized_plan[[
            "route",
            "scheduled_headway_min",
            "optimized_headway_min",
            "baseline_avg_wait_min",
            "optimized_avg_wait_min",
            "wait_time_saved_min",
            "pct_wait_reduction",
            "action"
        ]].rename(columns={
            "route": "Route",
            "scheduled_headway_min": "Scheduled Headway (min)",
            "optimized_headway_min": "Optimized Headway (min)",
            "baseline_avg_wait_min": "Baseline Wait (min)",
            "optimized_avg_wait_min": "Optimized Wait (min)",
            "wait_time_saved_min": "Saved Wait (min)",
            "pct_wait_reduction": "Wait Reduction (%)",
            "action": "Recommended Action"
        }),
        use_container_width=True
    )

    fig_comp = go.Figure(data=[
        go.Bar(name="Baseline Wait Time", x=optimized_plan["route"], y=optimized_plan["baseline_avg_wait_min"], marker_color="#e74c3c"),
        go.Bar(name="Optimized Wait Time", x=optimized_plan["route"], y=optimized_plan["optimized_avg_wait_min"], marker_color="#2ecc71")
    ])
    fig_comp.update_layout(
        barmode="group",
        title="Passenger Wait Time Comparison: Baseline Timetable vs Proactive Dynamic Headways",
        yaxis_title="Average Wait Time (mins)",
        xaxis_title="CTA Route",
        template="plotly_white",
        height=420
    )
    st.plotly_chart(fig_comp, use_container_width=True)
