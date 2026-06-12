import { useState } from "react";
import { AlertTriangle, TrendingUp, Clock, Layers, ChevronDown } from "lucide-react";

const districts = [
  { id: "bengaluru-urban", name: "Bengaluru Urban", x: 310, y: 230, radius: 52, cases: 4820, risk: "critical", change: "+12.4%" },
  { id: "bengaluru-rural", name: "Bengaluru Rural", x: 260, y: 175, radius: 34, cases: 980, risk: "medium", change: "+5.1%" },
  { id: "mysuru", name: "Mysuru", x: 240, y: 300, radius: 32, cases: 1240, risk: "medium", change: "-3.2%" },
  { id: "mandya", name: "Mandya", x: 270, y: 265, radius: 22, cases: 540, risk: "low", change: "-1.1%" },
  { id: "tumakuru", name: "Tumakuru", x: 290, y: 175, radius: 28, cases: 720, risk: "medium", change: "+8.3%" },
  { id: "kolar", name: "Kolar", x: 380, y: 195, radius: 24, cases: 610, risk: "medium", change: "+6.7%" },
  { id: "chikkaballapur", name: "Chikkaballapur", x: 360, y: 165, radius: 20, cases: 430, risk: "low", change: "+2.1%" },
  { id: "ramanagara", name: "Ramanagara", x: 280, y: 230, radius: 18, cases: 380, risk: "low", change: "-0.5%" },
  { id: "hassan", name: "Hassan", x: 205, y: 255, radius: 26, cases: 680, risk: "medium", change: "+4.2%" },
  { id: "dakshina-kannada", name: "Dakshina Kannada", x: 190, y: 330, radius: 28, cases: 980, risk: "high", change: "+8.7%" },
  { id: "belagavi", name: "Belagavi", x: 175, y: 130, radius: 34, cases: 1120, risk: "high", change: "+5.1%" },
  { id: "ballari", name: "Ballari", x: 370, y: 145, radius: 28, cases: 890, risk: "high", change: "+18.3%" },
  { id: "kalaburagi", name: "Kalaburagi", x: 430, y: 115, radius: 26, cases: 760, risk: "medium", change: "-1.5%" },
  { id: "vijayapura", name: "Vijayapura", x: 310, y: 110, radius: 26, cases: 700, risk: "medium", change: "+3.8%" },
  { id: "dharwad", name: "Dharwad", x: 185, y: 165, radius: 24, cases: 640, risk: "medium", change: "+2.9%" },
  { id: "haveri", name: "Haveri", x: 215, y: 185, radius: 20, cases: 440, risk: "low", change: "+1.2%" },
  { id: "gadag", name: "Gadag", x: 238, y: 150, radius: 18, cases: 380, risk: "low", change: "0.0%" },
  { id: "uttara-kannada", name: "Uttara Kannada", x: 170, y: 220, radius: 22, cases: 510, risk: "medium", change: "+7.1%" },
  { id: "shivamogga", name: "Shivamogga", x: 230, y: 225, radius: 24, cases: 580, risk: "medium", change: "+3.4%" },
  { id: "chikkamagaluru", name: "Chikkamagaluru", x: 220, y: 270, radius: 22, cases: 460, risk: "low", change: "-2.0%" },
  { id: "kodagu", name: "Kodagu", x: 225, y: 305, radius: 16, cases: 290, risk: "low", change: "-4.1%" },
  { id: "udupi", name: "Udupi", x: 180, y: 295, radius: 18, cases: 420, risk: "low", change: "+1.8%" },
  { id: "davangere", name: "Davangere", x: 278, y: 195, radius: 22, cases: 560, risk: "medium", change: "+5.5%" },
  { id: "chitradurga", name: "Chitradurga", x: 318, y: 175, radius: 22, cases: 520, risk: "medium", change: "+4.7%" },
  { id: "chamarajanagar", name: "Chamarajanagar", x: 268, y: 335, radius: 16, cases: 310, risk: "low", change: "-1.3%" },
  { id: "bidar", name: "Bidar", x: 450, y: 95, radius: 20, cases: 480, risk: "medium", change: "+6.2%" },
  { id: "raichur", name: "Raichur", x: 400, y: 120, radius: 22, cases: 550, risk: "medium", change: "+9.1%" },
  { id: "koppal", name: "Koppal", x: 350, y: 120, radius: 18, cases: 400, risk: "medium", change: "+7.4%" },
  { id: "yadgir", name: "Yadgir", x: 430, y: 140, radius: 16, cases: 340, risk: "low", change: "+3.6%" },
  { id: "vijayanagara", name: "Vijayanagara", x: 338, y: 155, radius: 20, cases: 460, risk: "medium", change: "+11.2%" },
];

const RISK_COLORS: Record<string, { fill: string; stroke: string; label: string }> = {
  critical: { fill: "#ff4d1c", stroke: "#ff6b3d", label: "Critical" },
  high: { fill: "#ffd700", stroke: "#ffed4a", label: "High" },
  medium: { fill: "#00c8ff", stroke: "#33d4ff", label: "Medium" },
  low: { fill: "#10b981", stroke: "#34d399", label: "Low" },
};

const hotspots = [
  { name: "Whitefield", x: 355, y: 240, type: "Cyber Fraud" },
  { name: "Electronic City", x: 330, y: 270, type: "Chain Snatching" },
  { name: "Majestic", x: 312, y: 225, type: "Pickpocketing" },
  { name: "Rajajinagar", x: 295, y: 220, type: "Gang Activity" },
  { name: "Yelahanka", x: 315, y: 205, type: "Vehicle Theft" },
];

const recentIncidents = [
  { time: "08:34", district: "Bengaluru Urban", type: "Cyber Fraud", severity: "high" },
  { time: "09:12", district: "Ballari", type: "Assault", severity: "critical" },
  { time: "10:05", district: "Belagavi", type: "Robbery", severity: "high" },
  { time: "10:48", district: "Mysuru", type: "Burglary", severity: "medium" },
  { time: "11:23", district: "Dakshina Kannada", type: "Kidnapping", severity: "critical" },
  { time: "12:01", district: "Kalaburagi", type: "Fraud", severity: "medium" },
];

export function CrimeMap() {
  const [selected, setSelected] = useState<typeof districts[0] | null>(null);
  const [layerMode, setLayerMode] = useState<"risk" | "density" | "type">("risk");
  const [showHotspots, setShowHotspots] = useState(true);

  return (
    <div className="flex flex-col gap-4" style={{ height: "calc(100vh - 88px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
            KARNATAKA CRIME HEATMAP
          </h1>
          <p className="text-muted-foreground text-sm">30 districts · District-level drill-down · June 2026</p>
        </div>
        <div className="flex items-center gap-2">
          {(["risk", "density", "type"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setLayerMode(m)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs transition-all"
              style={{
                background: layerMode === m ? "rgba(0,200,255,0.12)" : "#0f1018",
                color: layerMode === m ? "#00c8ff" : "#6b7094",
                borderColor: layerMode === m ? "rgba(0,200,255,0.3)" : "rgba(255,255,255,0.07)",
              }}
            >
              <Layers size={12} />
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
          <button
            onClick={() => setShowHotspots(!showHotspots)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs transition-all"
            style={{
              background: showHotspots ? "rgba(255,77,28,0.12)" : "#0f1018",
              color: showHotspots ? "#ff4d1c" : "#6b7094",
              borderColor: showHotspots ? "rgba(255,77,28,0.3)" : "rgba(255,255,255,0.07)",
            }}
          >
            <AlertTriangle size={12} />
            Hotspots
          </button>
        </div>
      </div>

      <div className="flex gap-4 flex-1 min-h-0">
        {/* Map */}
        <div className="flex-1 rounded-lg border border-border overflow-hidden relative" style={{ background: "#09090f" }}>
          {/* Grid overlay */}
          <svg width="100%" height="100%" style={{ position: "absolute", top: 0, left: 0, pointerEvents: "none" }}>
            <defs>
              <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>

          {/* Map SVG */}
          <svg viewBox="100 85 420 280" width="100%" height="100%" style={{ position: "absolute", top: 0, left: 0 }}>
            {/* State outline (simplified polygon) */}
            <path
              d="M 165 95 L 220 88 L 280 90 L 340 88 L 400 95 L 450 100 L 470 120 L 460 150 L 440 165 L 420 175 L 400 195 L 390 220 L 380 250 L 365 275 L 345 300 L 320 325 L 300 345 L 275 355 L 250 350 L 225 340 L 200 330 L 185 315 L 175 295 L 170 270 L 160 245 L 155 215 L 158 185 L 160 155 L 162 130 L 165 95 Z"
              fill="rgba(0,200,255,0.02)"
              stroke="rgba(0,200,255,0.12)"
              strokeWidth="1"
            />

            {/* Districts */}
            {districts.map((d) => {
              const color = RISK_COLORS[d.risk];
              const isSelected = selected?.id === d.id;
              const opacity = layerMode === "density" ? Math.min(d.cases / 5000, 1) : 0.85;
              return (
                <g key={d.id} onClick={() => setSelected(isSelected ? null : d)} style={{ cursor: "pointer" }}>
                  <circle
                    cx={d.x}
                    cy={d.y}
                    r={d.radius}
                    fill={color.fill}
                    fillOpacity={isSelected ? opacity : opacity * 0.55}
                    stroke={isSelected ? color.stroke : color.fill}
                    strokeWidth={isSelected ? 2 : 0.8}
                    strokeOpacity={0.7}
                  />
                  {isSelected && (
                    <circle cx={d.x} cy={d.y} r={d.radius + 5} fill="none" stroke={color.stroke} strokeWidth={1.5} strokeDasharray="4 3" strokeOpacity={0.8} />
                  )}
                  {d.radius > 22 && (
                    <text x={d.x} y={d.y + 1} fill="#fff" textAnchor="middle" dominantBaseline="middle" style={{ fontSize: "8px", fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>
                      {d.cases > 999 ? `${(d.cases / 1000).toFixed(1)}K` : d.cases}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Hotspot pins */}
            {showHotspots && hotspots.map((h) => (
              <g key={h.name}>
                <circle cx={h.x} cy={h.y} r={4} fill="#ff4d1c" fillOpacity={0.9} />
                <circle cx={h.x} cy={h.y} r={8} fill="#ff4d1c" fillOpacity={0.15} />
                <text x={h.x + 7} y={h.y + 1} fill="#ff9966" style={{ fontSize: "7px", fontFamily: "'Inter', sans-serif" }} dominantBaseline="middle">
                  {h.name}
                </text>
              </g>
            ))}
          </svg>

          {/* Legend */}
          <div className="absolute bottom-3 left-3 rounded p-2.5" style={{ background: "rgba(9,9,15,0.85)", border: "1px solid rgba(255,255,255,0.07)" }}>
            <div className="text-muted-foreground mb-2" style={{ fontSize: "9px", fontFamily: "'JetBrains Mono', monospace" }}>RISK LEVEL</div>
            {Object.entries(RISK_COLORS).map(([key, val]) => (
              <div key={key} className="flex items-center gap-2 py-0.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: val.fill }} />
                <span style={{ color: "#a8adc0", fontSize: "10px" }}>{val.label}</span>
              </div>
            ))}
            {showHotspots && (
              <div className="flex items-center gap-2 py-0.5 mt-1 border-t border-border pt-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: "#ff4d1c" }} />
                <span style={{ color: "#a8adc0", fontSize: "10px" }}>Active Hotspot</span>
              </div>
            )}
          </div>

          {/* Selected district tooltip */}
          {selected && (
            <div
              className="absolute top-3 right-3 rounded-lg p-3 min-w-44"
              style={{ background: "rgba(15,16,24,0.95)", border: `1px solid ${RISK_COLORS[selected.risk].fill}40` }}
            >
              <div
                className="text-xs px-1.5 py-0.5 rounded inline-flex mb-2"
                style={{ background: `${RISK_COLORS[selected.risk].fill}20`, color: RISK_COLORS[selected.risk].fill, fontFamily: "'JetBrains Mono', monospace", fontSize: "9px" }}
              >
                {selected.risk.toUpperCase()} RISK
              </div>
              <div style={{ color: "#e8eaf0", fontWeight: 600, fontSize: "13px", marginBottom: 6 }}>{selected.name}</div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-xs">Total cases</span>
                <span style={{ color: "#e8eaf0", fontFamily: "'JetBrains Mono', monospace", fontSize: "13px", fontWeight: 700 }}>{selected.cases.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between mt-1">
                <span className="text-muted-foreground text-xs">YoY change</span>
                <span style={{ color: selected.change.startsWith("-") ? "#10b981" : "#ff4d1c", fontFamily: "'JetBrains Mono', monospace", fontSize: "11px" }}>
                  {selected.change}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-52 flex flex-col gap-3 flex-shrink-0">
          {/* Summary */}
          <div className="rounded-lg p-3 border border-border" style={{ background: "#0f1018" }}>
            <div className="text-xs font-medium text-muted-foreground mb-3" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
              STATE SUMMARY
            </div>
            {Object.entries(RISK_COLORS).map(([key, val]) => {
              const count = districts.filter(d => d.risk === key).length;
              return (
                <div key={key} className="flex items-center justify-between py-1.5 border-b border-border last:border-0">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full" style={{ background: val.fill }} />
                    <span className="text-xs" style={{ color: "#a8adc0" }}>{val.label}</span>
                  </div>
                  <span style={{ color: val.fill, fontFamily: "'JetBrains Mono', monospace", fontSize: "13px", fontWeight: 600 }}>{count}</span>
                </div>
              );
            })}
          </div>

          {/* Live Feed */}
          <div className="rounded-lg p-3 border border-border flex-1" style={{ background: "#0f1018", overflow: "hidden" }}>
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs font-medium text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                LIVE INCIDENTS
              </div>
              <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "#ff4d1c" }} />
            </div>
            <div className="space-y-2 overflow-y-auto" style={{ maxHeight: 260 }}>
              {recentIncidents.map((inc, i) => {
                const c = inc.severity === "critical" ? "#ff4d1c" : inc.severity === "high" ? "#ffd700" : "#00c8ff";
                return (
                  <div key={i} className="rounded p-2" style={{ background: "#13141f", borderLeft: `2px solid ${c}` }}>
                    <div className="flex items-center justify-between">
                      <span style={{ color: "#a8adc0", fontFamily: "'JetBrains Mono', monospace", fontSize: "9px" }}>{inc.time}</span>
                      <span style={{ color: c, fontSize: "9px" }}>●</span>
                    </div>
                    <div style={{ color: "#e8eaf0", fontSize: "11px", fontWeight: 500, marginTop: 2 }}>{inc.type}</div>
                    <div className="text-muted-foreground" style={{ fontSize: "10px" }}>{inc.district}</div>
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
