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
      {/* Unified Sticky Header with Navigation Tabs */}
      <header className="top-nav-wrapper">
        <div className="top-nav-bar">
          <div className="brand-section">
            <div className="brand-badge-icon">🚌</div>
            <div>
              <h1 className="brand-headline">Chicago Transit AI · Route Intelligence Platform</h1>
              <p className="brand-tagline">
                Real-Time Vehicle Telemetry • Hourly Traffic Tracker • Multi-Horizon LightGBM Forecaster • Headway Optimization
              </p>
            </div>
          </div>

          <div className="top-nav-meta">
            <div className="developer-api-badge">
              <span className="pulsing-green-dot"></span>
              CTA DEVELOPER API ACTIVE
            </div>
            <div className="clock-timestamp">{lastUpdated} CST</div>
          </div>
        </div>

        {/* Top Navigation Tabs (Permanently Sticky) */}
        <nav className="sub-nav-tabs">
          <button
            className={`nav-tab-button ${activeTab === "live" ? "active" : ""}`}
            onClick={() => setActiveTab("live")}
          >
            🗺️ Live Network Operations
          </button>
          <button
            className={`nav-tab-button ${activeTab === "hourly" ? "active" : ""}`}
            onClick={() => setActiveTab("hourly")}
          >
            ⏱️ Hourly Bottlenecks & Speed
          </button>
          <button
            className={`nav-tab-button ${activeTab === "forecaster" ? "active" : ""}`}
            onClick={() => setActiveTab("forecaster")}
          >
            🔮 24-Hour Predictive Forecaster
          </button>
          <button
            className={`nav-tab-button ${activeTab === "optimization" ? "active" : ""}`}
            onClick={() => setActiveTab("optimization")}
          >
            ⚡ Dynamic Dispatch & Optimization
          </button>
        </nav>
      </header>

      {/* Main Page Container */}
      <main className="app-container">
        {/* Prominent Route Selection Toolbar */}
        <div className="route-control-card">
          <div className="route-control-header">
            <div className="route-control-label">
              <span>📍 Select CTA Bus Route:</span>
              {selectedRoute && (
                <span style={{ fontSize: "0.82rem", color: "#64748B", fontWeight: 500 }}>
                  (Filtering to Route {selectedRoute})
                </span>
              )}
            </div>

            <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
              {selectedRoute && (
                <button
                  className="btn-action-outline"
                  style={{ height: "38px", fontSize: "0.84rem", padding: "0 14px" }}
                  onClick={() => setSelectedRoute(null)}
                >
                  ✕ Show All Routes
                </button>
              )}
              <button
                className="btn-action-primary"
                style={{ height: "38px", fontSize: "0.84rem", padding: "0 16px" }}
                onClick={fetchLiveTelemetry}
                disabled={loading}
              >
                {loading ? "Syncing..." : "🔄 Sync Live Telemetry"}
              </button>
            </div>
          </div>

          <div className="route-chips-grid">
            <button
              className={`route-chip ${selectedRoute === null ? "active" : ""}`}
              onClick={() => setSelectedRoute(null)}
            >
              🌐 All Core Routes ({routesList.length || 10})
            </button>

            {routesList.map((rt) => {
              const isSelected = selectedRoute === rt.route;
              return (
                <button
                  key={rt.route}
                  className={`route-chip ${isSelected ? "active" : ""}`}
                  style={
                    isSelected
                      ? { background: rt.color || "#0072CE", borderColor: rt.color || "#0072CE" }
                      : {}
                  }
                  onClick={() => setSelectedRoute(isSelected ? null : rt.route)}
                >
                  <span
                    className="route-chip-num"
                    style={
                      !isSelected
                        ? { border: `1.5px solid ${rt.color || "#0072CE"}`, color: rt.color || "#0072CE" }
                        : {}
                    }
                  >
                    {rt.route}
                  </span>
                  <span>{rt.name}</span>
                </button>
              );
            })}
          </div>
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
