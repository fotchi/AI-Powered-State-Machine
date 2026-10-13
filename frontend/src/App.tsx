import { useEffect, useRef, useState } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./queryClient";
import { AuthProvider, useAuth } from "./auth";
import { apiFetch } from "./api";
import Sidebar from "../components/Sidebar";
import SignIn from "../screens/SignIn";
import Dashboard from "../screens/Dashboard";
import ScenarioGeneration from "../screens/ScenarioGeneration";
import ScenarioDetails from "../screens/ScenarioDetails";
import AgentPipeline from "../screens/AgentPipeline";
import GeneratedCode from "../screens/GeneratedCode";
import ValidationResults from "../screens/ValidationResults";
import ScenarioHistory from "../screens/ScenarioHistory";
import StateMachine from "../screens/StateMachine";
import AuditLog from "../screens/AuditLog";

type Screen =
  | "dashboard"
  | "generation"
  | "scenario-details"
  | "pipeline"
  | "state-machine"
  | "code"
  | "validation"
  | "history"
  | "audit-log";

interface RunSummary {
  id: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  scenario_count: number;
  script_count: number;
  error: string | null;
  requirements?: { name?: string; module?: string };
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const screenTitles: Record<Screen, string> = {
  dashboard: "Dashboard",
  generation: "Generate Scenario",
  "scenario-details": "Scenario Details",
  pipeline: "Agent Pipeline",
  "state-machine": "State Machine",
  code: "Generated Code",
  validation: "Validation Results",
  history: "Scenario History",
  "audit-log": "Audit Log",
};

function AppShell() {
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [notifOpen, setNotifOpen] = useState(false);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [runsLoading, setRunsLoading] = useState(false);
  const [runsError, setRunsError] = useState("");
  const notifRef = useRef<HTMLDivElement>(null);

  const navigate = (s: string) => {
    if (s in screenTitles) setScreen(s as Screen);
  };

  useEffect(() => {
    if (!notifOpen) return;
    const onClickAway = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener("mousedown", onClickAway);
    return () => document.removeEventListener("mousedown", onClickAway);
  }, [notifOpen]);

  const toggleNotifications = async () => {
    const next = !notifOpen;
    setNotifOpen(next);
    if (!next) return;
    setRunsLoading(true);
    setRunsError("");
    try {
      const res = await apiFetch("/runs");
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const data: RunSummary[] = await res.json();
      setRuns(data.slice(0, 8));
    } catch {
      setRunsError("Could not load recent activity.");
    } finally {
      setRunsLoading(false);
    }
  };

  const renderScreen = () => {
    switch (screen) {
      case "dashboard": return <Dashboard onNavigate={navigate} />;
      case "generation": return <ScenarioGeneration onNavigate={navigate} />;
      case "scenario-details": return <ScenarioDetails onNavigate={navigate} />;
      case "pipeline": return <AgentPipeline onNavigate={navigate} />;
      case "state-machine": return <StateMachine onNavigate={navigate} />;
      case "code": return <GeneratedCode onNavigate={navigate} />;
      case "validation": return <ValidationResults onNavigate={navigate} />;
      case "history": return <ScenarioHistory onNavigate={navigate} />;
      case "audit-log": return <AuditLog />;
      default: return <Dashboard onNavigate={navigate} />;
    }
  };

  return (
    <div className="flex h-full" style={{ fontFamily: "var(--font-body)", background: "var(--color-bg)" }}>
      <Sidebar current={screen} onNavigate={navigate} />

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="border-b px-8 py-3 flex items-center justify-between flex-shrink-0" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)" }}>
          <div className="flex items-center gap-3">
            <h2
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
              className="font-semibold text-[15px]"
            >
              {screenTitles[screen]}
            </h2>
          </div>
          <div className="flex items-center gap-3">
            {/* Notification bell -- opens a dropdown of recent pipeline runs */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={toggleNotifications}
                className="relative w-8 h-8 rounded-lg flex items-center justify-center text-[var(--color-text-muted)] hover:bg-[var(--color-surface-2)] transition-colors"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1.5C5.5 1.5 4 3.5 4 6v3L2 11h12l-2-2V6c0-2.5-1.5-4.5-4-4.5z" stroke="currentColor" strokeWidth="1.4" />
                  <path d="M6.5 12a1.5 1.5 0 003 0" stroke="currentColor" strokeWidth="1.4" />
                </svg>
                {runs.some((r) => r.status === "running") && (
                  <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "var(--color-danger)" }} />
                )}
              </button>

              {notifOpen && (
                <div
                  className="absolute right-0 top-10 w-80 rounded-xl border shadow-lg z-50 overflow-hidden"
                  style={{ background: "var(--color-surface)", borderColor: "var(--color-border)" }}
                >
                  <div className="px-4 py-3 border-b" style={{ borderColor: "var(--color-border)" }}>
                    <span className="text-[13px] font-semibold text-[var(--color-text)]">Recent Activity</span>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {runsLoading && (
                      <div className="px-4 py-6 text-center text-[12px] text-[var(--color-text-muted)]">Loading...</div>
                    )}
                    {runsError && (
                      <div className="px-4 py-6 text-center text-[12px]" style={{ color: "var(--color-danger)" }}>{runsError}</div>
                    )}
                    {!runsLoading && !runsError && runs.length === 0 && (
                      <div className="px-4 py-6 text-center text-[12px] text-[var(--color-text-muted)]">No pipeline runs yet.</div>
                    )}
                    {!runsLoading && runs.map((run) => {
                      const label = run.requirements?.name || (run.requirements?.module ? `Module: ${run.requirements.module}` : "Full pipeline run");
                      const statusColor = run.status === "completed" ? "var(--color-success)" : run.status === "failed" ? "var(--color-danger)" : "var(--color-primary-bright)";
                      const statusLabel = run.status === "completed" ? "Completed" : run.status === "failed" ? "Failed" : run.status === "running" ? "Running" : run.status;
                      return (
                        <button
                          key={run.id}
                          onClick={() => { setScreen("pipeline"); setNotifOpen(false); }}
                          className="w-full text-left px-4 py-3 border-b last:border-0 hover:bg-[var(--color-surface-2)] transition-colors"
                          style={{ borderColor: "var(--color-border)" }}
                        >
                          <div className="flex items-center justify-between gap-2 mb-1">
                            <span className="text-[12.5px] font-medium text-[var(--color-text)] truncate">{label}</span>
                            <span className="text-[10px] font-semibold flex-shrink-0" style={{ color: statusColor }}>{statusLabel}</span>
                          </div>
                          <div className="flex items-center justify-between text-[11px] text-[var(--color-text-muted)]">
                            <span>
                              {run.error ? run.error.slice(0, 60) : `${run.scenario_count} scenario(s) · ${run.script_count} script(s)`}
                            </span>
                            <span className="flex-shrink-0 ml-2">{timeAgo(run.completed_at || run.created_at)}</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Scrollable content */}
        <main className="flex-1 overflow-y-auto">
          <div key={screen} style={{ animation: "fadeIn 200ms ease-out" }}>
            {renderScreen()}
          </div>
        </main>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}

function AuthGate() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full" style={{ background: "var(--color-bg)" }}>
        <div className="text-[13px] text-[var(--color-text-muted)]">Loading…</div>
      </div>
    );
  }

  return user ? <AppShell /> : <SignIn />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AuthGate />
      </AuthProvider>
    </QueryClientProvider>
  );
}
