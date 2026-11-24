import React, { useState } from "react";

export default function HourlyBottlenecksTab({ hourlyData }) {
  const [activeWindow, setActiveWindow] = useState("all");

  const diurnal = hourlyData?.diurnal_series || [];
  const leaderboard = hourlyData?.leaderboard || [];
  const clustering = hourlyData?.clustering || { scatter_points: [], archetypes: [] };

  // Filter diurnal points if rush hour window selected
  const displayDiurnal = diurnal.filter((d) => {
    if (activeWindow === "morning") return d.hour >= 6 && d.hour <= 10;
    if (activeWindow === "evening") return d.hour >= 15 && d.hour <= 19;
    return true;
  });

  return (
    <div>
      {/* Overview Card */}
      <div className="section-card">
        <div className="section-header">
          <h2 className="section-title">⏱️ Hourly Bottleneck & Municipal Speed Sensor Analysis</h2>
          <p className="section-subtitle">
            Combines scheduled departures from CTA GTFS <code>stop_times.txt</code> with ground-truth arterial speeds from the{" "}
            <strong>Chicago Traffic Tracker</strong> across 1,250 road segments.
          </p>
        </div>

        {/* Time Window Selector Pills */}
        <div style={{ display: "flex", gap: "8px", marginBottom: "18px" }}>
          <button
            className={`route-pill ${activeWindow === "all" ? "active" : ""}`}
            onClick={() => setActiveWindow("all")}
          >
            🕒 Full 24-Hour Cycle
          </button>
          <button
            className={`route-pill ${activeWindow === "morning" ? "active" : ""}`}
            onClick={() => setActiveWindow("morning")}
          >
            🌅 Morning Rush (7–9 AM)
          </button>
          <button
            className={`route-pill ${activeWindow === "evening" ? "active" : ""}`}
            onClick={() => setActiveWindow("evening")}
          >
            🌆 Evening Rush (4–7 PM)
          </button>
        </div>

        {/* Diurnal Speed vs. Delay SVG Chart */}
        <div style={{ background: "#F8FAFC", border: "1px solid #E2E8F0", borderRadius: "10px", padding: "18px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#0F172A" }}>
              Arterial Speed (mph) vs. Transit Delay (min) by Hour
            </span>
            <div style={{ display: "flex", gap: "16px", fontSize: "0.78rem" }}>
              <span style={{ color: "#0072CE", fontWeight: 600 }}>● Arterial Street Speed (mph)</span>
              <span style={{ color: "#EF4444", fontWeight: 600 }}>■ Average Transit Delay (min)</span>
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <svg viewBox="0 0 900 220" style={{ width: "100%", height: "220px", overflow: "visible" }}>
              {/* Grid Lines */}
              <line x1="50" y1="20" x2="880" y2="20" stroke="#E2E8F0" strokeDasharray="3,3" />
              <line x1="50" y1="70" x2="880" y2="70" stroke="#E2E8F0" strokeDasharray="3,3" />
              <line x1="50" y1="120" x2="880" y2="120" stroke="#E2E8F0" strokeDasharray="3,3" />
              <line x1="50" y1="170" x2="880" y2="170" stroke="#CBD5E1" />

              {/* Y Axis Labels */}
              <text x="40" y="24" fontSize="10" fill="#64748B" textAnchor="end">20 mph / 10m</text>
              <text x="40" y="74" fontSize="10" fill="#64748B" textAnchor="end">15 mph / 6m</text>
              <text x="40" y="124" fontSize="10" fill="#64748B" textAnchor="end">10 mph / 3m</text>
              <text x="40" y="174" fontSize="10" fill="#64748B" textAnchor="end">0</text>

              {/* Bars for Delay */}
              {displayDiurnal.map((d, idx) => {
                const total = displayDiurnal.length;
                const slotWidth = (880 - 50) / total;
                const x = 50 + idx * slotWidth + slotWidth * 0.2;
                const barW = slotWidth * 0.6;
                const barH = Math.min(150, (d.delay_min / 10) * 150);
                const y = 170 - barH;

                return (
                  <g key={`bar-${d.hour}`}>
                    <rect
                      x={x}
                      y={y}
                      width={barW}
                      height={barH}
                      fill="#EF4444"
                      opacity="0.85"
                      rx="3"
                    />
                    <text
                      x={x + barW / 2}
                      y="190"
                      fontSize="9"
                      fill="#64748B"
                      textAnchor="middle"
                    >
                      {d.time_label.replace(" ", "")}
                    </text>
                  </g>
                );
              })}

              {/* Line for Speed */}
              {displayDiurnal.length > 1 && (
                <polyline
                  fill="none"
                  stroke="#0072CE"
                  strokeWidth="3"
                  points={displayDiurnal
                    .map((d, idx) => {
                      const total = displayDiurnal.length;
                      const slotWidth = (880 - 50) / total;
                      const x = 50 + idx * slotWidth + slotWidth * 0.5;
                      const y = 170 - Math.min(150, (d.speed_mph / 22) * 150);
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
              )}

              {/* Points on Speed Line */}
              {displayDiurnal.map((d, idx) => {
                const total = displayDiurnal.length;
                const slotWidth = (880 - 50) / total;
                const x = 50 + idx * slotWidth + slotWidth * 0.5;
                const y = 170 - Math.min(150, (d.speed_mph / 22) * 150);
                return (
                  <circle
                    key={`dot-${d.hour}`}
                    cx={x}
                    cy={y}
                    r="4"
                    fill="#FFFFFF"
                    stroke="#0072CE"
                    strokeWidth="2"
                  />
                );
              })}
            </svg>
          </div>
          <div style={{ marginTop: "12px", fontSize: "0.78rem", color: "#64748B" }}>
            💡 <strong>Diurnal Insight:</strong> Notice arterial street speeds drop to ~11.8 mph during the morning peak (7–9 AM) and evening peak (4–6 PM), causing delays to surge to 7–9 minutes on major thoroughfares.
          </div>
        </div>
      </div>

      {/* Section 3: Ranked Route Bottleneck Leaderboard */}
      <div className="section-card">
        <div className="section-header">
          <h2 className="section-title">🚦 Chicago Bus Route Congestion Leaderboard</h2>
          <p className="section-subtitle">
            Ranked by mean schedule delay, peak congestion, scheduled headway regularity, and demand score.
          </p>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Route</th>
                <th>Mean Delay</th>
                <th>Peak Delay</th>
                <th>Mean Speed</th>
                <th>Scheduled Headway</th>
                <th>Demand Score</th>
                <th>ML Archetype</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((r) => (
                <tr key={r.route}>
                  <td>
                    <strong>{r.display_name}</strong>
                  </td>
                  <td style={{ color: r.mean_delay >= 5 ? "#EF4444" : "#0F172A", fontWeight: 600 }}>
                    {r.mean_delay} min
                  </td>
                  <td style={{ color: r.peak_delay >= 7 ? "#EF4444" : "#64748B" }}>
                    {r.peak_delay} min
                  </td>
                  <td>{r.mean_speed} mph</td>
                  <td>{r.scheduled_headway} min</td>
                  <td>{r.demand_score}</td>
                  <td>
                    <span
                      style={{
                        padding: "3px 8px",
                        borderRadius: "6px",
                        fontSize: "0.74rem",
                        fontWeight: 600,
                        background: `${r.cluster_color}18`,
                        color: r.cluster_color,
                        border: `1px solid ${r.cluster_color}40`,
                      }}
                    >
                      {r.cluster_name}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Section 4: Unsupervised Machine Learning: K-Means Route Clustering Studio */}
      <div className="section-card">
        <div className="section-header">
          <h2 className="section-title">🤖 Unsupervised Machine Learning: K-Means Route Clustering Studio</h2>
          <p className="section-subtitle">
            Segments Chicago routes into operational archetypes by clustering across 4 dimensions:{" "}
            <code>[Mean Delay, Peak Delay, Scheduled Headway, Demand Score]</code>.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px" }}>
          {/* 2D SVG Scatter Plot in Feature Space */}
          <div style={{ background: "#F8FAFC", border: "1px solid #E2E8F0", borderRadius: "10px", padding: "16px" }}>
            <div style={{ fontWeight: 700, fontSize: "0.86rem", marginBottom: "10px", color: "#0F172A" }}>
              K-Means Feature Space: Demand Score vs. Mean Delay
            </div>

            <svg viewBox="0 0 450 300" style={{ width: "100%", height: "280px", overflow: "visible" }}>
              {/* Axes */}
              <line x1="45" y1="240" x2="420" y2="240" stroke="#CBD5E1" strokeWidth="1.5" />
              <line x1="45" y1="30" x2="45" y2="240" stroke="#CBD5E1" strokeWidth="1.5" />

              {/* Labels */}
              <text x="230" y="275" fontSize="11" fill="#64748B" textAnchor="middle">
                Demand Score (Ridership Volume) →
              </text>
              <text x="18" y="135" fontSize="11" fill="#64748B" textAnchor="middle" transform="rotate(-90 18 135)">
                Mean Delay (min) →
              </text>

              {/* Grid marks */}
              <line x1="45" y1="135" x2="420" y2="135" stroke="#E2E8F0" strokeDasharray="3,3" />
              <text x="38" y="140" fontSize="9" fill="#94A3B8" textAnchor="end">5.0m</text>

              {/* Scatter Points */}
              {clustering.scatter_points.map((pt) => {
                // Map demand (approx 60-160) to x (60-400)
                const cx = 50 + ((pt.x_demand - 50) / 120) * 350;
                // Map delay (approx 1.5 - 7.5) to y (230 - 45)
                const cy = 230 - ((pt.y_delay - 1.5) / 6.0) * 180;
                const r = Math.max(6, Math.min(14, (pt.size_peak / 8.0) * 11));

                return (
                  <g key={pt.route}>
                    <circle
                      cx={cx}
                      cy={cy}
                      r={r}
                      fill={pt.color}
                      opacity="0.85"
                      stroke="#FFFFFF"
                      strokeWidth="2"
                    />
                    <text
                      x={cx}
                      y={cy - r - 4}
                      fontSize="10"
                      fontWeight="700"
                      fill="#0F172A"
                      textAnchor="middle"
                    >
                      {pt.route_name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Operational Policy by Cluster Archetype */}
          <div>
            <h3 style={{ fontSize: "0.95rem", fontWeight: 700, margin: "0 0 12px 0", color: "#0F172A" }}>
              📌 Operational Policy by Cluster Archetype
            </h3>

            {clustering.archetypes.map((arch) => (
              <div
                key={arch.cluster_id}
                style={{
                  border: "1px solid #E2E8F0",
                  borderLeft: `4px solid ${arch.color}`,
                  borderRadius: "8px",
                  padding: "12px 14px",
                  marginBottom: "10px",
                  background: "#FFFFFF",
                }}
              >
                <div style={{ fontWeight: 700, fontSize: "0.88rem", color: arch.color, marginBottom: "4px" }}>
                  {arch.title}
                </div>
                <div style={{ fontSize: "0.78rem", color: "#64748B", marginBottom: "6px" }}>
                  <strong>Routes:</strong> {arch.routes.join(", ")}
                </div>
                <div style={{ fontSize: "0.8rem", color: "#334155" }}>
                  <strong>Action Directive:</strong> {arch.policy}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
