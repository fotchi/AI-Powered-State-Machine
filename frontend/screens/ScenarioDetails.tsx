import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import { getScenarios, type Scenario } from "../src/api";

interface ScenarioDetailsProps {
  onNavigate: (screen: string) => void;
}

export default function ScenarioDetails({ onNavigate }: ScenarioDetailsProps) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);

  useEffect(() => {
    getScenarios().then(setScenarios).catch(() => setScenarios([]));
  }, []);

  const positiveScenarios = scenarios.filter((scenario) => scenario.type.toLowerCase() === "positive");
  const negativeScenarios = scenarios.filter((scenario) => scenario.type.toLowerCase() === "negative");
  const toSteps = (scenario: Scenario) => [scenario.description];
  const selectedScenario = scenarios.find((scenario) => scenario.id === window.localStorage.getItem("flync_selected_scenario_id")) || scenarios[0];

  if (scenarios.length === 0) {
    return (
      <div className="p-8">
        <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold mb-6">
          Scenario Details
        </h1>
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm">
          <EmptyState
            icon={
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 3h9l3 3v11a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.4" />
                <path d="M7 9h6M7 12.5h6M7 16h3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            }
            title="No scenario to show"
            description="Generate a scenario, or pick one from History, to see its details here."
            action={{ label: "Generate a scenario", onClick: () => onNavigate("generation") }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-sm mb-2">
            <button onClick={() => onNavigate("history")} className="hover:text-[var(--color-primary-bright)]">History</button>
            <span>/</span>
            <span className="text-[var(--color-text-secondary)]">{selectedScenario?.id || "No scenario selected"}</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
              {selectedScenario?.title || "Scenario Details"}
            </h1>
            {selectedScenario && <StatusBadge status={selectedScenario.type.toLowerCase() as any} />}
          </div>
          <div className="flex items-center gap-4 mt-2">
            <span
              style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)", background: "var(--color-primary-soft)" }}
              className="text-xs px-2 py-0.5 rounded font-medium"
            >
              {selectedScenario?.id || "—"}
            </span>
            <span className="text-[var(--color-text-muted)] text-sm">{selectedScenario?.submodel || "—"}</span>
            <span className="text-[var(--color-text-disabled)]">·</span>
            <span className="text-[var(--color-text-muted)] text-sm">Existing Scenario Agent output</span>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onNavigate("pipeline")}
            className="px-4 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-[var(--color-text-secondary)] text-sm font-medium hover:bg-[var(--color-surface-2)]"
          >
            View Pipeline
          </button>
          <button
            onClick={() => onNavigate("code")}
            className="px-4 py-2.5 rounded-lg text-white text-sm font-semibold"
            style={{ background: "var(--color-primary)" }}
          >
            View Code →
          </button>
        </div>
      </div>

      {/* Metadata cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Scenario Type", value: selectedScenario?.type || "—", color: "var(--color-primary-bright)", bg: "var(--color-primary-soft)" },
          { label: "Total Cases", value: String(scenarios.length), color: "var(--color-text)", bg: "var(--color-surface-2)" },
          { label: "Positive", value: String(positiveScenarios.length), color: "var(--color-success)", bg: "var(--color-success-soft)" },
          { label: "Negative", value: String(negativeScenarios.length), color: "var(--color-warning)", bg: "var(--color-warning-soft)" },
        ].map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-[var(--color-border)] shadow-sm p-4 bg-[var(--color-surface)]"
          >
            <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
              {m.label}
            </div>
            <div
              style={{ fontFamily: "var(--font-display)", color: m.color, background: m.bg }}
              className="inline-block text-sm font-bold px-2.5 py-1 rounded-lg"
            >
              {m.value}
            </div>
          </div>
        ))}
      </div>

      {/* Scenario details (real data — no more fake "Analyst Agent" step) */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-6 mb-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: "var(--color-primary-soft)", color: "var(--color-primary-bright)" }}>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5" />
              <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-semibold text-[15px]">
            Scenario Details
          </h2>
        </div>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Submodel</div>
            <p className="text-[12px] text-[var(--color-text-secondary)] leading-relaxed">
              {selectedScenario?.submodel || "—"}
            </p>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">Description</div>
            <p className="text-[12px] text-[var(--color-text-secondary)] leading-relaxed">
              {selectedScenario?.description || "No scenario is currently selected."}
            </p>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1.5">
              {selectedScenario?.type?.toLowerCase() === "negative" ? "Injected Fault" : "Expected Result"}
            </div>
            <div
              className="rounded-lg p-3"
              style={{ background: "var(--color-code-bg)", fontFamily: "var(--font-mono)" }}
            >
              <div className="text-[12px] text-[#67E8F9] break-words">
                {selectedScenario?.type?.toLowerCase() === "negative"
                  ? selectedScenario?.injected_fault || "—"
                  : selectedScenario?.expected_result || "—"}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Positive / Negative scenarios */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        {/* Positive */}
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-5 py-4 border-b border-[var(--color-border)]" style={{ background: "var(--color-success-soft)" }}>
            <div className="w-2.5 h-2.5 rounded-full" style={{ background: "var(--color-success)" }} />
            <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-success)" }} className="font-semibold text-[14px]">
              Positive Scenarios ({positiveScenarios.length})
            </h2>
          </div>
          <div className="p-4 space-y-3 max-h-[520px] overflow-y-auto">
            {positiveScenarios.length === 0 && (
              <p className="text-[12px] text-[var(--color-text-muted)] text-center py-6">No positive cases generated for this scenario.</p>
            )}
            {positiveScenarios.map((s, i) => (
              <div key={s.id} className="rounded-lg p-4" style={{ border: "1px solid var(--color-success-soft)", background: "color-mix(in srgb, var(--color-success) 6%, transparent)" }}>
                <div className="flex items-center justify-between mb-2">
                  <span
                    style={{ fontFamily: "var(--font-mono)", color: "var(--color-success)" }}
                    className="text-[11px] font-medium"
                  >
                    {s.id}
                  </span>
                  <StatusBadge status="positive" size="sm" />
                </div>
                <div className="font-semibold text-[var(--color-text)] text-[13px] mb-2">{s.title}</div>
                <div className="space-y-1 mb-2">
                  {toSteps(s).map((step, si) => (
                    <div key={si} className="flex items-start gap-2 text-[12px] text-[var(--color-text-muted)]">
                      <span className="font-semibold flex-shrink-0" style={{ color: "var(--color-success)" }}>{si + 1}.</span>
                      {step}
                    </div>
                  ))}
                </div>
                <div className="text-[11px] rounded px-2.5 py-1.5 font-medium" style={{ color: "var(--color-success)", background: "var(--color-success-soft)" }}>
                  ✓ Expected: {s.expected_result}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Negative */}
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-5 py-4 border-b border-[var(--color-border)]" style={{ background: "var(--color-warning-soft)" }}>
            <div className="w-2.5 h-2.5 rounded-full" style={{ background: "var(--color-warning)" }} />
            <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-warning)" }} className="font-semibold text-[14px]">
              Negative Scenarios ({negativeScenarios.length})
            </h2>
          </div>
          <div className="p-4 space-y-3 max-h-[520px] overflow-y-auto">
            {negativeScenarios.length === 0 && (
              <p className="text-[12px] text-[var(--color-text-muted)] text-center py-6">No negative cases generated for this scenario.</p>
            )}
            {negativeScenarios.map((s) => (
              <div key={s.id} className="rounded-lg p-4" style={{ border: "1px solid var(--color-warning-soft)", background: "color-mix(in srgb, var(--color-warning) 6%, transparent)" }}>
                <div className="flex items-center justify-between mb-2">
                  <span
                    style={{ fontFamily: "var(--font-mono)", color: "var(--color-warning)" }}
                    className="text-[11px] font-medium"
                  >
                    {s.id}
                  </span>
                  <StatusBadge status="negative" size="sm" />
                </div>
                <div className="font-semibold text-[var(--color-text)] text-[13px] mb-2">{s.title}</div>
                <div className="space-y-1 mb-2">
                  {toSteps(s).map((step, si) => (
                    <div key={si} className="flex items-start gap-2 text-[12px] text-[var(--color-text-muted)]">
                      <span className="font-semibold flex-shrink-0" style={{ color: "var(--color-warning)" }}>{si + 1}.</span>
                      {step}
                    </div>
                  ))}
                </div>
                <div className="text-[11px] rounded px-2.5 py-1.5 font-medium" style={{ color: "var(--color-warning)", background: "var(--color-warning-soft)" }}>
                  ✗ Expected: {s.expected_result}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}