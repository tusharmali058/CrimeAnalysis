import { useState } from "react";
import {
  MessageSquare,
  Network,
  Map,
  BarChart3,
  UserSearch,
  TrendingUp,
  DollarSign,
  Shield,
  AlertTriangle,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  Activity,
} from "lucide-react";

const navItems = [
  { id: "overview", label: "Overview", icon: Activity },
  { id: "chat", label: "Crime AI Chat", icon: MessageSquare },
  { id: "network", label: "Criminal Network", icon: Network },
  { id: "heatmap", label: "Crime Map", icon: Map },
  { id: "analytics", label: "Pattern Analytics", icon: BarChart3 },
  { id: "profiling", label: "Offender Profiling", icon: UserSearch },
  { id: "forecast", label: "Forecasting", icon: TrendingUp },
  { id: "financial", label: "Financial Crime", icon: DollarSign },
];

const bottomItems = [
  { id: "alerts", label: "Alert Centre", icon: AlertTriangle, badge: 7 },
  { id: "settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className="flex flex-col h-screen border-r border-border bg-sidebar transition-all duration-300"
      style={{ width: collapsed ? 64 : 220 }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-4 border-b border-sidebar-border">
        <div
          className="flex-shrink-0 w-8 h-8 rounded flex items-center justify-center"
          style={{ background: "linear-gradient(135deg, #00c8ff22, #00c8ff44)", border: "1px solid #00c8ff66" }}
        >
          <Shield size={16} style={{ color: "#00c8ff" }} />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <div className="text-sidebar-accent-foreground font-semibold text-xs leading-tight" style={{ fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.08em" }}>
              KARNATAKA STATE POLICE
            </div>
            <div className="text-muted-foreground" style={{ fontSize: "10px", letterSpacing: "0.12em" }}>
              CRIME INTELLIGENCE
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-all duration-150 relative group"
              style={{
                color: isActive ? "#00c8ff" : "#6b7094",
                background: isActive ? "rgba(0,200,255,0.07)" : "transparent",
                borderLeft: isActive ? "2px solid #00c8ff" : "2px solid transparent",
              }}
            >
              <Icon size={16} className="flex-shrink-0" />
              {!collapsed && (
                <span className="text-sm font-medium truncate">{item.label}</span>
              )}
              {isActive && !collapsed && (
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{ background: "linear-gradient(90deg, rgba(0,200,255,0.06) 0%, transparent 100%)" }}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="py-3 border-t border-sidebar-border">
        {bottomItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-all duration-150 relative"
              style={{ color: "#6b7094" }}
            >
              <Icon size={16} className="flex-shrink-0" />
              {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
              {item.badge && !collapsed && (
                <span
                  className="ml-auto text-xs px-1.5 py-0.5 rounded"
                  style={{ background: "#ff4d1c", color: "#fff", fontSize: "10px" }}
                >
                  {item.badge}
                </span>
              )}
              {item.badge && collapsed && (
                <span
                  className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full"
                  style={{ background: "#ff4d1c" }}
                />
              )}
            </button>
          );
        })}

        {/* User */}
        <div className="flex items-center gap-3 px-4 py-3 mt-1">
          <div
            className="w-7 h-7 rounded flex-shrink-0 flex items-center justify-center text-xs font-bold"
            style={{ background: "linear-gradient(135deg, #1a1b28, #2d2f45)", color: "#00c8ff", border: "1px solid rgba(0,200,255,0.2)" }}
          >
            AS
          </div>
          {!collapsed && (
            <div className="flex-1 overflow-hidden">
              <div className="text-xs font-medium text-sidebar-accent-foreground truncate">Arjun Sharma</div>
              <div className="text-muted-foreground truncate" style={{ fontSize: "10px" }}>Senior Analyst</div>
            </div>
          )}
          {!collapsed && <LogOut size={14} style={{ color: "#6b7094", flexShrink: 0 }} className="cursor-pointer" />}
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center py-2 transition-colors"
          style={{ color: "#6b7094" }}
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>
    </aside>
  );
}
