import { useState, useRef, useEffect } from "react";
import { Search, ZoomIn, ZoomOut, Filter, Download, Info } from "lucide-react";

interface Node {
  id: string;
  label: string;
  type: "accused" | "victim" | "location" | "financial" | "gang";
  incidents: number;
  x: number;
  y: number;
  radius: number;
}

interface Edge {
  from: string;
  to: string;
  label: string;
  weight: number;
}

const NODES: Node[] = [
  { id: "n1", label: "Ravi K.", type: "accused", incidents: 14, x: 380, y: 220, radius: 22 },
  { id: "n2", label: "Suresh M.", type: "accused", incidents: 9, x: 260, y: 160, radius: 18 },
  { id: "n3", label: "Anwar H.", type: "accused", incidents: 7, x: 500, y: 140, radius: 16 },
  { id: "n4", label: "Kumar B.", type: "accused", incidents: 5, x: 320, y: 320, radius: 14 },
  { id: "n5", label: "Ganesh P.", type: "accused", incidents: 4, x: 460, y: 310, radius: 13 },
  { id: "n6", label: "Whitefield PS", type: "location", incidents: 11, x: 180, y: 250, radius: 16 },
  { id: "n7", label: "Electronic City", type: "location", incidents: 8, x: 570, y: 240, radius: 15 },
  { id: "n8", label: "HDFC0012345", type: "financial", incidents: 0, x: 380, y: 380, radius: 14 },
  { id: "n9", label: "Victim Group A", type: "victim", incidents: 0, x: 160, y: 370, radius: 12 },
  { id: "n10", label: "Victim Group B", type: "victim", incidents: 0, x: 560, y: 380, radius: 12 },
  { id: "n11", label: "UPI Fraud Gang", type: "gang", incidents: 31, x: 380, y: 100, radius: 24 },
  { id: "n12", label: "Rajajinagar Hub", type: "location", incidents: 6, x: 230, y: 80, radius: 13 },
];

const EDGES: Edge[] = [
  { from: "n1", to: "n11", label: "member", weight: 3 },
  { from: "n2", to: "n11", label: "member", weight: 2 },
  { from: "n3", to: "n11", label: "member", weight: 2 },
  { from: "n1", to: "n2", label: "co-accused", weight: 2 },
  { from: "n1", to: "n3", label: "co-accused", weight: 2 },
  { from: "n1", to: "n4", label: "associate", weight: 1 },
  { from: "n1", to: "n8", label: "financial", weight: 2 },
  { from: "n2", to: "n8", label: "financial", weight: 2 },
  { from: "n1", to: "n6", label: "operates", weight: 2 },
  { from: "n3", to: "n7", label: "operates", weight: 2 },
  { from: "n4", to: "n6", label: "operates", weight: 1 },
  { from: "n5", to: "n7", label: "operates", weight: 1 },
  { from: "n9", to: "n6", label: "victimized", weight: 1 },
  { from: "n10", to: "n7", label: "victimized", weight: 1 },
  { from: "n11", to: "n12", label: "base", weight: 2 },
  { from: "n1", to: "n12", label: "address", weight: 1 },
  { from: "n2", to: "n12", label: "address", weight: 1 },
];

const NODE_COLORS: Record<string, string> = {
  accused: "#ff4d1c",
  victim: "#10b981",
  location: "#00c8ff",
  financial: "#ffd700",
  gang: "#7c3aed",
};

const EDGE_COLORS: Record<string, string> = {
  "co-accused": "#ff4d1c",
  financial: "#ffd700",
  member: "#7c3aed",
  operates: "#00c8ff",
  victimized: "#10b981",
  base: "#7c3aed",
  address: "#a8adc0",
  associate: "#ff9944",
};

export function CriminalNetwork() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [zoom, setZoom] = useState(1);
  const [filter, setFilter] = useState<string | null>(null);

  const filteredNodes = filter ? NODES.filter(n => n.type === filter) : NODES;
  const filteredEdges = EDGES.filter(e =>
    filteredNodes.find(n => n.id === e.from) && filteredNodes.find(n => n.id === e.to)
  );

  const nodeMap = Object.fromEntries(NODES.map(n => [n.id, n]));

  return (
    <div className="flex flex-col gap-4" style={{ height: "calc(100vh - 88px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div>
          <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
            CRIMINAL NETWORK ANALYSIS
          </h1>
          <p className="text-muted-foreground text-sm">UPI Fraud Gang · BU-2026-CF · {NODES.length} nodes · {EDGES.length} connections</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2" style={{ color: "#6b7094" }} />
            <input
              placeholder="Search node..."
              className="pl-7 pr-3 py-1.5 rounded border border-border text-sm"
              style={{ background: "#13141f", color: "#e8eaf0", width: 160 }}
            />
          </div>
          <button onClick={() => setZoom(z => Math.min(z + 0.2, 2))} className="p-1.5 rounded border border-border" style={{ color: "#6b7094" }}>
            <ZoomIn size={14} />
          </button>
          <button onClick={() => setZoom(z => Math.max(z - 0.2, 0.5))} className="p-1.5 rounded border border-border" style={{ color: "#6b7094" }}>
            <ZoomOut size={14} />
          </button>
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded border border-border text-sm" style={{ color: "#a8adc0" }}>
            <Download size={13} />
            Export
          </button>
        </div>
      </div>

      <div className="flex gap-4 flex-1 min-h-0">
        {/* Graph Canvas */}
        <div className="flex-1 rounded-lg border border-border overflow-hidden relative" style={{ background: "#0a0b14" }}>
          {/* Filter bar */}
          <div className="absolute top-3 left-3 flex gap-1.5 z-10">
            {[null, "accused", "victim", "location", "financial", "gang"].map((f) => (
              <button
                key={f ?? "all"}
                onClick={() => setFilter(f)}
                className="px-2 py-1 rounded text-xs transition-all"
                style={{
                  background: filter === f ? (f ? `${NODE_COLORS[f]}20` : "rgba(255,255,255,0.1)") : "rgba(0,0,0,0.5)",
                  color: filter === f ? (f ? NODE_COLORS[f] : "#e8eaf0") : "#6b7094",
                  border: `1px solid ${filter === f ? (f ? `${NODE_COLORS[f]}40` : "rgba(255,255,255,0.2)") : "rgba(255,255,255,0.06)"}`,
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: "10px",
                }}
              >
                {f ? f.toUpperCase() : "ALL"}
              </button>
            ))}
          </div>

          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            viewBox="0 0 760 480"
            style={{ transform: `scale(${zoom})`, transformOrigin: "center", transition: "transform 0.2s" }}
          >
            <defs>
              {Object.entries(EDGE_COLORS).map(([key, color]) => (
                <marker
                  key={key}
                  id={`arrow-${key}`}
                  markerWidth="6"
                  markerHeight="6"
                  refX="5"
                  refY="3"
                  orient="auto"
                >
                  <path d="M0,0 L0,6 L6,3 z" fill={color} fillOpacity={0.6} />
                </marker>
              ))}
            </defs>

            {/* Edges */}
            {filteredEdges.map((edge, i) => {
              const from = nodeMap[edge.from];
              const to = nodeMap[edge.to];
              if (!from || !to) return null;
              const color = EDGE_COLORS[edge.label] ?? "#4a4f6b";
              const midX = (from.x + to.x) / 2;
              const midY = (from.y + to.y) / 2;
              return (
                <g key={i}>
                  <line
                    x1={from.x}
                    y1={from.y}
                    x2={to.x}
                    y2={to.y}
                    stroke={color}
                    strokeWidth={edge.weight}
                    strokeOpacity={0.35}
                    markerEnd={`url(#arrow-${edge.label})`}
                  />
                  <text x={midX} y={midY} fill={color} fillOpacity={0.5} style={{ fontSize: "8px", fontFamily: "'JetBrains Mono', monospace" }} textAnchor="middle">
                    {edge.label}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {filteredNodes.map((node) => {
              const color = NODE_COLORS[node.type];
              const isSelected = selectedNode?.id === node.id;
              return (
                <g
                  key={node.id}
                  onClick={() => setSelectedNode(isSelected ? null : node)}
                  style={{ cursor: "pointer" }}
                >
                  {isSelected && (
                    <circle cx={node.x} cy={node.y} r={node.radius + 6} fill={color} fillOpacity={0.1} stroke={color} strokeWidth={1} strokeDasharray="3 2" />
                  )}
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={node.radius}
                    fill={color}
                    fillOpacity={isSelected ? 0.25 : 0.12}
                    stroke={color}
                    strokeWidth={isSelected ? 2 : 1.5}
                    strokeOpacity={isSelected ? 1 : 0.7}
                  />
                  {node.incidents > 0 && (
                    <text x={node.x} y={node.y + 1} fill={color} textAnchor="middle" dominantBaseline="middle" style={{ fontSize: node.radius > 16 ? "10px" : "9px", fontFamily: "'JetBrains Mono', monospace", fontWeight: 600 }}>
                      {node.incidents}
                    </text>
                  )}
                  <text x={node.x} y={node.y + node.radius + 11} fill="#a8adc0" textAnchor="middle" style={{ fontSize: "9px", fontFamily: "'Inter', sans-serif" }}>
                    {node.label}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Side Panel */}
        <div className="w-56 flex flex-col gap-3 flex-shrink-0">
          {/* Legend */}
          <div className="rounded-lg p-3 border border-border" style={{ background: "#0f1018" }}>
            <div className="text-xs font-medium text-muted-foreground mb-2.5" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
              NODE TYPES
            </div>
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2 py-1">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: color }} />
                <span className="capitalize text-xs" style={{ color: "#a8adc0" }}>{type}</span>
              </div>
            ))}
          </div>

          {/* Node Detail */}
          {selectedNode ? (
            <div className="rounded-lg p-3 border border-border flex-1" style={{ background: "#0f1018", borderColor: `${NODE_COLORS[selectedNode.type]}30` }}>
              <div className="text-xs font-medium text-muted-foreground mb-3" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
                NODE DETAILS
              </div>
              <div
                className="inline-flex px-2 py-0.5 rounded mb-3 text-xs uppercase"
                style={{ background: `${NODE_COLORS[selectedNode.type]}15`, color: NODE_COLORS[selectedNode.type], fontFamily: "'JetBrains Mono', monospace", fontSize: "10px" }}
              >
                {selectedNode.type}
              </div>
              <div style={{ color: "#e8eaf0", fontWeight: 600, marginBottom: 8 }}>{selectedNode.label}</div>
              {selectedNode.incidents > 0 && (
                <div className="flex items-center justify-between py-2 border-t border-border">
                  <span className="text-muted-foreground text-xs">Incidents</span>
                  <span style={{ color: NODE_COLORS[selectedNode.type], fontFamily: "'JetBrains Mono', monospace", fontSize: "13px", fontWeight: 700 }}>
                    {selectedNode.incidents}
                  </span>
                </div>
              )}
              <div className="py-2 border-t border-border">
                <div className="text-muted-foreground text-xs mb-1.5">Connected nodes</div>
                {EDGES.filter(e => e.from === selectedNode.id || e.to === selectedNode.id).slice(0, 5).map((e, i) => {
                  const other = nodeMap[e.from === selectedNode.id ? e.to : e.from];
                  if (!other) return null;
                  return (
                    <div key={i} className="flex items-center gap-2 py-1">
                      <span className="w-1.5 h-1.5 rounded-full" style={{ background: NODE_COLORS[other.type] }} />
                      <span style={{ color: "#a8adc0", fontSize: "11px" }}>{other.label}</span>
                      <span style={{ color: EDGE_COLORS[e.label] ?? "#6b7094", fontSize: "9px", marginLeft: "auto", fontFamily: "'JetBrains Mono', monospace" }}>{e.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="rounded-lg p-4 border border-border flex-1 flex flex-col items-center justify-center" style={{ background: "#0f1018" }}>
              <Info size={22} style={{ color: "#2d2f45" }} />
              <p className="text-muted-foreground text-xs text-center mt-2">Click any node to view details</p>
            </div>
          )}

          {/* Stats */}
          <div className="rounded-lg p-3 border border-border" style={{ background: "#0f1018" }}>
            <div className="text-xs font-medium text-muted-foreground mb-2" style={{ fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em" }}>
              NETWORK STATS
            </div>
            {[
              { label: "Total nodes", value: NODES.length },
              { label: "Connections", value: EDGES.length },
              { label: "Key suspects", value: 5 },
              { label: "Jurisdictions", value: 3 },
            ].map(s => (
              <div key={s.label} className="flex items-center justify-between py-1 border-b border-border last:border-0">
                <span className="text-muted-foreground text-xs">{s.label}</span>
                <span style={{ color: "#e8eaf0", fontFamily: "'JetBrains Mono', monospace", fontSize: "12px" }}>{s.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
