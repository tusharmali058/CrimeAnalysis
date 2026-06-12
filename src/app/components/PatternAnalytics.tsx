import { useState } from "react";
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell,
} from "recharts";

const hourlyData = Array.from({ length: 24 }, (_, h) => ({
  hour: `${String(h).padStart(2, "0")}:00`,
  property: Math.round(Math.sin((h - 14) * 0.4) * 30 + 45 + Math.random() * 15),
  violent: Math.round(Math.sin((h - 22) * 0.35) * 20 + 25 + Math.random() * 10),
  cyber: Math.round(Math.sin((h - 10) * 0.5) * 15 + 22 + Math.random() * 8),
}));

const monthlyTrend = [
  { month: "Jan", actual: 1240, predicted: 1220, anomaly: false },
  { month: "Feb", actual: 1185, predicted: 1210, anomaly: false },
  { month: "Mar", actual: 1320, predicted: 1300, anomaly: false },
  { month: "Apr", actual: 1098, predicted: 1150, anomaly: false },
  { month: "May", actual: 1430, predicted: 1380, anomaly: false },
  { month: "Jun", actual: 1760, predicted: 1500, anomaly: true },
  { month: "Jul", actual: 1388, predicted: 1420, anomaly: false },
  { month: "Aug", actual: 1520, predicted: 1480, anomaly: false },
  { month: "Sep", actual: 1642, predicted: 1580, anomaly: false },
  { month: "Oct", actual: 1715, predicted: 1660, anomaly: false },
  { month: "Nov", actual: 1589, predicted: 1620, anomaly: false },
  { month: "Dec", actual: 1834, predicted: 1750, anomaly: false },
];

const weeklyHeatmap = [
  { day: "Mon", hours: [2, 1, 0, 0, 0, 1, 3, 5, 8, 7, 9, 11, 12, 10, 9, 8, 7, 8, 9, 12, 14, 10, 7, 4] },
  { day: "Tue", hours: [1, 1, 0, 0, 0, 1, 2, 4, 7, 8, 10, 12, 11, 9, 8, 7, 6, 7, 8, 11, 13, 9, 6, 3] },
  { day: "Wed", hours: [2, 1, 0, 0, 0, 1, 3, 5, 8, 9, 11, 13, 14, 12, 10, 9, 8, 9, 10, 13, 15, 11, 8, 4] },
  { day: "Thu", hours: [2, 1, 0, 0, 0, 1, 2, 4, 7, 8, 10, 11, 12, 10, 9, 8, 7, 8, 9, 12, 14, 10, 7, 3] },
  { day: "Fri", hours: [3, 2, 1, 0, 0, 1, 3, 5, 9, 10, 12, 14, 15, 13, 11, 10, 9, 10, 12, 15, 18, 14, 10, 6] },
  { day: "Sat", hours: [5, 4, 3, 2, 1, 1, 2, 3, 5, 6, 8, 10, 11, 10, 9, 8, 8, 9, 11, 14, 18, 16, 13, 8] },
  { day: "Sun", hours: [6, 5, 4, 3, 1, 1, 1, 2, 4, 5, 6, 8, 9, 8, 7, 6, 6, 7, 9, 11, 15, 14, 11, 7] },
];

const socioData = [
  { district: "BU", urbanization: 92, crime_rate: 4820, literacy: 88 },
  { district: "MYS", urbanization: 68, crime_rate: 1240, literacy: 82 },
  { district: "BEL", urbanization: 55, crime_rate: 1120, literacy: 76 },
  { district: "BAL", urbanization: 48, crime_rate: 890, literacy: 68 },
  { district: "DK", urbanization: 62, crime_rate: 980, literacy: 84 },
  { district: "KAL", urbanization: 45, crime_rate: 760, literacy: 71 },
  { district: "TUM", urbanization: 52, crime_rate: 720, literacy: 78 },
  { district: "KOL", urbanization: 42, crime_rate: 610, literacy: 74 },
];

function getHeatColor(value: number) {
  const max = 18;
  const pct = value / max;
  if (pct < 0.2) return "rgba(0,200,255,0.08)";
  if (pct < 0.4) return "rgba(0,200,255,0.2)";
  if (pct < 0.6) return "rgba(255,215,0,0.3)";
  if (pct < 0.8) return "rgba(255,100,30,0.5)";
  return "rgba(255,77,28,0.8)";
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded border border-border p-2" style={{ background: "#13141f", fontSize: "11px" }}>
      <div style={{ color: "#a8adc0" }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.name} style={{ color: p.color }}>
          {p.name}: <strong>{p.value}</strong>
        </div>
      ))}
    </div>
  );
};

export function PatternAnalytics() {
  const [activeTab, setActiveTab] = useState<"temporal" | "heatmap" | "socio" | "anomaly">("temporal");

  const tabs = [
    { id: "temporal", label: "Temporal Patterns" },
    { id: "heatmap", label: "Crime Heatmap" },
    { id: "socio", label: "Socio-Economic" },
    { id: "anomaly", label: "Anomaly Detection" },
  ] as const;

  return (
    <div className="flex flex-col gap-4" style={{ height: "calc(100vh - 88px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
            CRIME PATTERN ANALYTICS
          </h1>
          <p className="text-muted-foreground text-sm">Statistical analysis · Spatiotemporal clusters · Trend intelligence</p>
        </div>
        <div className="flex items-center gap-1 rounded-lg p-1 border border-border" style={{ background: "#0f1018" }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="px-3 py-1.5 rounded text-xs transition-all"
              style={{
                background: activeTab === tab.id ? "rgba(0,200,255,0.12)" : "transparent",
                color: activeTab === tab.id ? "#00c8ff" : "#6b7094",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {activeTab === "temporal" && (
        <div className="flex flex-col gap-4 flex-1">
          <div className="grid grid-cols-2 gap-4 flex-1">
            <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
              <div className="text-xs font-medium text-muted-foreground mb-4" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                HOURLY CRIME DISTRIBUTION
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={hourlyData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="propGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00c8ff" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#00c8ff" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="violGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ff4d1c" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#ff4d1c" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="hour" tick={{ fill: "#6b7094", fontSize: 8 }} axisLine={false} tickLine={false} interval={3} />
                  <YAxis tick={{ fill: "#6b7094", fontSize: 9 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="property" name="Property" stroke="#00c8ff" strokeWidth={1.5} fill="url(#propGrad)" dot={false} />
                  <Area type="monotone" dataKey="violent" name="Violent" stroke="#ff4d1c" strokeWidth={1.5} fill="url(#violGrad)" dot={false} />
                  <Line type="monotone" dataKey="cyber" name="Cyber" stroke="#ffd700" strokeWidth={1.5} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
              <div className="mt-2 text-muted-foreground" style={{ fontSize: "10px" }}>
                Peak violent crime: 22:00–00:00 · Peak property crime: 12:00–14:00 · Peak cyber: 10:00–12:00
              </div>
            </div>

            <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
              <div className="text-xs font-medium text-muted-foreground mb-4" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                MONTHLY TREND — ACTUAL VS PREDICTED
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={monthlyTrend} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="month" tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#6b7094", fontSize: 9 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="actual" name="Actual" stroke="#00c8ff" strokeWidth={2} dot={(props: any) => {
                    const d = monthlyTrend[props.index];
                    if (d?.anomaly) return <circle key={props.index} cx={props.cx} cy={props.cy} r={6} fill="#ff4d1c" stroke="#ff4d1c" strokeWidth={2} fillOpacity={0.3} />;
                    return <circle key={props.index} cx={props.cx} cy={props.cy} r={2} fill="#00c8ff" />;
                  }} />
                  <Line type="monotone" dataKey="predicted" name="Predicted" stroke="#7c3aed" strokeWidth={1.5} strokeDasharray="4 2" dot={false} />
                </LineChart>
              </ResponsiveContainer>
              <div className="flex items-center gap-1.5 mt-2" style={{ fontSize: "10px" }}>
                <span className="w-2 h-2 rounded-full" style={{ background: "#ff4d1c" }} />
                <span className="text-muted-foreground">Anomaly detected: Jun 2026 — 17.3% above prediction threshold</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "heatmap" && (
        <div className="rounded-lg p-4 border border-border flex-1" style={{ background: "#0f1018" }}>
          <div className="text-xs font-medium text-muted-foreground mb-4" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
            WEEKLY × HOURLY CRIME INTENSITY HEATMAP
          </div>
          <div className="overflow-x-auto">
            <div style={{ minWidth: 600 }}>
              {/* Hour labels */}
              <div className="flex items-center gap-0 ml-10 mb-1">
                {Array.from({ length: 24 }, (_, h) => (
                  <div key={h} style={{ width: "calc((100% - 40px) / 24)", fontSize: "8px", color: "#6b7094", textAlign: "center", fontFamily: "'JetBrains Mono', monospace" }}>
                    {h % 4 === 0 ? `${String(h).padStart(2, "0")}` : ""}
                  </div>
                ))}
              </div>
              {weeklyHeatmap.map((row) => (
                <div key={row.day} className="flex items-center gap-0 mb-1">
                  <div style={{ width: 40, color: "#6b7094", fontSize: "10px", flexShrink: 0 }}>{row.day}</div>
                  {row.hours.map((val, h) => (
                    <div
                      key={h}
                      title={`${row.day} ${String(h).padStart(2, "0")}:00 — ${val} incidents`}
                      style={{
                        flex: 1,
                        height: 28,
                        background: getHeatColor(val),
                        border: "1px solid rgba(0,0,0,0.2)",
                        borderRadius: 2,
                        cursor: "pointer",
                      }}
                    />
                  ))}
                </div>
              ))}
              {/* Scale */}
              <div className="flex items-center gap-2 mt-4 ml-10">
                <span className="text-muted-foreground" style={{ fontSize: "9px" }}>Low</span>
                {["rgba(0,200,255,0.08)", "rgba(0,200,255,0.2)", "rgba(255,215,0,0.3)", "rgba(255,100,30,0.5)", "rgba(255,77,28,0.8)"].map((c, i) => (
                  <div key={i} style={{ width: 24, height: 14, background: c, borderRadius: 2 }} />
                ))}
                <span className="text-muted-foreground" style={{ fontSize: "9px" }}>High</span>
              </div>
            </div>
          </div>
          <div className="mt-4 text-muted-foreground" style={{ fontSize: "11px" }}>
            Fridays 20:00–23:00 and Saturdays 20:00–22:00 are the highest-risk windows — consistent with entertainment district activity patterns.
          </div>
        </div>
      )}

      {activeTab === "socio" && (
        <div className="flex flex-col gap-4 flex-1">
          <div className="rounded-lg p-4 border border-border flex-1" style={{ background: "#0f1018" }}>
            <div className="text-xs font-medium text-muted-foreground mb-4" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
              URBANIZATION VS CRIME RATE CORRELATION (R² = 0.78)
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart margin={{ top: 10, right: 20, left: -10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="urbanization" name="Urbanization %" tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: "Urbanization %", fill: "#6b7094", fontSize: 10, dy: 14 }} />
                <YAxis dataKey="crime_rate" name="Crime Cases" tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} label={{ value: "Cases", fill: "#6b7094", fontSize: 10, angle: -90, dx: -14 }} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const d = payload[0]?.payload;
                    return (
                      <div className="rounded border border-border p-2" style={{ background: "#13141f", fontSize: "11px" }}>
                        <div style={{ color: "#00c8ff", fontWeight: 600 }}>{d.district}</div>
                        <div style={{ color: "#a8adc0" }}>Urbanization: {d.urbanization}%</div>
                        <div style={{ color: "#a8adc0" }}>Cases: {d.crime_rate.toLocaleString()}</div>
                        <div style={{ color: "#a8adc0" }}>Literacy: {d.literacy}%</div>
                      </div>
                    );
                  }}
                />
                <Scatter data={socioData} fill="#00c8ff" fillOpacity={0.75} />
              </ScatterChart>
            </ResponsiveContainer>
            <div className="mt-2 text-muted-foreground" style={{ fontSize: "11px" }}>
              Strong positive correlation between urbanization and reported crime rate (R² = 0.78). High-literacy districts show moderating effect on violent crime despite urbanization.
            </div>
          </div>
        </div>
      )}

      {activeTab === "anomaly" && (
        <div className="flex flex-col gap-4 flex-1">
          <div className="rounded-lg p-4 border border-border flex-1" style={{ background: "#0f1018" }}>
            <div className="flex items-center justify-between mb-4">
              <div className="text-xs font-medium text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                DETECTED ANOMALIES — ML DRIVEN
              </div>
              <div className="px-2 py-0.5 rounded" style={{ background: "rgba(255,77,28,0.12)", color: "#ff4d1c", fontSize: "10px", fontFamily: "'JetBrains Mono', monospace" }}>
                3 ACTIVE ANOMALIES
              </div>
            </div>
            <div className="space-y-3">
              {[
                { id: "ANO-2026-047", desc: "Cyber fraud cases in BU district spiked 34% above 6-month baseline", district: "Bengaluru Urban", severity: "high", deviation: "+34%", detected: "2026-06-08", model: "LSTM Anomaly Detector" },
                { id: "ANO-2026-048", desc: "Coordinated assault pattern in Ballari matching 3 distinct FIRs — potential organized activity", district: "Ballari", severity: "critical", deviation: "+91%", detected: "2026-06-10", model: "Graph Anomaly ML" },
                { id: "ANO-2026-049", desc: "Unusual transaction cluster linked to 7 FIRs in Belagavi — hawala network suspected", district: "Belagavi", severity: "high", deviation: "₹2.4Cr", detected: "2026-06-11", model: "Financial Network ML" },
              ].map((a) => {
                const sc = a.severity === "critical" ? "#ff4d1c" : "#ffd700";
                return (
                  <div
                    key={a.id}
                    className="rounded-lg p-4 border"
                    style={{ background: "#13141f", borderColor: `${sc}25`, borderLeft: `3px solid ${sc}` }}
                  >
                    <div className="flex items-start gap-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span style={{ color: sc, fontFamily: "'JetBrains Mono', monospace", fontSize: "10px" }}>{a.id}</span>
                          <span className="px-1.5 py-0.5 rounded capitalize" style={{ background: `${sc}12`, color: sc, fontSize: "9px" }}>{a.severity}</span>
                          <span className="text-muted-foreground" style={{ fontSize: "10px" }}>{a.district}</span>
                        </div>
                        <p style={{ color: "#c8ccd8", fontSize: "12px" }}>{a.desc}</p>
                        <div className="flex items-center gap-4 mt-2">
                          <div>
                            <span className="text-muted-foreground" style={{ fontSize: "10px" }}>Deviation: </span>
                            <span style={{ color: sc, fontFamily: "'JetBrains Mono', monospace", fontSize: "11px" }}>{a.deviation}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground" style={{ fontSize: "10px" }}>Model: </span>
                            <span style={{ color: "#a8adc0", fontSize: "10px" }}>{a.model}</span>
                          </div>
                          <div>
                            <span className="text-muted-foreground" style={{ fontSize: "10px" }}>Detected: </span>
                            <span style={{ color: "#a8adc0", fontFamily: "'JetBrains Mono', monospace", fontSize: "10px" }}>{a.detected}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
