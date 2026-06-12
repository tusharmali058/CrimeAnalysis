import { useState } from "react";
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell,
} from "recharts";
import {
  TrendingUp, TrendingDown, AlertTriangle, Users, FileText, MapPin, Clock, ShieldAlert,
} from "lucide-react";

const crimeTrendData = [
  { month: "Jan", IPC: 1240, violent: 312, cyber: 88 },
  { month: "Feb", IPC: 1185, violent: 298, cyber: 102 },
  { month: "Mar", IPC: 1320, violent: 341, cyber: 119 },
  { month: "Apr", IPC: 1098, violent: 278, cyber: 134 },
  { month: "May", IPC: 1430, violent: 385, cyber: 151 },
  { month: "Jun", IPC: 1560, violent: 402, cyber: 178 },
  { month: "Jul", IPC: 1388, violent: 356, cyber: 193 },
  { month: "Aug", IPC: 1520, violent: 389, cyber: 208 },
  { month: "Sep", IPC: 1642, violent: 421, cyber: 224 },
  { month: "Oct", IPC: 1715, violent: 445, cyber: 247 },
  { month: "Nov", IPC: 1589, violent: 412, cyber: 231 },
  { month: "Dec", IPC: 1834, violent: 468, cyber: 263 },
];

const districtData = [
  { district: "Bengaluru Urban", cases: 4820, change: 12.4 },
  { district: "Mysuru", cases: 1240, change: -3.2 },
  { district: "Dakshina Kannada", cases: 980, change: 8.7 },
  { district: "Belagavi", cases: 1120, change: 5.1 },
  { district: "Ballari", cases: 890, change: 18.3 },
  { district: "Kalaburagi", cases: 760, change: -1.5 },
];

const crimeTypeData = [
  { name: "Property", value: 38, color: "#00c8ff" },
  { name: "Violent", value: 22, color: "#ff4d1c" },
  { name: "Cyber", value: 18, color: "#ffd700" },
  { name: "Narcotics", value: 12, color: "#7c3aed" },
  { name: "Economic", value: 10, color: "#10b981" },
];

const recentAlerts = [
  { id: "A-2847", type: "SPIKE", district: "Bengaluru Urban", crime: "Cyber Fraud", change: "+34%", time: "14m ago", severity: "high" },
  { id: "A-2846", type: "GANG", district: "Ballari", crime: "Organized Crime", change: "New network", time: "1h ago", severity: "critical" },
  { id: "A-2845", type: "REPEAT", district: "Mysuru", crime: "Burglary", change: "Same MO ×4", time: "2h ago", severity: "medium" },
  { id: "A-2844", type: "HOTSPOT", district: "Kalaburagi", crime: "Assault", change: "+28%", time: "3h ago", severity: "high" },
  { id: "A-2843", type: "FINANCIAL", district: "Belagavi", crime: "Hawala", change: "₹2.4Cr traced", time: "4h ago", severity: "medium" },
];

const kpiData = [
  { label: "Total FIRs (YTD)", value: "18,432", change: "+7.2%", up: true, icon: FileText, color: "#00c8ff" },
  { label: "Active Accused", value: "3,847", change: "+12.1%", up: true, icon: Users, color: "#ff4d1c" },
  { label: "Solved Cases", value: "71.4%", change: "+3.8%", up: true, icon: ShieldAlert, color: "#10b981" },
  { label: "Crime Hotspots", value: "24", change: "+4", up: true, icon: MapPin, color: "#ffd700" },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded border border-border p-3" style={{ background: "#13141f", fontSize: "12px" }}>
      <div className="text-muted-foreground mb-1">{label}</div>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center gap-2">
          <span style={{ color: p.color }}>●</span>
          <span style={{ color: "#e8eaf0" }}>{p.name}: <strong>{p.value}</strong></span>
        </div>
      ))}
    </div>
  );
};

export function OverviewDashboard() {
  const [timeRange, setTimeRange] = useState<"7d" | "30d" | "1y">("1y");

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
            CRIME INTELLIGENCE OVERVIEW
          </h1>
          <p className="text-muted-foreground text-sm mt-0.5">Karnataka State — Real-time analytics · June 2026</p>
        </div>
        <div className="flex items-center gap-2">
          {(["7d", "30d", "1y"] as const).map((r) => (
            <button
              key={r}
              onClick={() => setTimeRange(r)}
              className="px-3 py-1 rounded text-sm transition-all"
              style={{
                background: timeRange === r ? "rgba(0,200,255,0.12)" : "transparent",
                color: timeRange === r ? "#00c8ff" : "#6b7094",
                border: timeRange === r ? "1px solid rgba(0,200,255,0.3)" : "1px solid transparent",
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: "11px",
              }}
            >
              {r}
            </button>
          ))}
          <div
            className="ml-2 flex items-center gap-1.5 px-3 py-1 rounded"
            style={{ background: "rgba(255,77,28,0.1)", border: "1px solid rgba(255,77,28,0.25)", color: "#ff4d1c", fontSize: "11px" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
            <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>LIVE</span>
          </div>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4">
        {kpiData.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="rounded-lg p-4 border border-border"
              style={{ background: "#0f1018" }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-muted-foreground text-xs mb-2" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.05em" }}>
                    {kpi.label.toUpperCase()}
                  </div>
                  <div style={{ fontSize: "28px", fontWeight: 700, color: "#e8eaf0", fontFamily: "'Barlow Condensed', sans-serif", lineHeight: 1 }}>
                    {kpi.value}
                  </div>
                  <div className="flex items-center gap-1 mt-1.5">
                    {kpi.up ? <TrendingUp size={12} style={{ color: kpi.color }} /> : <TrendingDown size={12} style={{ color: "#ef4444" }} />}
                    <span style={{ color: kpi.color, fontSize: "11px", fontFamily: "'JetBrains Mono', monospace" }}>{kpi.change}</span>
                    <span className="text-muted-foreground" style={{ fontSize: "10px" }}>vs last yr</span>
                  </div>
                </div>
                <div
                  className="w-9 h-9 rounded flex items-center justify-center"
                  style={{ background: `${kpi.color}18`, border: `1px solid ${kpi.color}33` }}
                >
                  <Icon size={16} style={{ color: kpi.color }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Crime Trend */}
        <div className="col-span-2 rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-medium text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
              CRIME TREND ANALYSIS · 2025
            </div>
            <div className="flex items-center gap-3">
              {[{ label: "IPC", color: "#00c8ff" }, { label: "Violent", color: "#ff4d1c" }, { label: "Cyber", color: "#ffd700" }].map(l => (
                <div key={l.label} className="flex items-center gap-1.5">
                  <span className="w-2 h-0.5 rounded-full" style={{ background: l.color }} />
                  <span className="text-muted-foreground" style={{ fontSize: "10px" }}>{l.label}</span>
                </div>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={crimeTrendData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="ipc" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00c8ff" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#00c8ff" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="violent" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff4d1c" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#ff4d1c" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="IPC" name="IPC" stroke="#00c8ff" strokeWidth={1.5} fill="url(#ipc)" dot={false} />
              <Area type="monotone" dataKey="violent" name="Violent" stroke="#ff4d1c" strokeWidth={1.5} fill="url(#violent)" dot={false} />
              <Line type="monotone" dataKey="cyber" name="Cyber" stroke="#ffd700" strokeWidth={1.5} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Crime Type Distribution */}
        <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
          <div className="text-xs font-medium text-muted-foreground mb-4" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
            CRIME CATEGORY SPLIT
          </div>
          <ResponsiveContainer width="100%" height={140}>
            <PieChart>
              <Pie
                data={crimeTypeData}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={68}
                paddingAngle={2}
                dataKey="value"
              >
                {crimeTypeData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} stroke="transparent" />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 space-y-1.5">
            {crimeTypeData.map((c) => (
              <div key={c.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: c.color }} />
                  <span className="text-muted-foreground" style={{ fontSize: "11px" }}>{c.name}</span>
                </div>
                <span style={{ color: c.color, fontSize: "11px", fontFamily: "'JetBrains Mono', monospace" }}>{c.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-3 gap-4">
        {/* District Ranking */}
        <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
          <div className="text-xs font-medium text-muted-foreground mb-4" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
            TOP DISTRICTS BY CASES
          </div>
          <ResponsiveContainer width="100%" height={170}>
            <BarChart data={districtData} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#6b7094", fontSize: 9 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="district" tick={{ fill: "#a8adc0", fontSize: 9 }} axisLine={false} tickLine={false} width={80} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="cases" name="Cases" fill="#00c8ff" radius={[0, 3, 3, 0]} fillOpacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Alerts */}
        <div className="col-span-2 rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-medium text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
              ACTIVE INTELLIGENCE ALERTS
            </div>
            <div
              className="flex items-center gap-1.5 px-2 py-0.5 rounded"
              style={{ background: "rgba(255,77,28,0.1)", color: "#ff4d1c", fontSize: "10px" }}
            >
              <AlertTriangle size={10} />
              <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>5 UNREAD</span>
            </div>
          </div>
          <div className="space-y-2">
            {recentAlerts.map((alert) => {
              const sColor = alert.severity === "critical" ? "#ff4d1c" : alert.severity === "high" ? "#ffd700" : "#00c8ff";
              return (
                <div
                  key={alert.id}
                  className="flex items-center gap-4 rounded p-3 border transition-all cursor-pointer hover:border-border"
                  style={{
                    background: "#13141f",
                    borderColor: `${sColor}18`,
                    borderLeft: `3px solid ${sColor}`,
                  }}
                >
                  <div
                    className="text-xs px-1.5 py-0.5 rounded flex-shrink-0"
                    style={{ background: `${sColor}20`, color: sColor, fontFamily: "'JetBrains Mono', monospace", fontSize: "9px" }}
                  >
                    {alert.type}
                  </div>
                  <div className="flex-1 min-w-0">
                    <span style={{ color: "#e8eaf0", fontSize: "12px" }}>{alert.crime}</span>
                    <span className="text-muted-foreground mx-1.5" style={{ fontSize: "11px" }}>·</span>
                    <span className="text-muted-foreground" style={{ fontSize: "11px" }}>{alert.district}</span>
                  </div>
                  <div style={{ color: sColor, fontSize: "11px", fontFamily: "'JetBrains Mono', monospace", flexShrink: 0 }}>{alert.change}</div>
                  <div className="flex items-center gap-1 text-muted-foreground flex-shrink-0">
                    <Clock size={10} />
                    <span style={{ fontSize: "10px" }}>{alert.time}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
