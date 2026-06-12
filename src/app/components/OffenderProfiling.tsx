import { useState } from "react";
import { Search, User, MapPin, Calendar, AlertTriangle, FileText, Network, ChevronRight } from "lucide-react";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const offenders = [
  {
    id: "KAR-2024-08841",
    name: "Ravi Kumar",
    alias: ["Ravi Hacker", "RK Online"],
    age: 34,
    gender: "Male",
    district: "Bengaluru Urban",
    ps: "Rajajinagar",
    incidents: 14,
    status: "On Bail",
    category: "Cyber",
    riskScore: 87,
    lastKnown: "Rajajinagar, Bengaluru",
    firstOffence: "2019-03-14",
    modus: "UPI Phishing, WhatsApp Impersonation",
    associates: ["KAR-2025-01234", "KAR-2025-04567"],
    profile: { aggression: 32, sophistication: 85, recidivism: 91, network: 78, mobility: 54, financial: 88 },
    timeline: [
      { year: "2019", incidents: 1 }, { year: "2020", incidents: 2 },
      { year: "2021", incidents: 1 }, { year: "2022", incidents: 3 },
      { year: "2023", incidents: 3 }, { year: "2024", incidents: 4 },
    ],
  },
  {
    id: "KAR-2023-05511",
    name: "Muthuraja S.",
    alias: ["Mutha", "King Raju"],
    age: 28,
    gender: "Male",
    district: "Ballari",
    ps: "Nandihalli",
    incidents: 9,
    status: "Absconding",
    category: "Violent",
    riskScore: 94,
    lastKnown: "Last seen Ballari, Jun 2026",
    firstOffence: "2021-07-02",
    modus: "Extortion, Assault, Gang-related violence",
    associates: ["KAR-2022-11203"],
    profile: { aggression: 95, sophistication: 42, recidivism: 88, network: 72, mobility: 81, financial: 38 },
    timeline: [
      { year: "2019", incidents: 0 }, { year: "2020", incidents: 0 },
      { year: "2021", incidents: 1 }, { year: "2022", incidents: 2 },
      { year: "2023", incidents: 3 }, { year: "2024", incidents: 3 },
    ],
  },
  {
    id: "KAR-2020-33891",
    name: "Venkatesh R.",
    alias: ["Venki Finance"],
    age: 45,
    gender: "Male",
    district: "Mysuru",
    ps: "Hebbal",
    incidents: 7,
    status: "Convicted",
    category: "Economic",
    riskScore: 62,
    lastKnown: "Mysuru Central Prison",
    firstOffence: "2015-11-22",
    modus: "Chit fund fraud, Property forgery",
    associates: ["KAR-2019-88231", "KAR-2021-44102"],
    profile: { aggression: 18, sophistication: 76, recidivism: 65, network: 55, mobility: 30, financial: 93 },
    timeline: [
      { year: "2019", incidents: 2 }, { year: "2020", incidents: 1 },
      { year: "2021", incidents: 2 }, { year: "2022", incidents: 1 },
      { year: "2023", incidents: 1 }, { year: "2024", incidents: 0 },
    ],
  },
];

const STATUS_STYLES: Record<string, { bg: string; color: string }> = {
  "On Bail": { bg: "rgba(255,215,0,0.12)", color: "#ffd700" },
  "Absconding": { bg: "rgba(255,77,28,0.12)", color: "#ff4d1c" },
  "Convicted": { bg: "rgba(16,185,129,0.12)", color: "#10b981" },
  "Undertrial": { bg: "rgba(0,200,255,0.12)", color: "#00c8ff" },
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded border border-border p-2" style={{ background: "#13141f", fontSize: "11px" }}>
      <div style={{ color: "#a8adc0" }}>{label}</div>
      <div style={{ color: "#00c8ff" }}>Incidents: {payload[0]?.value}</div>
    </div>
  );
};

export function OffenderProfiling() {
  const [selected, setSelected] = useState(offenders[0]);
  const [search, setSearch] = useState("");

  const filtered = offenders.filter(o =>
    o.name.toLowerCase().includes(search.toLowerCase()) ||
    o.id.toLowerCase().includes(search.toLowerCase())
  );

  const radarData = Object.entries(selected.profile).map(([key, val]) => ({
    subject: key.charAt(0).toUpperCase() + key.slice(1),
    value: val,
  }));

  const riskColor = selected.riskScore >= 85 ? "#ff4d1c" : selected.riskScore >= 65 ? "#ffd700" : "#10b981";

  return (
    <div className="flex flex-col gap-4" style={{ height: "calc(100vh - 88px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
            OFFENDER PROFILING SYSTEM
          </h1>
          <p className="text-muted-foreground text-sm">Criminology-based profiling · Repeat offender tracking · MO analysis</p>
        </div>
      </div>

      <div className="flex gap-4 flex-1 min-h-0">
        {/* Offender List */}
        <div className="w-56 flex flex-col gap-2 flex-shrink-0">
          <div className="relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2" style={{ color: "#6b7094" }} />
            <input
              placeholder="Search offender..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-7 pr-3 py-2 rounded border border-border text-xs"
              style={{ background: "#13141f", color: "#e8eaf0" }}
            />
          </div>
          <div className="space-y-2 overflow-y-auto flex-1">
            {filtered.map((o) => {
              const isActive = selected.id === o.id;
              const rc = o.riskScore >= 85 ? "#ff4d1c" : o.riskScore >= 65 ? "#ffd700" : "#10b981";
              return (
                <button
                  key={o.id}
                  onClick={() => setSelected(o)}
                  className="w-full text-left rounded-lg p-3 border transition-all"
                  style={{
                    background: isActive ? "#13141f" : "#0f1018",
                    borderColor: isActive ? "rgba(0,200,255,0.25)" : "rgba(255,255,255,0.06)",
                  }}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div
                      className="w-8 h-8 rounded flex-shrink-0 flex items-center justify-center"
                      style={{ background: `${rc}15`, border: `1px solid ${rc}30` }}
                    >
                      <User size={14} style={{ color: rc }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div style={{ color: "#e8eaf0", fontSize: "12px", fontWeight: 500 }} className="truncate">{o.name}</div>
                      <div style={{ color: "#6b7094", fontSize: "9px", fontFamily: "'JetBrains Mono', monospace" }}>{o.id}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <div
                      className="text-xs px-1.5 py-0.5 rounded"
                      style={{ ...STATUS_STYLES[o.status], fontSize: "9px", fontFamily: "'JetBrains Mono', monospace" }}
                    >
                      {o.status.toUpperCase()}
                    </div>
                    <div className="ml-auto flex items-center gap-1">
                      <span style={{ color: rc, fontFamily: "'JetBrains Mono', monospace", fontSize: "11px", fontWeight: 700 }}>{o.riskScore}</span>
                      <span className="text-muted-foreground" style={{ fontSize: "9px" }}>risk</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Profile Detail */}
        <div className="flex-1 overflow-y-auto space-y-3">
          {/* Header Card */}
          <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
            <div className="flex items-start gap-4">
              <div
                className="w-14 h-14 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: `${riskColor}15`, border: `2px solid ${riskColor}30` }}
              >
                <User size={26} style={{ color: riskColor }} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 flex-wrap">
                  <h2 style={{ color: "#e8eaf0", fontFamily: "'Barlow Condensed', sans-serif", fontSize: "22px", fontWeight: 700 }}>
                    {selected.name}
                  </h2>
                  <div className="px-2 py-0.5 rounded text-xs" style={{ ...STATUS_STYLES[selected.status] }}>
                    {selected.status}
                  </div>
                  <div className="px-2 py-0.5 rounded text-xs" style={{ background: "rgba(0,200,255,0.08)", color: "#00c8ff" }}>
                    {selected.category} Crime
                  </div>
                </div>
                <div className="text-muted-foreground mt-0.5" style={{ fontSize: "11px", fontFamily: "'JetBrains Mono', monospace" }}>{selected.id}</div>
                {selected.alias.length > 0 && (
                  <div className="text-muted-foreground mt-1" style={{ fontSize: "11px" }}>
                    AKA: {selected.alias.join(", ")}
                  </div>
                )}
              </div>
              <div className="flex-shrink-0 text-center">
                <div style={{ fontSize: "40px", fontWeight: 800, color: riskColor, fontFamily: "'Barlow Condensed', sans-serif", lineHeight: 1 }}>
                  {selected.riskScore}
                </div>
                <div className="text-muted-foreground" style={{ fontSize: "9px", fontFamily: "'JetBrains Mono', monospace" }}>RISK SCORE</div>
                <div className="mt-1 w-16 h-1.5 rounded-full overflow-hidden mx-auto" style={{ background: "rgba(255,255,255,0.08)" }}>
                  <div className="h-full rounded-full" style={{ width: `${selected.riskScore}%`, background: riskColor }} />
                </div>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-3 mt-4 pt-4 border-t border-border">
              {[
                { label: "Age", value: `${selected.age} yrs`, icon: Calendar },
                { label: "District", value: selected.district, icon: MapPin },
                { label: "Total Incidents", value: selected.incidents, icon: AlertTriangle },
                { label: "First Offence", value: selected.firstOffence, icon: FileText },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.label}>
                    <div className="flex items-center gap-1.5 mb-1">
                      <Icon size={11} style={{ color: "#6b7094" }} />
                      <span className="text-muted-foreground" style={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace" }}>{item.label.toUpperCase()}</span>
                    </div>
                    <div style={{ color: "#e8eaf0", fontSize: "12px" }}>{item.value}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-2 gap-3">
            {/* Radar */}
            <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
              <div className="text-xs font-medium text-muted-foreground mb-3" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                CRIMINOLOGICAL PROFILE
              </div>
              <ResponsiveContainer width="100%" height={180}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.06)" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: "#6b7094", fontSize: 9 }} />
                  <Radar name="Profile" dataKey="value" stroke={riskColor} fill={riskColor} fillOpacity={0.12} strokeWidth={1.5} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Timeline */}
            <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
              <div className="text-xs font-medium text-muted-foreground mb-3" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                INCIDENT TIMELINE
              </div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={selected.timeline} margin={{ top: 0, right: 5, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="year" tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#6b7094", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="incidents" fill={riskColor} fillOpacity={0.7} radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* MO & Associates */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
              <div className="text-xs font-medium text-muted-foreground mb-3" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                MODUS OPERANDI
              </div>
              <p style={{ color: "#a8adc0", fontSize: "12px", lineHeight: 1.6 }}>{selected.modus}</p>
              <div className="mt-3 pt-3 border-t border-border">
                <div className="text-muted-foreground mb-1.5" style={{ fontSize: "10px" }}>Last known location</div>
                <div className="flex items-center gap-1.5" style={{ color: "#e8eaf0", fontSize: "12px" }}>
                  <MapPin size={12} style={{ color: "#00c8ff" }} />
                  {selected.lastKnown}
                </div>
              </div>
            </div>
            <div className="rounded-lg p-4 border border-border" style={{ background: "#0f1018" }}>
              <div className="flex items-center gap-2 mb-3">
                <Network size={13} style={{ color: "#7c3aed" }} />
                <div className="text-xs font-medium text-muted-foreground" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                  KNOWN ASSOCIATES
                </div>
              </div>
              {selected.associates.map((id) => (
                <div
                  key={id}
                  className="flex items-center justify-between rounded p-2.5 mb-1.5 border border-border cursor-pointer"
                  style={{ background: "#13141f" }}
                >
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: "rgba(124,58,237,0.15)" }}>
                      <User size={11} style={{ color: "#7c3aed" }} />
                    </div>
                    <span style={{ color: "#a8adc0", fontFamily: "'JetBrains Mono', monospace", fontSize: "10px" }}>{id}</span>
                  </div>
                  <ChevronRight size={12} style={{ color: "#6b7094" }} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
