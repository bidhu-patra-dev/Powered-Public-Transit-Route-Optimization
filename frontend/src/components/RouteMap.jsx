import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet's default icon paths in bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

export default function RouteMap({ geojsonData, vehicles = [], selectedRoute, onSelectRoute }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geojsonLayerRef = useRef(null);
  const vehiclesLayerRef = useRef(null);

  // Initialize Leaflet map instance once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [41.8781, -87.6298],
      zoom: 11,
      zoomControl: true,
      preferCanvas: true,
    });

    // Standard OpenStreetMap tiles (100% free, zero API key required, crisp street grid)
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    geojsonLayerRef.current = L.layerGroup().addTo(map);
    vehiclesLayerRef.current = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;

    // Force map size invalidation so it renders fully inside React dynamic layout
    setTimeout(() => {
      map.invalidateSize();
    }, 150);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Route Polylines / Line Connections when geojsonData changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layer = geojsonLayerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
      return;
    }

    const geoLayer = L.geoJSON(geojsonData, {
      style: (feature) => {
        const rt = String(feature.properties?.ROUTE || "");
        const isSelected = selectedRoute && selectedRoute === rt;
        const color = feature.properties?.color || "#0072CE";

        return {
          color: color,
          weight: isSelected ? 6 : 4,
          opacity: isSelected ? 0.95 : 0.75,
          lineJoin: "round",
          lineCap: "round",
        };
      },
      onEachFeature: (feature, featureLayer) => {
        const rt = feature.properties?.ROUTE;
        const name = feature.properties?.NAME || `Route ${rt}`;
        const disp = feature.properties?.display_name || `Route ${rt} - ${name}`;

        featureLayer.bindTooltip(
          `<strong>${disp}</strong><br><small style="color:#64748B;">Click to inspect route</small>`,
          { sticky: true, className: "route-tooltip" }
        );

        featureLayer.on({
          mouseover: (e) => {
            const l = e.target;
            l.setStyle({ weight: 7, opacity: 1.0 });
            l.bringToFront();
          },
          mouseout: (e) => {
            const l = e.target;
            const isSelected = selectedRoute && selectedRoute === rt;
            l.setStyle({
              weight: isSelected ? 6 : 4,
              opacity: isSelected ? 0.95 : 0.75,
            });
          },
          click: () => {
            if (onSelectRoute && rt) {
              onSelectRoute(rt);
            }
          },
        });
      },
    });

    layer.addLayer(geoLayer);

    // Auto-fit map bounds to encompass all route lines cleanly
    try {
      const bounds = geoLayer.getBounds();
      if (bounds && bounds.isValid()) {
        map.fitBounds(bounds, { padding: [30, 30] });
      }
    } catch (e) {
      // ignore
    }
  }, [geojsonData, selectedRoute, onSelectRoute]);

  // Update live vehicle markers along the route lines
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layer = vehiclesLayerRef.current;
    if (!map || !layer) return;

    layer.clearLayers();

    vehicles.forEach((v) => {
      if (!v.lat || !v.lon) return;

      const markerColor = v.color || "#0072CE";
      const delayStatus = v.status_label || "On-Time";

      // Custom animated circle marker with route number badge
      const icon = L.divIcon({
        className: "bus-custom-marker",
        html: `
          <div style="
            background: ${markerColor};
            color: #FFFFFF;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 800;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
            cursor: pointer;
          ">
            ${v.route}
          </div>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });

      const marker = L.marker([v.lat, v.lon], { icon });

      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; line-height: 1.5; min-width: 170px;">
          <div style="font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #0F172A;">
            Bus #${v.vid} (${v.display_name})
          </div>
          <div style="color: #64748B; margin-bottom: 6px;">
            Status: <span style="font-weight: 700; color: ${markerColor};">${delayStatus}</span>
          </div>
          <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
            <tr><td style="color:#64748B;">Live Speed:</td><td><strong>${v.speed} mph</strong></td></tr>
            <tr><td style="color:#64748B;">Delay:</td><td><strong>${v.delay_min} min</strong></td></tr>
            <tr><td style="color:#64748B;">GPS Heading:</td><td>${v.heading}°</td></tr>
            <tr><td style="color:#64748B;">Telemetry Ping:</td><td>${v.last_update}</td></tr>
          </table>
        </div>
      `);

      layer.addLayer(marker);
    });
  }, [vehicles]);

  return (
    <div
      ref={mapContainerRef}
      className="leaflet-map-container"
      style={{ height: "640px", width: "100%", minHeight: "640px" }}
    />
  );
}
