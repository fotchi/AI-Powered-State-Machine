import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import EmptyState from "../components/EmptyState";
import { useScenarios, useScripts, scenarioIdFromScriptId } from "../src/hooks";

interface DashboardProps {
  onNavigate: (screen: string) => void;
}

export default function Dashboard({ onNavigate }: DashboardProps) {
  const { data: scenarios = [] } = useScenarios();
  const { data: scripts = [] } = useScripts();
  const scriptCount = scripts.length;
  const validatedCount = scripts.filter((s) => s.execution_success === true).length;
  const failedCount = scripts.filter((s) => s.execution_success === false).length;

  const executedCount = validatedCount + failedCount;
  const metrics = [
    { label: "Total Scenarios", value: String(scenarios.length), delta: "Scenario Agent outputs", color: "var(--color-primary-bright)", icon: "description", action: "View scenarios", screen: "history" },
    { label: "Success Rate", value: executedCount ? `${Math.round((validatedCount / executedCount) * 100)}%` : "—", delta: executedCount ? `${validatedCount}/${executedCount} executed scripts` : "No script executed yet", color: "var(--color-success)", icon: "check_circle", action: "View validation", screen: "validation" },
    { label: "Generated Scripts", value: String(scriptCount), delta: "Script Agent outputs", color: "var(--color-warning)", icon: "code", action: "View scripts", screen: "code" },
    { label: "Failed Validations", value: String(failedCount), delta: failedCount ? "Needs attention" : "None so far", color: "var(--color-danger)", icon: "error", action: "Review failures", screen: "validation" },
  ];
  const recentScenarios = scenarios.slice(0, 5).map((scenario) => {
    const script = scripts.find((s) => scenarioIdFromScriptId(s.id) === scenario.id);
    const status = !script || script.execution_success === null
      ? "pending"
      : script.execution_success ? "success" : "failed";
    return { id: scenario.id, name: scenario.title, type: scenario.type.toLowerCase(), status, submodel: scenario.submodel };
  });
  const agentStatus = [
    { name: "Analyst Agent", role: "Scenario Agent output", status: "success" as const, queue: 0 },
    { name: "Developer Agent", role: "Script Agent output", status: scriptCount ? "success" as const : "pending" as const, queue: 0 },
    { name: "Validator Agent", role: "Execution results", status: executedCount ? (failedCount ? "failed" as const : "success" as const) : "pending" as const, queue: 0 },
  ];
  const positiveCount = scenarios.filter((scenario) => scenario.type.toLowerCase() === "positive").length;
  const negativeCount = scenarios.filter((scenario) => scenario.type.toLowerCase() === "negative").length;
  return (
    <div className="p-8 space-y-7">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1
            style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
            className="text-2xl font-bold"
          >
            Platform Overview
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">
            FLYNC AI QA — Automated scenario generation & validation
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => onNavigate("generation")}
          icon={
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1v12M1 7h12" stroke="white" strokeWidth="2" strokeLinecap="round" />
            </svg>
          }
        >
          New Scenario
        </Button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm hover:border-[var(--color-border-strong)] transition-colors overflow-hidden"
          >
            <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-[var(--color-border)]">
              <h5 className="text-[var(--color-text-muted)] text-[10px] font-semibold uppercase tracking-wider truncate">
                {m.label}
              </h5>
              <div
                className="w-6 h-6 rounded-md flex items-center justify-center text-xs flex-shrink-0 ml-2"
                style={{ background: `color-mix(in srgb, ${m.color} 18%, transparent)` }}
              >
                <span className="material-symbols-rounded text-[16px]" style={{ color: m.color }}>{m.icon}</span>
              </div>
            </div>
            <div className="px-3.5 py-3">
              <h5
                className="text-xl font-bold"
                style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
              >
                {m.value}
              </h5>
              <p className="text-[10px] text-[var(--color-text-muted)] mt-1 truncate">{m.delta}</p>
              <Button
                variant="primary"
                size="sm"
                className="mt-3 h-7 px-2.5 text-[10px]"
                onClick={() => onNavigate(m.screen)}
              >
                {m.action}
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-5">
        {/* Recent scenarios table */}
        <div className="xl:col-span-3 bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-x-auto">
          <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)]">
            <h2
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
              className="font-semibold text-[15px]"
            >
              Recent Scenarios
            </h2>
            <button
              onClick={() => onNavigate("history")}
              className="text-[var(--color-primary-bright)] text-xs font-medium hover:opacity-80"
            >
              View all →
            </button>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--color-border)]">
                {["ID", "Scenario", "Type", "Status", "Submodel"].map((h) => (
                  <th
                    key={h}
                    className="text-left text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider px-6 py-3"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {recentScenarios.map((s, i) => (
                <tr
                  key={s.id}
                  className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-surface-2)] cursor-pointer transition-colors"
                  onClick={() => onNavigate("scenario-details")}
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  <td className="px-6 py-3">
                    <span
                      style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)" }}
                      className="text-xs"
                    >
                      {s.id}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-[13px] font-medium text-[var(--color-text)] max-w-[160px] truncate">
                    {s.name}
                  </td>
                  <td className="px-6 py-3">
                    <StatusBadge status={s.type as any} size="sm" />
                  </td>
                  <td className="px-6 py-3">
                    <StatusBadge status={s.status as any} size="sm" />
                  </td>
                  <td className="px-6 py-3 text-[12px] text-[var(--color-text-muted)]">{s.submodel}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {recentScenarios.length === 0 && (
            <EmptyState
              icon={
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M4 3h9l3 3v11a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.4" />
                  <path d="M7 9h6M7 12.5h6M7 16h3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
                </svg>
              }
              title="No scenarios yet"
              description="Generate your first FLYNC test scenario to see it show up here."
              action={{ label: "Generate a scenario", onClick: () => onNavigate("generation") }}
            />
          )}
        </div>

        {/* Agent status */}
        <div className="xl:col-span-2 space-y-4">
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm">
            <div className="px-5 py-4 border-b border-[var(--color-border)]">
              <h2
                style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
                className="font-semibold text-[15px]"
              >
                AI Agent Status
              </h2>
            </div>
            <div className="p-4 space-y-3">
              {agentStatus.map((agent) => (
                <div
                  key={agent.name}
                  className="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-surface-2)]"
                >
                  <div
                    className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{
                      background:
                        agent.status === "failed" ? "var(--color-danger-soft)" : agent.status === "pending" ? "var(--color-surface-3)" : "var(--color-success-soft)",
                    }}
                  >
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <circle cx="8" cy="5" r="2.5" stroke={agent.status === "failed" ? "var(--color-danger)" : agent.status === "pending" ? "var(--color-text-muted)" : "var(--color-success)"} strokeWidth="1.5" />
                      <path d="M3 14c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke={agent.status === "failed" ? "var(--color-danger)" : agent.status === "pending" ? "var(--color-text-muted)" : "var(--color-success)"} strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[13px] font-semibold text-[var(--color-text)] truncate">{agent.name}</div>
                    <div className="text-[11px] text-[var(--color-text-muted)] truncate">{agent.role}</div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <StatusBadge status={agent.status} size="sm" />
                    <div className="text-[10px] text-[var(--color-text-muted)] mt-1">
                      {agent.queue > 0 ? `${agent.queue} queued` : "idle"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Weekly summary */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-semibold text-[15px]">
                Scenario Breakdown
              </h2>
            </div>
            <div className="space-y-3">
              {[
                { label: "Positive Scenarios", count: positiveCount, total: scenarios.length || 1, color: "var(--color-success)" },
                { label: "Negative Scenarios", count: negativeCount, total: scenarios.length || 1, color: "var(--color-warning)" },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex justify-between text-[12px] mb-1">
                    <span className="text-[var(--color-text-secondary)]">{item.label}</span>
                    <span className="font-semibold text-[var(--color-text)]">{item.count}</span>
                  </div>
                  <div className="h-1.5 bg-[var(--color-surface-2)] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${(item.count / item.total) * 100}%`,
                        background: item.color,
                      }}
                    />
                  </div>
                </div>
              ))}
              <div className="pt-2 flex justify-between text-[12px]">
                <span className="text-[var(--color-text-muted)]">Total</span>
                <span className="font-bold text-[var(--color-text)]">{scenarios.length} scenarios</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}