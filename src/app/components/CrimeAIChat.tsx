import { useState, useRef, useEffect } from "react";
import { Send, Mic, Download, RefreshCw, ChevronDown, Sparkles, FileText, Network, MapPin } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  citations?: string[];
  confidence?: number;
  followups?: string[];
}

const SAMPLE_MESSAGES: Message[] = [
  {
    id: "1",
    role: "user",
    content: "Show me crime trends in Bengaluru Urban district for the last 6 months",
    timestamp: new Date(Date.now() - 120000),
  },
  {
    id: "2",
    role: "assistant",
    content: `**Analysis: Bengaluru Urban Crime Trends (Jan–Jun 2026)**

Bengaluru Urban has recorded **4,820 FIRs** in the first half of 2026, representing a **12.4% increase** year-over-year. Key findings:

- **Cyber Fraud** is the fastest-growing category (+34%), concentrated in Whitefield, Electronic City, and Marathahalli police station jurisdictions
- **Chain snatching** incidents have spiked 28% since March, predominantly targeting women commuters near metro stations
- **Property crimes** show a seasonal dip in summer months (May–Jun) consistent with 3-year patterns

Three organized groups are linked to 61 of the cyber fraud cases. Network analysis suggests a hub node (Accused ID: KAR-2024-08841) operating from Rajajinagar with 12 direct co-offender connections.

*Confidence: 94.2% · Source: CCTNS FIR Database, 6,241 records analyzed*`,
    timestamp: new Date(Date.now() - 115000),
    citations: ["CCTNS FIR Database Q1-Q2 2026", "KSP Beat Patrol Reports", "Cyber Crime Cell Karnataka"],
    confidence: 94.2,
    followups: [
      "Who are the repeat offenders in the cyber fraud cluster?",
      "Show the network graph of accused KAR-2024-08841",
      "Which police stations have the highest workload?",
    ],
  },
  {
    id: "3",
    role: "user",
    content: "Who are the repeat offenders in the cyber fraud cluster?",
    timestamp: new Date(Date.now() - 60000),
  },
  {
    id: "4",
    role: "assistant",
    content: `**Repeat Offender Profile — Cyber Fraud Cluster BU-2026-CF**

Identified **7 repeat accused** with 3+ linked incidents:

| Accused ID | Name | Incidents | Districts | Status |
|---|---|---|---|---|
| KAR-2024-08841 | Ravi K. | 14 | BU, MYS | Bail |
| KAR-2025-01234 | [Redacted] | 9 | BU | Undertrial |
| KAR-2025-04567 | [Redacted] | 7 | BU, DK | Absconding |
| KAR-2023-99012 | [Redacted] | 5 | BU | Convicted |

**MO Analysis:** All incidents share a phishing-via-UPI vector. Victim profile: urban professionals aged 28–45, first contact via WhatsApp or OLX. Average loss per incident: ₹1.2 lakh.

**Hidden Association:** KAR-2024-08841 and KAR-2025-01234 share a common financial account (IFSC flagged: HDFC0012345) used for fund laundering — detected via transaction graph analysis.

*Confidence: 91.7% · 4 data sources · Explainable AI: feature weights visible*`,
    timestamp: new Date(Date.now() - 55000),
    citations: ["CCTNS Accused Database", "Financial Intelligence Unit", "Cyber Crime Cell FIR Archive"],
    confidence: 91.7,
    followups: [
      "Show financial transaction network for HDFC0012345",
      "Generate case summary PDF for KAR-2024-08841",
      "What investigative leads are available?",
    ],
  },
];

const SUGGESTED_QUERIES = [
  { icon: MapPin, text: "Crime hotspots in Mysuru last 30 days" },
  { icon: Network, text: "Show gang network for Ballari organized crime" },
  { icon: FileText, text: "Generate FIR summary for case KA-2026-45231" },
  { icon: Sparkles, text: "Predict high-risk areas for next week" },
];

export function CrimeAIChat() {
  const [messages, setMessages] = useState<Message[]>(SAMPLE_MESSAGES);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [lang, setLang] = useState<"EN" | "KN">("EN");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const sendMessage = () => {
    if (!input.trim()) return;
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `**Query Processed: "${input.substring(0, 60)}${input.length > 60 ? "..." : ""}"**\n\nAnalyzing Karnataka State Police crime database... Found **2,847 matching records** across 12 districts.\n\nThis is a demonstration response. In a production deployment, this would connect to the live CCTNS database and provide real-time intelligence analysis with citations and confidence scores.\n\n*Confidence: 87.3% · Powered by KSP Crime AI · Audit logged*`,
        timestamp: new Date(),
        citations: ["CCTNS Live Feed", "KSP Intelligence Database"],
        confidence: 87.3,
        followups: ["Drill down by district", "Show network connections", "Export analysis"],
      };
      setMessages((prev) => [...prev, aiMsg]);
    }, 2200);
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderMarkdown = (text: string) => {
    return text
      .split("\n")
      .map((line, i) => {
        if (line.startsWith("**") && line.endsWith("**") && !line.includes(" **")) {
          return <div key={i} className="font-semibold mt-3 mb-1" style={{ color: "#e8eaf0" }}>{line.slice(2, -2)}</div>;
        }
        if (line.startsWith("- ")) {
          return (
            <div key={i} className="flex gap-2 my-0.5">
              <span style={{ color: "#00c8ff", flexShrink: 0 }}>·</span>
              <span dangerouslySetInnerHTML={{ __html: formatInline(line.slice(2)) }} />
            </div>
          );
        }
        if (line.startsWith("| ")) {
          const cells = line.split("|").filter(Boolean).map(c => c.trim());
          if (cells[0] === "---" || cells[0] === "---|") return null;
          const isHeader = i > 0 && text.split("\n")[i - 1]?.startsWith("| Accused");
          return (
            <div key={i} className="flex gap-0 text-xs border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
              {cells.map((cell, ci) => (
                <div key={ci} className={`flex-1 py-1.5 px-2 ${isHeader ? "text-muted-foreground" : ""}`}
                  style={{ color: ci === 4 && cell === "Bail" ? "#ffd700" : ci === 4 && cell === "Absconding" ? "#ff4d1c" : undefined }}>
                  {cell}
                </div>
              ))}
            </div>
          );
        }
        if (line.startsWith("*") && line.endsWith("*") && !line.startsWith("**")) {
          return <div key={i} className="text-muted-foreground mt-2" style={{ fontSize: "11px" }}>{line.slice(1, -1)}</div>;
        }
        if (line.trim() === "") return <div key={i} className="h-1" />;
        return <div key={i} dangerouslySetInnerHTML={{ __html: formatInline(line) }} />;
      });
  };

  const formatInline = (text: string) =>
    text.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#e8eaf0">$1</strong>');

  return (
    <div className="flex flex-col h-full" style={{ height: "calc(100vh - 88px)" }}>
      {/* Header */}
      <div className="flex items-center justify-between pb-4 flex-shrink-0">
        <div>
          <h1 style={{ fontFamily: "'Barlow Condensed', sans-serif", fontSize: "26px", fontWeight: 700, letterSpacing: "0.04em", color: "#e8eaf0" }}>
            CRIME AI INTELLIGENCE CHAT
          </h1>
          <p className="text-muted-foreground text-sm">Natural language queries · English & Kannada · Audit logged</p>
        </div>
        <div className="flex items-center gap-2">
          {(["EN", "KN"] as const).map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className="px-2.5 py-1 rounded text-xs transition-all"
              style={{
                background: lang === l ? "rgba(0,200,255,0.12)" : "transparent",
                color: lang === l ? "#00c8ff" : "#6b7094",
                border: lang === l ? "1px solid rgba(0,200,255,0.3)" : "1px solid rgba(255,255,255,0.08)",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              {l}
            </button>
          ))}
          <button
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs border border-border"
            style={{ color: "#a8adc0" }}
          >
            <Download size={12} />
            Save PDF
          </button>
          <button className="p-1.5 rounded border border-border" style={{ color: "#6b7094" }}>
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1" style={{ minHeight: 0 }}>
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div
                className="w-7 h-7 rounded flex-shrink-0 flex items-center justify-center mr-3 mt-1"
                style={{ background: "linear-gradient(135deg, rgba(0,200,255,0.15), rgba(0,200,255,0.05))", border: "1px solid rgba(0,200,255,0.25)", flexShrink: 0 }}
              >
                <Sparkles size={13} style={{ color: "#00c8ff" }} />
              </div>
            )}
            <div className={`max-w-2xl ${msg.role === "user" ? "max-w-lg" : ""}`}>
              <div
                className="rounded-lg px-4 py-3 text-sm leading-relaxed"
                style={{
                  background: msg.role === "user" ? "rgba(0,200,255,0.1)" : "#13141f",
                  border: msg.role === "user" ? "1px solid rgba(0,200,255,0.2)" : "1px solid rgba(255,255,255,0.06)",
                  color: "#c8ccd8",
                }}
              >
                {msg.role === "assistant" ? (
                  <div className="space-y-0.5">{renderMarkdown(msg.content)}</div>
                ) : (
                  msg.content
                )}
              </div>

              {msg.role === "assistant" && msg.confidence && (
                <div className="flex items-center gap-3 mt-2 ml-1">
                  <div className="flex items-center gap-1.5">
                    <div className="w-16 h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.08)" }}>
                      <div className="h-full rounded-full" style={{ width: `${msg.confidence}%`, background: "#10b981" }} />
                    </div>
                    <span className="text-muted-foreground" style={{ fontSize: "10px", fontFamily: "'JetBrains Mono', monospace" }}>
                      {msg.confidence}% confidence
                    </span>
                  </div>
                  {msg.citations?.map((c, i) => (
                    <span key={i} className="px-1.5 py-0.5 rounded" style={{ background: "rgba(255,255,255,0.04)", color: "#6b7094", fontSize: "9px" }}>
                      {c}
                    </span>
                  ))}
                </div>
              )}

              {msg.role === "assistant" && msg.followups && (
                <div className="flex flex-wrap gap-1.5 mt-2 ml-1">
                  {msg.followups.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => { setInput(q); }}
                      className="flex items-center gap-1 px-2 py-1 rounded border transition-all hover:border-border/60"
                      style={{ background: "#0f1018", borderColor: "rgba(255,255,255,0.07)", color: "#6b7094", fontSize: "10px" }}
                    >
                      <ChevronDown size={9} />
                      {q}
                    </button>
                  ))}
                </div>
              )}

              <div className="mt-1 ml-1 text-muted-foreground" style={{ fontSize: "9px", fontFamily: "'JetBrains Mono', monospace" }}>
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center gap-3">
            <div
              className="w-7 h-7 rounded flex-shrink-0 flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, rgba(0,200,255,0.15), rgba(0,200,255,0.05))", border: "1px solid rgba(0,200,255,0.25)" }}
            >
              <Sparkles size={13} style={{ color: "#00c8ff" }} />
            </div>
            <div className="rounded-lg px-4 py-3" style={{ background: "#13141f", border: "1px solid rgba(255,255,255,0.06)" }}>
              <div className="flex items-center gap-1.5">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="w-1.5 h-1.5 rounded-full animate-pulse"
                    style={{ background: "#00c8ff", animationDelay: `${i * 0.2}s` }}
                  />
                ))}
                <span className="text-muted-foreground ml-1" style={{ fontSize: "11px" }}>Analyzing crime database...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 4 && (
        <div className="flex gap-2 py-3 flex-shrink-0 flex-wrap">
          {SUGGESTED_QUERIES.map((q) => {
            const Icon = q.icon;
            return (
              <button
                key={q.text}
                onClick={() => setInput(q.text)}
                className="flex items-center gap-2 px-3 py-2 rounded border transition-all"
                style={{ background: "#0f1018", borderColor: "rgba(255,255,255,0.07)", color: "#a8adc0", fontSize: "11px" }}
              >
                <Icon size={12} style={{ color: "#00c8ff" }} />
                {q.text}
              </button>
            );
          })}
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 pt-2">
        <div
          className="flex items-end gap-2 rounded-lg p-3 border"
          style={{ background: "#13141f", borderColor: "rgba(0,200,255,0.15)" }}
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder={lang === "EN" ? "Ask anything about crime data, FIRs, accused, patterns..." : "ಅಪರಾಧ ಡೇಟಾ, ಎಫ್‌ಐಆರ್‌ಗಳ ಬಗ್ಗೆ ಕೇಳಿ..."}
            rows={1}
            className="flex-1 resize-none bg-transparent outline-none text-sm"
            style={{ color: "#e8eaf0", caretColor: "#00c8ff", maxHeight: "100px" }}
          />
          <div className="flex items-center gap-2 flex-shrink-0">
            <button className="p-2 rounded transition-colors" style={{ color: "#6b7094" }}>
              <Mic size={16} />
            </button>
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isTyping}
              className="p-2 rounded transition-all"
              style={{
                background: input.trim() && !isTyping ? "#00c8ff" : "rgba(0,200,255,0.1)",
                color: input.trim() && !isTyping ? "#09090f" : "#6b7094",
              }}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
        <div className="text-center mt-1.5 text-muted-foreground" style={{ fontSize: "9px" }}>
          All queries are audit logged · AI responses include data citations · Not for judicial use without verification
        </div>
      </div>
    </div>
  );
}
