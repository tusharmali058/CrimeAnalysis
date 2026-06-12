import { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { OverviewDashboard } from "./components/OverviewDashboard";
import { CrimeAIChat } from "./components/CrimeAIChat";
import { CriminalNetwork } from "./components/CriminalNetwork";
import { CrimeMap } from "./components/CrimeMap";
import { PatternAnalytics } from "./components/PatternAnalytics";
import { OffenderProfiling } from "./components/OffenderProfiling";
import { Bell, Search, Shield } from "lucide-react";

const VIEW_TITLES: Record<string, string> = {
  overview: "Overview",
  chat: "Crime AI Chat",
  network: "Criminal Network",
  heatmap: "Crime Map",
  analytics: "Pattern Analytics",
  profiling: "Offender Profiling",
  forecast: "Forecasting",
  financial: "Financial Crime",
  alerts: "Alert Centre",
};

function ForecastPlaceholder() {
  return (
    <div className="flex flex-col items-center justify-center" style={{ height: "calc(100vh - 88px)" }}>
      <div className="w-16 h-16 rounded-xl flex items-center justify-center mb-4" style={{ background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.2)" }}>
        <Shield size={28} style={{ color: "#7c3aed" }} />
      </div>
      <h2 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "22px", fontWeight: 700, color: "#e8eaf0", letterSpacing: "0.04em" }}>
        AI FORECASTING MODULE
      </h2>
      <p className="text-muted-foreground text-sm mt-2 text-center max-w-sm">
        Predictive crime hotspot models, 7-day / 30-day / seasonal forecasting, and early warning alert configuration.
      </p>
      <div className="mt-4 px-4 py-2 rounded border text-sm" style={{ background: "rgba(124,58,237,0.08)", borderColor: "rgba(124,58,237,0.25)", color: "#a78bfa" }}>
        Coming in v2 — ML models in training
      </div>
    </div>
  );
}

function FinancialPlaceholder() {
  return (
    <div className="flex flex-col items-center justify-center" style={{ height: "calc(100vh - 88px)" }}>
      <div className="w-16 h-16 rounded-xl flex items-center justify-center mb-4" style={{ background: "rgba(255,215,0,0.1)", border: "1px solid rgba(255,215,0,0.2)" }}>
        <Shield size={28} style={{ color: "#ffd700" }} />
      </div>
      <h2 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "22px", fontWeight: 700, color: "#e8eaf0", letterSpacing: "0.04em" }}>
        FINANCIAL CRIME MODULE
      </h2>
      <p className="text-muted-foreground text-sm mt-2 text-center max-w-sm">
        Transaction network graphs, hawala flow detection, suspicious account clustering, and money trail visualization.
      </p>
      <div className="mt-4 px-4 py-2 rounded border text-sm" style={{ background: "rgba(255,215,0,0.08)", borderColor: "rgba(255,215,0,0.25)", color: "#ffd700" }}>
        FIU data integration pending
      </div>
    </div>
  );
}

function AlertsView() {
  const alerts = [
    { id: "A-2847", type: "SPIKE", district: "Bengaluru Urban", crime: "Cyber Fraud", detail: "34% above 6-month baseline", severity: "high", time: "14m ago" },
    { id: "A-2846", type: "GANG", district: "Ballari", crime: "Organized Crime", detail: "New co-offender cluster identified (7 nodes)", severity: "critical", time: "1h ago" },
    { id: "A-2845", type: "REPEAT", district: "Mysuru", crime: "Burglary", detail: "Same MO — 4th incident same PS", severity: "medium", time: "2h ago" },
    { id: "A-2844", type: "HOTSPOT", district: "Kalaburagi", crime: "Assault", detail: "28% spike near NH-50 corridor", severity: "high", time: "3h ago" },
    { id: "A-2843", type: "FINANCIAL", district: "Belagavi", crime: "Hawala", detail: "₹2.4 Cr suspicious transaction cluster", severity: "medium", time: "4h ago" },
    { id: "A-2842", type: "FORECAST", district: "Bengaluru Urban", crime: "Cyber Fraud", detail: "High risk predicted for next 7 days", severity: "high", time: "6h ago" },
    { id: "A-2841", type: "REPEAT", district: "Dakshina Kannada", crime: "Vehicle Theft", detail: "Same accused MO — 3 jurisdictions", severity: "medium", time: "8h ago" },
  ];
  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
          ALERT CENTRE
        </h1>
        <p className="text-muted-foreground text-sm">7 unread alerts · Configured thresholds: spike &gt;20%, new gang cluster, repeat MO</p>
      </div>
      <div className="space-y-2">
        {alerts.map((a) => {
          const sc = a.severity === "critical" ? "#ff4d1c" : a.severity === "high" ? "#ffd700" : "#00c8ff";
          return (
            <div key={a.id} className="flex items-center gap-4 rounded-lg p-4 border" style={{ background: "#0f1018", borderColor: `${sc}18`, borderLeft: `3px solid ${sc}` }}>
              <div className="px-2 py-1 rounded text-xs flex-shrink-0" style={{ background: `${sc}15`, color: sc, fontFamily: "'JetBrains Mono', monospace", fontSize: "10px" }}>
                {a.type}
              </div>
              <div className="flex-1">
                <span style={{ color: "#e8eaf0", fontSize: "13px", fontWeight: 500 }}>{a.crime}</span>
                <span className="text-muted-foreground mx-2" style={{ fontSize: "12px" }}>·</span>
                <span className="text-muted-foreground" style={{ fontSize: "12px" }}>{a.district}</span>
                <div style={{ color: "#a8adc0", fontSize: "11px", marginTop: 2 }}>{a.detail}</div>
              </div>
              <div className="text-muted-foreground flex-shrink-0" style={{ fontSize: "11px" }}>{a.time}</div>
              <button className="px-3 py-1.5 rounded border text-xs flex-shrink-0" style={{ background: "transparent", borderColor: "rgba(255,255,255,0.08)", color: "#6b7094" }}>
                Review
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function App() {
  {/* MARKER-MAKE-KIT-INVOKED */}
  const [activeView, setActiveView] = useState("overview");

  const renderView = () => {
    switch (activeView) {
      case "overview": return <OverviewDashboard />;
      case "chat": return <CrimeAIChat />;
      case "network": return <CriminalNetwork />;
      case "heatmap": return <CrimeMap />;
      case "analytics": return <PatternAnalytics />;
      case "profiling": return <OffenderProfiling />;
      case "forecast": return <ForecastPlaceholder />;
      case "financial": return <FinancialPlaceholder />;
      case "alerts": return <AlertsView />;
      default: return <OverviewDashboard />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "#09090f" }}>
      <Sidebar activeView={activeView} onViewChange={setActiveView} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-border flex-shrink-0" style={{ background: "#09090f" }}>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground" style={{ fontSize: "12px", fontFamily: "'JetBrains Mono', monospace" }}>KSP / SCRB</span>
            <span className="text-muted-foreground">/</span>
            <span style={{ color: "#e8eaf0", fontSize: "12px" }}>{VIEW_TITLES[activeView] ?? "Overview"}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2" style={{ color: "#6b7094" }} />
              <input
                placeholder="Search FIR, accused, case..."
                className="pl-7 pr-3 py-1.5 rounded border border-border text-xs"
                style={{ background: "#13141f", color: "#e8eaf0", width: 200 }}
              />
            </div>
            <button className="relative p-1.5 rounded border border-border" style={{ color: "#6b7094" }} onClick={() => setActiveView("alerts")}>
              <Bell size={15} />
              <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full flex items-center justify-center text-white" style={{ background: "#ff4d1c", fontSize: "8px" }}>7</span>
            </button>
            <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-border" style={{ fontSize: "10px" }}>
              <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "#10b981" }} />
              <span className="text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace" }}>SECURE SESSION</span>
            </div>
          </div>
        </header>

        {/* Page */}
        <main className="flex-1 overflow-y-auto px-6 py-5">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
