import React, { useState, useEffect, useCallback } from "react";
import LiveOperationsTab from "./components/LiveOperationsTab";
import HourlyBottlenecksTab from "./components/HourlyBottlenecksTab";
import ForecasterTab from "./components/ForecasterTab";
import OptimizationTab from "./components/OptimizationTab";

export default function App() {
  const [activeTab, setActiveTab] = useState("live");
  const [routesList, setRoutesList] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [geojsonData, setGeojsonData] = useState(null);

  // Module data states
  const [liveData, setLiveData] = useState(null);
  const [hourlyData, setHourlyData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [optimizationData, setOptimizationData] = useState(null);

  // Forecaster & Optimizer horizon
  const [horizon, setHorizon] = useState(3);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());

  // 1. Fetch available routes and base GeoJSON
  useEffect(() => {
    fetch("/api/v2/routes")
      .then((res) => res.json())
      .then((data) => setRoutesList(data.routes || []))
      .catch((err) => console.error("Error fetching routes:", err));

    fetch("/api/v2/routes/geojson")
      .then((res) => res.json())
      .then((data) => setGeojsonData(data))
      .catch((err) => console.error("Error fetching GeoJSON:", err));
  }, []);

  // 2. Fetch live vehicle telemetry
  const fetchLiveTelemetry = useCallback(() => {
    setLoading(true);
    const url = selectedRoute
      ? `/api/v2/live?routes=${selectedRoute}`
      : "/api/v2/live";

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        setLiveData(data);
        setLastUpdated(new Date().toLocaleTimeString());
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching live telemetry:", err);
        setLoading(false);
      });
  }, [selectedRoute]);

  // Auto-sync live feed every 15 seconds
  useEffect(() => {
    fetchLiveTelemetry();
    const interval = setInterval(fetchLiveTelemetry, 15000);
    return () => clearInterval(interval);
  }, [fetchLiveTelemetry]);

  // 3. Fetch hourly bottlenecks when tab is active or route filter changes
  useEffect(() => {
    if (activeTab === "hourly") {
      const url = selectedRoute
        ? `/api/v2/hourly-bottlenecks?routes=${selectedRoute}`
        : "/api/v2/hourly-bottlenecks";
      fetch(url)
        .then((res) => res.json())
        .then((data) => setHourlyData(data))
        .catch((err) => console.error("Error fetching hourly bottlenecks:", err));
    }
  }, [activeTab, selectedRoute]);

  // 4. Fetch 24h forecasting predictions when horizon or tab changes
  useEffect(() => {
    if (activeTab === "forecaster") {
      const url = selectedRoute
        ? `/api/v2/forecast?horizon=${horizon}&routes=${selectedRoute}`
        : `/api/v2/forecast?horizon=${horizon}`;
      fetch(url)
        .then((res) => res.json())
        .then((data) => setForecastData(data))
        .catch((err) => console.error("Error fetching forecast:", err));
    }
  }, [activeTab, horizon, selectedRoute]);

  // 5. Fetch dynamic headway optimization when horizon or tab changes
  useEffect(() => {
    if (activeTab === "optimization") {
      const url = selectedRoute
        ? `/api/v2/optimize?horizon=${horizon}&routes=${selectedRoute}`
        : `/api/v2/optimize?horizon=${horizon}`;
      fetch(url)
        .then((res) => res.json())
        .then((data) => setOptimizationData(data))
        .catch((err) => console.error("Error fetching optimization:", err));
    }
  }, [activeTab, horizon, selectedRoute]);

  return (
    <div>
      {/* Enterprise Header */}
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-icon">🚌</div>
          <div>
            <h1 className="brand-title">CTA Transit AI · Route Intelligence Platform</h1>
            <p className="brand-subtitle">
              Real-Time Vehicle Telemetry • Hourly Traffic Analysis • LightGBM Forecaster • Dynamic Headway Optimization
            </p>
          </div>
        </div>

        <div className="header-meta">
          <div className="api-badge">
            <span className="dot"></span>
            CTA DEVELOPER API ACTIVE
          </div>
          <span style={{ fontSize: "0.82rem", color: "#64748B", borderLeft: "1px solid #CBD5E1", paddingLeft: "12px" }}>
            {lastUpdated} CST
          </span>
        </div>
      </header>

      {/* Modern Tabbed Navigation */}
      <nav className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === "live" ? "active" : ""}`}
          onClick={() => setActiveTab("live")}
        >
          🗺️ Live Network Operations
        </button>
        <button
          className={`tab-btn ${activeTab === "hourly" ? "active" : ""}`}
          onClick={() => setActiveTab("hourly")}
        >
          ⏱️ Hourly Bottlenecks & Speed
        </button>
        <button
          className={`tab-btn ${activeTab === "forecaster" ? "active" : ""}`}
          onClick={() => setActiveTab("forecaster")}
        >
          🔮 24-Hour Predictive Forecaster
        </button>
        <button
          className={`tab-btn ${activeTab === "optimization" ? "active" : ""}`}
          onClick={() => setActiveTab("optimization")}
        >
          ⚡ Dynamic Dispatch & Optimization
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Global Route Selection Bar */}
        <div className="route-filter-bar">
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "#475569" }}>
              Filter by CTA Route:
            </span>
            <div className="filter-pills">
              <button
                className={`route-pill ${selectedRoute === null ? "active" : ""}`}
                onClick={() => setSelectedRoute(null)}
              >
                🌐 All Routes (10)
              </button>
              {routesList.map((rt) => (
                <button
                  key={rt.route}
                  className={`route-pill ${selectedRoute === rt.route ? "active" : ""}`}
                  style={
                    selectedRoute === rt.route
                      ? { background: rt.color || "#0072CE", borderColor: rt.color || "#0072CE" }
                      : {}
                  }
                  onClick={() => setSelectedRoute(rt.route)}
                >
                  {rt.display_name}
                </button>
              ))}
            </div>
          </div>

          {selectedRoute && (
            <button
              className="btn-outline"
              style={{ fontSize: "0.78rem", padding: "4px 8px" }}
              onClick={() => setSelectedRoute(null)}
            >
              Clear Route Filter
            </button>
          )}
        </div>

        {/* Tab 1: Live Network Operations */}
        {activeTab === "live" && (
          <LiveOperationsTab
            liveData={liveData}
            geojsonData={geojsonData}
            selectedRoute={selectedRoute}
            onSelectRoute={setSelectedRoute}
            onRefresh={fetchLiveTelemetry}
            loading={loading}
          />
        )}

        {/* Tab 2: Hourly Bottlenecks & K-Means ML Clustering */}
        {activeTab === "hourly" && <HourlyBottlenecksTab hourlyData={hourlyData} />}

        {/* Tab 3: 24-Hour Predictive Forecaster */}
        {activeTab === "forecaster" && (
          <ForecasterTab
            forecastData={forecastData}
            horizon={horizon}
            onHorizonChange={setHorizon}
            loading={loading}
          />
        )}

        {/* Tab 4: Dynamic Dispatch & Optimization */}
        {activeTab === "optimization" && (
          <OptimizationTab
            optimizationData={optimizationData}
            horizon={horizon}
            onHorizonChange={setHorizon}
            loading={loading}
          />
        )}
      </main>
    </div>
  );
}
