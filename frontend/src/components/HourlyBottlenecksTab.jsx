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
      <div className="card-enterprise">
        <div className="card-enterprise-header">
          <h2 className="card-title-lg">⏱️ Hourly Bottleneck & Municipal Speed Sensor Analysis</h2>
          <p className="card-subtitle-text">
            Combines scheduled departures from CTA GTFS <code>stop_times.txt</code> with ground-truth arterial speeds from the{" "}
            <strong>Chicago Traffic Tracker</strong> across 1,250 road segments.
          </p>
        </div>

        {/* Prominent Time Window Selector Buttons */}
        <div style={{ display: "flex", gap: "10px", marginBottom: "20px", flexWrap: "wrap" }}>
          <button
            className={`route-chip ${activeWindow === "all" ? "active" : ""}`}
            style={{ height: "44px", fontSize: "0.92rem", padding: "0 20px" }}
            onClick={() => setActiveWindow("all")}
          >
            🕒 Full 24-Hour Cycle
          </button>
          <button
            className={`route-chip ${activeWindow === "morning" ? "active" : ""}`}
            style={{ height: "44px", fontSize: "0.92rem", padding: "0 20px" }}
            onClick={() => setActiveWindow("morning")}
          >
            🌅 Morning Rush (7–9 AM)
          </button>
          <button
            className={`route-chip ${activeWindow === "evening" ? "active" : ""}`}
            style={{ height: "44px", fontSize: "0.92rem", padding: "0 20px" }}
            onClick={() => setActiveWindow("evening")}
          >
            🌆 Evening Rush (4–7 PM)
          </button>
        </div>

        {/* Diurnal Speed vs. Delay SVG Chart */}
        <div style={{ background: "#F8FAFC", border: "1.5px solid var(--border-light)", borderRadius: "12px", padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
            <span style={{ fontWeight: 800, fontSize: "1rem", color: "var(--text-dark)" }}>
              Arterial Speed (mph) vs. Transit Delay (min) by Hour
            </span>
            <div style={{ display: "flex", gap: "20px", fontSize: "0.85rem" }}>
              <span style={{ color: "var(--cta-blue)", fontWeight: 700 }}>● Arterial Street Speed (mph)</span>
              <span style={{ color: "var(--red-main)", fontWeight: 700 }}>■ Average Transit Delay (min)</span>
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <svg viewBox="0 0 920 240" style={{ width: "100%", height: "240px", overflow: "visible" }}>
              {/* Grid Lines */}
              <line x1="55" y1="20" x2="900" y2="20" stroke="#E2E8F0" strokeDasharray="3,3" />
              <line x1="55" y1="75" x2="900" y2="75" stroke="#E2E8F0" strokeDasharray="3,3" />
              <line x1="55" y1="130" x2="900" y2="130" stroke="#E2E8F0" strokeDasharray="3,3" />
              <line x1="55" y1="185" x2="900" y2="185" stroke="#CBD5E1" strokeWidth="1.5" />

              {/* Y Axis Labels */}
              <text x="45" y="24" fontSize="11" fontWeight="600" fill="#64748B" textAnchor="end">20 mph / 10m</text>
              <text x="45" y="79" fontSize="11" fontWeight="600" fill="#64748B" textAnchor="end">15 mph / 6m</text>
              <text x="45" y="134" fontSize="11" fontWeight="600" fill="#64748B" textAnchor="end">10 mph / 3m</text>
              <text x="45" y="189" fontSize="11" fontWeight="600" fill="#64748B" textAnchor="end">0</text>

              {/* Bars for Delay */}
              {displayDiurnal.map((d, idx) => {
                const total = displayDiurnal.length;
                const slotWidth = (900 - 55) / total;
                const x = 55 + idx * slotWidth + slotWidth * 0.2;
                const barW = slotWidth * 0.6;
                const barH = Math.min(165, (d.delay_min / 10) * 165);
                const y = 185 - barH;

                return (
                  <g key={`bar-${d.hour}`}>
                    <rect
                      x={x}
                      y={y}
                      width={barW}
                      height={barH}
                      fill="#EF4444"
                      opacity="0.85"
                      rx="4"
                    />
                    <text
                      x={x + barW / 2}
                      y="208"
                      fontSize="10"
                      fontWeight="600"
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
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={displayDiurnal
                    .map((d, idx) => {
                      const total = displayDiurnal.length;
                      const slotWidth = (900 - 55) / total;
                      const x = 55 + idx * slotWidth + slotWidth * 0.5;
                      const y = 185 - Math.min(165, (d.speed_mph / 22) * 165);
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
              )}

              {/* Points on Speed Line */}
              {displayDiurnal.map((d, idx) => {
                const total = displayDiurnal.length;
                const slotWidth = (900 - 55) / total;
                const x = 55 + idx * slotWidth + slotWidth * 0.5;
                const y = 185 - Math.min(165, (d.speed_mph / 22) * 165);
                return (
                  <circle
                    key={`dot-${d.hour}`}
                    cx={x}
                    cy={y}
                    r="5"
                    fill="#FFFFFF"
                    stroke="#0072CE"
                    strokeWidth="2.5"
                  />
                );
              })}
            </svg>
          </div>
          <div style={{ marginTop: "16px", fontSize: "0.85rem", color: "var(--text-muted)", lineHeight: "1.5" }}>
            💡 <strong>Diurnal Congestion Pattern:</strong> Notice arterial street speeds drop to ~11.8 mph during the morning peak (7–9 AM) and evening peak (4–6 PM), causing passenger arrival delays to surge to 7–9 minutes on major thoroughfares.
          </div>
        </div>
      </div>

      {/* Section 3: Ranked Route Bottleneck Leaderboard */}
      <div className="card-enterprise">
        <div className="card-enterprise-header">
          <h2 className="card-title-lg">🚦 Chicago Bus Route Congestion Leaderboard</h2>
          <p className="card-subtitle-text">
            Ranked by mean schedule delay, peak congestion, scheduled headway regularity, and demand score.
          </p>
        </div>

        <div className="table-responsive-container">
          <table className="enterprise-data-table">
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
                    <strong style={{ fontSize: "0.95rem" }}>{r.display_name}</strong>
                  </td>
                  <td style={{ color: r.mean_delay >= 5 ? "var(--red-main)" : "var(--text-dark)", fontWeight: 750 }}>
                    {r.mean_delay} min
                  </td>
                  <td style={{ color: r.peak_delay >= 7 ? "var(--red-main)" : "var(--text-muted)", fontWeight: 600 }}>
                    {r.peak_delay} min
                  </td>
                  <td>{r.mean_speed} mph</td>
                  <td>{r.scheduled_headway} min</td>
                  <td><strong>{r.demand_score}</strong></td>
                  <td>
                    <span
                      style={{
                        padding: "5px 12px",
                        borderRadius: "8px",
                        fontSize: "0.78rem",
                        fontWeight: 700,
                        background: `${r.cluster_color}18`,
                        color: r.cluster_color,
                        border: `1.5px solid ${r.cluster_color}40`,
                        display: "inline-block",
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
      <div className="card-enterprise">
        <div className="card-enterprise-header">
          <h2 className="card-title-lg">🤖 Unsupervised Machine Learning: K-Means Route Clustering Studio</h2>
          <p className="card-subtitle-text">
            Segments Chicago routes into operational archetypes by clustering across 4 dimensions:{" "}
            <code>[Mean Delay, Peak Delay, Scheduled Headway, Demand Score]</code>.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "24px", alignItems: "start" }}>
          {/* 2D SVG Scatter Plot in Feature Space */}
          <div style={{ background: "#F8FAFC", border: "1.5px solid var(--border-light)", borderRadius: "12px", padding: "22px" }}>
            <div style={{ fontWeight: 800, fontSize: "0.95rem", marginBottom: "14px", color: "var(--text-dark)" }}>
              K-Means Feature Space: Demand Score vs. Mean Delay
            </div>

            <svg viewBox="0 0 460 310" style={{ width: "100%", height: "290px", overflow: "visible" }}>
              {/* Axes */}
              <line x1="50" y1="250" x2="430" y2="250" stroke="#CBD5E1" strokeWidth="2" />
              <line x1="50" y1="30" x2="50" y2="250" stroke="#CBD5E1" strokeWidth="2" />

              {/* Labels */}
              <text x="240" y="290" fontSize="12" fontWeight="700" fill="#64748B" textAnchor="middle">
                Demand Score (Ridership Volume) →
              </text>
              <text x="18" y="140" fontSize="12" fontWeight="700" fill="#64748B" textAnchor="middle" transform="rotate(-90 18 140)">
                Mean Delay (min) →
              </text>

              {/* Grid marks */}
              <line x1="50" y1="140" x2="430" y2="140" stroke="#E2E8F0" strokeDasharray="3,3" />
              <text x="42" y="145" fontSize="10" fontWeight="600" fill="#94A3B8" textAnchor="end">5.0m</text>

              {/* Scatter Points */}
              {clustering.scatter_points.map((pt) => {
                const cx = 55 + ((pt.x_demand - 50) / 120) * 360;
                const cy = 240 - ((pt.y_delay - 1.5) / 6.0) * 190;
                const r = Math.max(7, Math.min(16, (pt.size_peak / 8.0) * 13));

                return (
                  <g key={pt.route}>
                    <circle
                      cx={cx}
                      cy={cy}
                      r={r}
                      fill={pt.color}
                      opacity="0.88"
                      stroke="#FFFFFF"
                      strokeWidth="2.5"
                    />
                    <text
                      x={cx}
                      y={cy - r - 6}
                      fontSize="11"
                      fontWeight="800"
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
            <h3 style={{ fontSize: "1.05rem", fontWeight: 800, margin: "0 0 16px 0", color: "var(--text-dark)" }}>
              📌 Operational Policy by Cluster Archetype
            </h3>

            {clustering.archetypes.map((arch) => (
              <div
                key={arch.cluster_id}
                style={{
                  border: "1.5px solid var(--border-light)",
                  borderLeft: `6px solid ${arch.color}`,
                  borderRadius: "10px",
                  padding: "16px 18px",
                  marginBottom: "14px",
                  background: "#FFFFFF",
                  boxShadow: "var(--shadow-sm)",
                }}
              >
                <div style={{ fontWeight: 800, fontSize: "0.95rem", color: arch.color, marginBottom: "6px" }}>
                  {arch.title}
                </div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "8px" }}>
                  <strong>Routes:</strong> {arch.routes.join(", ")}
                </div>
                <div style={{ fontSize: "0.88rem", color: "var(--text-body)", lineHeight: "1.5" }}>
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
