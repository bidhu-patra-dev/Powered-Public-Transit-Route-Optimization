import React from "react";
import RouteMap from "./RouteMap";

export default function LiveOperationsTab({
  liveData,
  geojsonData,
  selectedRoute,
  onSelectRoute,
  onRefresh,
  loading,
}) {
  const summary = liveData?.summary || {
    active_buses: 0,
    avg_speed_mph: 0,
    on_time_pct: 0,
    severe_delays_count: 0,
  };
  const vehicles = liveData?.vehicles || [];
  const routeTelemetry = liveData?.route_telemetry || [];

  return (
    <div>
      {/* CTA Developer API Attribution Banner */}
      <div
        style={{
          background: "#F0FDF4",
          border: "1px solid #BBF7D0",
          borderLeft: "4px solid #16A34A",
          borderRadius: "10px",
          padding: "12px 18px",
          marginBottom: "20px",
          fontSize: "0.88rem",
          color: "#166534",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <div>
          <strong>🟢 Live Telemetry Stream:</strong> Powered by the author's registered{" "}
          <strong>CTA Bus Tracker Developer API Key</strong> & GTFS-Realtime streams, broadcasting
          ground-truth bus GPS coordinates, speeds, and schedule adherence along official CTA line geometry.
        </div>
        <button
          className="btn-outline"
          onClick={onRefresh}
          disabled={loading}
          style={{ padding: "6px 12px", fontSize: "0.8rem", background: "#FFFFFF" }}
        >
          {loading ? "Syncing..." : "🔄 Sync Telemetry"}
        </button>
      </div>

      {/* Real-time KPI Scorecard */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Active Fleet in Service</div>
          <div className="kpi-value" style={{ color: "#0072CE" }}>
            {summary.active_buses}
          </div>
          <div className="kpi-subtext">Buses reporting real-time telemetry</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Average Fleet Speed</div>
          <div className="kpi-value">
            {summary.avg_speed_mph} <span style={{ fontSize: "1rem", fontWeight: 500 }}>mph</span>
          </div>
          <div className="kpi-subtext">Chicago arterial free-flow: 22 mph</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">On-Time Performance (OTP)</div>
          <div className="kpi-value" style={{ color: summary.on_time_pct >= 70 ? "#10B981" : "#F59E0B" }}>
            {summary.on_time_pct}%
          </div>
          <div className="kpi-subtext">Tracking within ≤ 2 mins of schedule</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Severe Bottlenecks</div>
          <div className="kpi-value" style={{ color: summary.severe_delays_count > 0 ? "#EF4444" : "#10B981" }}>
            {summary.severe_delays_count}
          </div>
          <div className="kpi-subtext">Vehicles with delay &gt; 6 mins</div>
        </div>
      </div>

      {/* 70/30 Map and Telemetry Stream Layout */}
      <div className="section-card">
        <div className="section-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2 className="section-title">🗺️ Live Chicago Transit Map (Route Polylines & Fleet GPS)</h2>
            <p className="section-subtitle">
              Displaying exact route polyline street connections and moving vehicles along active Chicago transit routes.
            </p>
          </div>
          {selectedRoute && (
            <button
              className="btn-outline"
              onClick={() => onSelectRoute(null)}
              style={{ fontSize: "0.78rem", padding: "4px 10px" }}
            >
              Reset to All Routes
            </button>
          )}
        </div>

        <div className="map-split-layout">
          {/* Left: Leaflet Route Map */}
          <div>
            <RouteMap
              geojsonData={geojsonData}
              vehicles={vehicles}
              selectedRoute={selectedRoute}
              onSelectRoute={onSelectRoute}
            />
            <div style={{ marginTop: "8px", fontSize: "0.78rem", color: "#64748B", display: "flex", gap: "16px" }}>
              <span>🟢 <strong>On-Time:</strong> ≤ 2 min</span>
              <span>🟡 <strong>Minor Delay:</strong> 2–6 min</span>
              <span>🔴 <strong>Severe Bottleneck:</strong> &gt; 6 min</span>
              <span style={{ marginLeft: "auto" }}>💡 Click any route line or bus marker to inspect details.</span>
            </div>
          </div>

          {/* Right: Live Route Telemetry Stream */}
          <div className="telemetry-stream">
            <div className="telemetry-header">
              📊 Live Route Telemetry Stream ({routeTelemetry.length} Routes)
            </div>
            <div className="telemetry-list">
              {routeTelemetry.map((rt) => {
                const isSelected = selectedRoute === rt.route;
                return (
                  <div
                    key={rt.route}
                    className="telemetry-item"
                    style={{
                      borderLeft: `4px solid ${rt.color || "#0072CE"}`,
                      background: isSelected ? "#F0F7FF" : "#FFFFFF",
                      cursor: "pointer",
                    }}
                    onClick={() => onSelectRoute(isSelected ? null : rt.route)}
                  >
                    <div className="telemetry-item-top">
                      <span className="route-tag">
                        <span className="route-tag-circle" style={{ background: rt.color || "#0072CE" }}></span>
                        {rt.display_name}
                      </span>
                      <span
                        className={`badge-status ${
                          rt.avg_delay <= 2.5
                            ? "badge-green"
                            : rt.avg_delay <= 5.0
                            ? "badge-amber"
                            : "badge-red"
                        }`}
                      >
                        {rt.avg_delay <= 2.5 ? "On-Time" : rt.avg_delay <= 5.0 ? "Moderate" : "Bottleneck"}
                      </span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "#64748B", marginTop: "4px" }}>
                      <span>Active Buses: <strong>{rt.active_buses}</strong></span>
                      <span>Speed: <strong>{rt.avg_speed} mph</strong></span>
                      <span>Delay: <strong style={{ color: rt.avg_delay > 5 ? "#EF4444" : "#0F172A" }}>{rt.avg_delay}m</strong></span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
