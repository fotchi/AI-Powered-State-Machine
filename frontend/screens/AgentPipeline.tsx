import { useState, useEffect } from "react";
import StatusBadge from "../components/StatusBadge";
import { authenticatedWebSocketUrl, getScenarios, getScripts } from "../src/api";

interface AgentPipelineProps {
  onNavigate: (screen: string) => void;
}

type AgentStatus = "pending" | "running" | "success" | "failed";

interface AgentState {
  team: "Scenario Agent" | "Script Agent";
  name: string;
  role: string;
  status: AgentStatus;
  startTime?: string;
  duration?: string;
  logs: string[];
  output?: string;
}

const scenarioAgentSubAgents = ["app", "bus", "communication", "ecu", "metadata", "nm", "security", "signal", "someip", "topology", "tsn"];
const initialAgents: AgentState[] = [
  ...scenarioAgentSubAgents.map((name) => ({ team: "Scenario Agent" as const, name: `${name.toUpperCase()} Agent`, role: "Scenario generation", status: "pending" as AgentStatus, logs: [] })),
  { team: "Script Agent" as const, name: "Analyst Agent", role: "Requirement analysis", status: "pending" as AgentStatus, logs: [] },
  { team: "Script Agent" as const, name: "Developer Agent", role: "Python test code generation", status: "pending" as AgentStatus, logs: [] },
  { team: "Script Agent" as const, name: "Validator Agent", role: "Code execution and result validation", status: "pending" as AgentStatus, logs: [] },
];

export default function AgentPipeline({ onNavigate }: AgentPipelineProps) {
  const [agents, setAgents] = useState<AgentState[]>(initialAgents);
  const [activeAgent, setActiveAgent] = useState(0);
  const [phase, setPhase] = useState<"idle" | "running" | "done">("idle");
  const [failed, setFailed] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [overallProgress, setOverallProgress] = useState(0);
  const [scenarioCount, setScenarioCount] = useState(0);
  const [scriptCount, setScriptCount] = useState(0);
  const [scenarioTitle, setScenarioTitle] = useState("Existing outputs");
  const [scenarioId, setScenarioId] = useState("—");

  useEffect(() => {
    const runId = window.localStorage.getItem("flync_active_run_id") || undefined;
    if (!runId) {
      Promise.all([getScenarios(), getScripts()]).then(([scenarios, scripts]) => {
        setAgents((prev) => prev.map((agent, index) => ({
          ...agent,
          status: index < 11 || index === 12 ? "success" : "pending",
          logs: ["[read-only] Existing outputs loaded"],
          duration: "Existing output",
        })));
        setOverallProgress(scripts.length ? 67 : scenarios.length ? 33 : 0);
        setScenarioCount(scenarios.length);
        setScriptCount(scripts.length);
        if (scenarios[0]) { setScenarioTitle(scenarios[0].title); setScenarioId(scenarios[0].id); }
        setPhase("done");
      }).catch(() => setPhase("idle"));
      return;
    }

    const socket = new WebSocket(authenticatedWebSocketUrl(`/runs/${encodeURIComponent(runId)}/stream`));
    socket.onmessage = (event) => {
      let message: any;
      try { message = JSON.parse(event.data); } catch { return; }
      if (message.type === "snapshot") {
        const run = message.run;
        setPhase(run.status === "completed" || run.status === "failed" ? "done" : "running");
        setFailed(run.status === "failed");
        setErrorMessage(run.status === "failed" ? run.error || "Unknown error" : null);
        setOverallProgress(run.current_step === "script_agent" ? 67 : run.current_step === "completed" ? 100 : 33);
        setScenarioCount(run.scenario_count || 0);
        setScriptCount(run.script_count || 0);
        setAgents((prev) => prev.map((agent, index) => ({
          ...agent,
          status: run.status === "failed" ? "failed" : run.current_step === "script_agent" && index < 11 ? "success" : run.current_step === "script_agent" && index === 11 ? "running" : run.current_step === "completed" ? "success" : "pending",
        })));
        return;
      }
      if (message.type === "step_started") {
        setPhase("running");
        setActiveAgent(message.step === "scenario_agent" ? 0 : 11);
        setAgents((prev) => prev.map((agent, index) => ({
          ...agent,
          status: message.step === "scenario_agent" ? (index < 11 ? "running" : "pending") : (index < 11 ? "success" : index === 11 ? "running" : "pending"),
        })));
        setOverallProgress(message.step === "scenario_agent" ? 33 : 67);
        return;
      }
      if (message.type === "log") {
        const agentIndex = message.step === "scenario_agent" ? 0 : 11;
        setAgents((prev) => prev.map((agent, index) => index === agentIndex ? { ...agent, logs: [...agent.logs, message.message].slice(-40) } : agent));
        return;
      }
      if (message.type === "scenario_agent_complete") {
        setAgents((prev) => prev.map((agent, index) => index < 11 ? { ...agent, status: "success", logs: index === 0 ? message.logs || [] : agent.logs, duration: "Completed" } : index === 11 ? { ...agent, status: "running" } : agent));
        setScenarioCount(message.scenario_count || 0);
        setActiveAgent(11);
        setOverallProgress(67);
        return;
      }
      if (message.type === "pipeline_complete") {
        setAgents((prev) => prev.map((agent, index) => ({ ...agent, status: index === 13 ? "pending" : "success", logs: index === 11 ? message.logs || agent.logs : agent.logs, duration: "Completed" })));
        setScenarioCount(message.scenario_count || 0);
        setScriptCount(message.script_count || 0);
        setOverallProgress(100);
        setFailed(false);
        setPhase("done");
        return;
      }
      if (message.type === "pipeline_failed") {
        setAgents((prev) => prev.map((agent) => ({ ...agent, status: "failed", logs: message.logs || agent.logs })));
        setFailed(true);
        setErrorMessage(message.error || "Unknown error");
        setPhase("done");
      }
    };
    socket.onerror = () => setPhase("idle");
    return () => socket.close();
  }, []);

  const agentIcon = (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="3" y="3" width="10" height="10" rx="2" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="6" cy="6.5" r="0.9" fill="currentColor" />
      <circle cx="10" cy="6.5" r="0.9" fill="currentColor" />
      <path d="M5.5 9.5h5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-sm mb-2">
            <button onClick={() => onNavigate("dashboard")} className="hover:text-[var(--color-primary-bright)]">Dashboard</button>
            <span>/</span>
            <button onClick={() => onNavigate("generation")} className="hover:text-[var(--color-primary-bright)]">Generate</button>
            <span>/</span>
            <span className="text-[var(--color-text-secondary)]">Agent Pipeline</span>
          </div>
          <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
            AI Agent Pipeline Execution
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">
            Scenario: <span className="font-medium text-[var(--color-text)]">{scenarioTitle}</span>
            <span
              className="ml-2 px-2 py-0.5 rounded text-[11px] font-semibold"
              style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)", background: "var(--color-primary-soft)" }}
            >
              {scenarioId}
            </span>
          </p>
        </div>
        {phase === "done" && !failed && (
          <button
            onClick={() => onNavigate("code")}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-white text-sm font-semibold"
            style={{ background: "var(--color-primary)" }}
          >
            View Generated Code →
          </button>
        )}
      </div>

      {/* Overall progress */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-[var(--color-text)]">Overall Pipeline Progress</span>
            {phase === "done" && (
              failed ? (
                <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold" style={{ background: "var(--color-danger-soft)", color: "var(--color-danger)" }}>
                  ✗ Failed
                </span>
              ) : (
                <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold" style={{ background: "var(--color-success-soft)", color: "var(--color-success)" }}>
                  ✓ Complete
                </span>
              )
            )}
          </div>
          <span className="text-sm font-bold text-[var(--color-primary-bright)]">{phase === "done" ? 100 : overallProgress}%</span>
        </div>
        <div className="h-2 bg-[var(--color-surface-2)] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${phase === "done" ? 100 : overallProgress}%`,
              background: "var(--color-primary)",
            }}
          />
        </div>
        <div className="flex justify-between mt-2">
            <span className="text-[11px] text-[var(--color-text-muted)]">11 Scenario Agent sub-agents · 3 Script Agent stages · {scenarioCount} scenarios · {scriptCount} scripts</span>
          <span className="text-[11px] text-[var(--color-text-muted)]">
            {phase === "done" ? "Completed" : phase === "running" ? "Running..." : "Existing output"}
          </span>
        </div>
      </div>

      {/* Agents */}
      <div className="space-y-4">
        {agents.map((agent, idx) => (
          <div
            key={agent.name}
            className="bg-[var(--color-surface)] rounded-xl border shadow-sm overflow-hidden transition-all"
            style={{ borderColor: activeAgent === idx && phase !== "done" ? "var(--color-primary-bright)" : "var(--color-border)" }}
          >
            {/* Agent header */}
            <div className="flex items-center gap-4 px-6 py-4">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background: "var(--color-primary-soft)", color: "var(--color-primary-bright)" }}
              >
                {agentIcon}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2.5">
                  <span
                    style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
                    className="font-semibold text-[15px]"
                  >
                    {agent.name}
                  </span>
                  <StatusBadge status={agent.status} size="sm" />
                </div>
                <div className="text-[12px] text-[var(--color-text-muted)] mt-0.5">{agent.role}</div>
              </div>
              <div className="text-right">
                {agent.status === "success" && (
                  <div>
                    <div className="text-[11px] text-[var(--color-text-muted)]">Duration</div>
                    <div
                      style={{ fontFamily: "var(--font-mono)", color: "var(--color-success)" }}
                      className="text-sm font-semibold"
                    >
                      {agent.duration}
                    </div>
                  </div>
                )}
                {agent.status === "running" && (
                  <div className="flex items-center gap-1.5">
                    <div
                      className="w-2 h-2 rounded-full animate-pulse"
                      style={{ background: "var(--color-primary-bright)" }}
                    />
                    <span className="text-[12px] text-[var(--color-primary-bright)] font-medium">Processing</span>
                  </div>
                )}
              </div>
            </div>

            {/* Log terminal */}
            {agent.logs.length > 0 && (
              <div
                className="mx-6 mb-4 rounded-lg overflow-hidden"
                style={{ background: "var(--color-code-bg)" }}
              >
                <div className="flex items-center gap-1.5 px-3 py-2 border-b border-white/10">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
                  <span
                    style={{ fontFamily: "var(--font-mono)" }}
                    className="text-[var(--color-text-muted)] text-[10px] ml-2"
                  >
                    agent.log
                  </span>
                </div>
                <div className="p-3 space-y-0.5 max-h-36 overflow-y-auto">
                  {agent.logs.map((log, li) => (
                    <div
                      key={li}
                      style={{ fontFamily: "var(--font-mono)" }}
                      className="text-[11px] leading-relaxed"
                    >
                      <span className="text-[var(--color-text-muted)]">{log.slice(0, 10)}</span>
                      <span
                        style={{
                          color: log.includes("✓") ? "var(--color-success)" : log.includes("ERROR") ? "var(--color-danger)" : "var(--color-text-muted)",
                        }}
                      >
                        {log.slice(10)}
                      </span>
                    </div>
                  ))}
                  {agent.status === "running" && (
                    <div style={{ fontFamily: "var(--font-mono)" }} className="text-[11px] text-[var(--color-text-muted)]">
                      <span className="animate-pulse">█</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Connector arrow */}
            {idx < agents.length - 1 && (
              <div className="flex justify-center py-1">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1v10M4 8l4 4 4-4" stroke="var(--color-border-strong)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Done actions */}
      {phase === "done" && (
        failed ? (
          <div className="mt-6 rounded-xl p-5 flex items-center justify-between" style={{ background: "var(--color-danger-soft)", border: "1px solid color-mix(in srgb, var(--color-danger) 30%, transparent)" }}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "color-mix(in srgb, var(--color-danger) 18%, transparent)" }}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M6 6l8 8M14 6l-8 8" stroke="var(--color-danger)" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </div>
              <div>
                <div className="font-semibold" style={{ color: "var(--color-danger)" }}>Pipeline failed — no scenario was generated</div>
                <div className="text-[12px] mt-0.5 max-w-xl break-words" style={{ color: "var(--color-danger)" }}>{errorMessage}</div>
              </div>
            </div>
            <button
              onClick={() => onNavigate("generation")}
              className="px-4 py-2 rounded-lg text-sm font-semibold text-white flex-shrink-0"
              style={{ background: "var(--color-danger-strong)" }}
            >
              Back to Generation
            </button>
          </div>
        ) : (
          <div className="mt-6 rounded-xl p-5 flex items-center justify-between" style={{ background: "var(--color-success-soft)", border: "1px solid color-mix(in srgb, var(--color-success) 30%, transparent)" }}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "color-mix(in srgb, var(--color-success) 18%, transparent)" }}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M16 6L8 14l-4-4" stroke="var(--color-success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div>
                <div className="font-semibold" style={{ color: "var(--color-success)" }}>Pipeline completed successfully</div>
                <div className="text-[12px]" style={{ color: "var(--color-success)" }}>{scenarioCount} scenarios available · {scriptCount} scripts available</div>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => onNavigate("scenario-details")}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-[var(--color-surface-3)]"
                style={{ border: "1px solid color-mix(in srgb, var(--color-success) 40%, transparent)", color: "var(--color-success)" }}
              >
                View Scenario
              </button>
              <button
                onClick={() => onNavigate("state-machine")}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-[var(--color-surface-3)]"
                style={{ border: "1px solid color-mix(in srgb, var(--color-success) 40%, transparent)", color: "var(--color-success)" }}
              >
                State Machine
              </button>
              <button
                onClick={() => onNavigate("code")}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-[var(--color-surface-3)]"
                style={{ border: "1px solid color-mix(in srgb, var(--color-success) 40%, transparent)", color: "var(--color-success)" }}
              >
                View Code
              </button>
              <button
                onClick={() => onNavigate("validation")}
                className="px-4 py-2 rounded-lg text-sm font-semibold text-white"
                style={{ background: "var(--color-success-strong)" }}
              >
                View Results →
              </button>
            </div>
          </div>
        )
      )}
    </div>
  );
}
