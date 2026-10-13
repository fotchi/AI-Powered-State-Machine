import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge";
import { apiFetch, getScripts, type GeneratedScript } from "../src/api";

interface ValidationResultsProps {
  onNavigate: (screen: string) => void;
}

interface ConsistencyReport {
  total_scenarios: number;
  total_scripts: number;
  consistent: number;
  missing_scripts: { scenario_id: string; expected_script_id: string }[];
  orphan_scripts: string[];
}

interface RunAllSummary {
  total: number;
  success: number;
  failed: number;
  skipped: number;
  duration_seconds: number;
}

export default function ValidationResults({ onNavigate }: ValidationResultsProps) {
  const [scripts, setScripts] = useState<GeneratedScript[]>([]);
  const [consistency, setConsistency] = useState<ConsistencyReport | null>(null);
  const [consistencyLoading, setConsistencyLoading] = useState(false);
  const [consistencyError, setConsistencyError] = useState("");
  const [running, setRunning] = useState(false);
  const [runSummary, setRunSummary] = useState<RunAllSummary | null>(null);
  const [runError, setRunError] = useState("");
  useEffect(() => {
    getScripts().then(setScripts).catch(() => setScripts([]));
  }, []);

  const runAllScripts = async () => {
    if (running) return;
    setRunning(true);
    setRunError("");
    setRunSummary(null);
    try {
      const res = await apiFetch("/scripts/execute-all", { method: "POST" });
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const summary: RunAllSummary = await res.json();
      setRunSummary(summary);
      const updated = await getScripts();
      setScripts(updated);
    } catch {
      setRunError("Could not run the scripts -- backend unreachable or execution failed.");
    } finally {
      setRunning(false);
    }
  };

  const checkConsistency = async () => {
    setConsistencyLoading(true);
    setConsistencyError("");
    try {
      const res = await apiFetch("/coverage/consistency");
      if (!res.ok) throw new Error();
      setConsistency(await res.json());
    } catch {
      setConsistencyError("Could not reach the Integration Agent.");
    } finally {
      setConsistencyLoading(false);
    }
  };

  const results = scripts.map((script) => ({
    id: script.id,
    scenario: script.name,
    type: script.name.includes("neg") ? "negative" as const : "positive" as const,
    status: script.skipped
      ? "skipped" as const
      : script.execution_success === true ? "success" as const
      : script.execution_success === false ? "failed" as const
      : "pending" as const,
    assertions: 0,
    passed: script.execution_success === true ? 0 : 0,
    duration: script.duration_seconds != null ? `${script.duration_seconds.toFixed(2)}s` : "—",
    statusCode: 0,
    detail: script.skipped
      ? "Out of scope for isolated execution -- not counted as pass/fail."
      : script.error || (script.execution_success === true ? "Execution succeeded." : script.execution_success === false ? "Execution failed." : "No validation result available."),
  }));
  // Skipped scripts (out-of-scope/requires-SDK, deliberately sys.exit(1) by
  // design -- see phase2_service.py's _NOT_APPLICABLE_CATEGORIES) aren't
  // real pass/fail cases, so they're excluded from the pass-rate denominator
  // to avoid making the platform look worse than it is.
  const applicable = results.filter((result) => result.status !== "skipped");
  const passed = applicable.filter((result) => result.status === "success").length;
  const failed = applicable.filter((result) => result.status === "failed").length;
  const skippedCount = results.length - applicable.length;
  const totalDuration = scripts.reduce((sum, s) => sum + (s.duration_seconds || 0), 0);
  const positiveResults = results.filter((result) => result.type === "positive");
  const negativeResults = results.filter((result) => result.type === "negative");
  const summaryStats = [
    { label: "Total Tests", value: String(results.length), color: "var(--color-primary-bright)" },
    { label: "Passed", value: String(passed), color: "var(--color-success)" },
    { label: "Failed", value: String(failed), color: "var(--color-danger)" },
    { label: "Pass Rate", value: applicable.length ? `${Math.round((passed / applicable.length) * 100)}%` : "—", color: "var(--color-primary-bright)" },
    { label: "Total Duration", value: totalDuration > 0 ? `${totalDuration.toFixed(1)}s` : "—", color: "var(--color-warning)" },
    { label: "Skipped / N/A", value: String(skippedCount), color: "var(--color-text-muted)" },
  ];
  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-sm mb-2">
            <button onClick={() => onNavigate("pipeline")} className="hover:text-[var(--color-primary-bright)]">Pipeline</button>
            <span>/</span>
            <button onClick={() => onNavigate("code")} className="hover:text-[var(--color-primary-bright)]">Code</button>
            <span>/</span>
            <span className="text-[var(--color-text-secondary)]">Validation Results</span>
          </div>
          <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
            Validation Results
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">
            All Script Agent outputs, newest first · Execution results available from the backend
          </p>
        </div>
        <div className="flex gap-3">
          <button
            className="px-4 py-2.5 rounded-lg text-sm font-medium border border-[var(--color-border-strong)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-2)] flex items-center gap-2"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1v8M4 6l3 3 3-3M2 11h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Export Report
          </button>
          <button
            onClick={runAllScripts}
            disabled={running || !scripts.length}
            className="px-4 py-2.5 rounded-lg text-sm font-semibold border disabled:opacity-60 flex items-center gap-2"
            style={{ borderColor: "color-mix(in srgb, var(--color-success) 40%, transparent)", color: "var(--color-success)", background: "var(--color-success-soft)" }}
          >
            {running ? "Running..." : "Run All Scripts"}
          </button>
          <button
            onClick={() => onNavigate("history")}
            className="px-4 py-2.5 rounded-lg text-white text-sm font-semibold"
            style={{ background: "var(--color-primary)" }}
          >
            View History →
          </button>
        </div>
      </div>

      {(runSummary || runError) && (
        <div
          className="rounded-lg border px-4 py-2.5 mb-4 text-[13px]"
          style={
            runError
              ? { background: "var(--color-danger-soft)", borderColor: "color-mix(in srgb, var(--color-danger) 30%, transparent)", color: "var(--color-danger)" }
              : { background: "var(--color-success-soft)", borderColor: "color-mix(in srgb, var(--color-success) 30%, transparent)", color: "var(--color-success)" }
          }
        >
          {runError
            ? runError
            : `✓ Ran ${runSummary!.total} script(s) in ${runSummary!.duration_seconds}s -- ${runSummary!.success} passed, ${runSummary!.failed} failed, ${runSummary!.skipped} not applicable.`}
        </div>
      )}

      {/* Result banner */}
      <div
        className="rounded-xl border p-5 mb-6 flex items-center gap-5"
        style={{ background: "var(--color-success-soft)", borderColor: "color-mix(in srgb, var(--color-success) 30%, transparent)" }}
      >
        <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: "color-mix(in srgb, var(--color-success) 18%, transparent)" }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M20 7L10 17l-5-5" stroke="var(--color-success)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="flex-1">
          <div style={{ fontFamily: "var(--font-display)", color: "var(--color-success)" }} className="font-bold text-lg">
            {results.length ? `${passed} Test${passed === 1 ? "" : "s"} Passed` : "No Validation Results"}
          </div>
          <div className="text-sm" style={{ color: "var(--color-success)" }}>
            {results.length
              ? `${passed} of ${applicable.length} applicable test cases passed${skippedCount ? ` (${skippedCount} out of scope, excluded)` : ""}.`
              : "Script Agent has not provided validation results for the existing scripts."}
          </div>
        </div>
        <div
          style={{ fontFamily: "var(--font-mono)", color: "var(--color-success)" }}
          className="text-4xl font-bold"
        >
          {applicable.length ? `${Math.round((passed / applicable.length) * 100)}%` : "—"}
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-6 gap-3 mb-6">
        {summaryStats.map((s) => (
          <div key={s.label} className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-4">
            <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
              {s.label}
            </div>
            <div
              style={{ fontFamily: "var(--font-display)", color: s.color }}
              className="text-xl font-bold"
            >
              {s.value}
            </div>
          </div>
        ))}
      </div>

      {/* Results table */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)]">
          <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-semibold text-[15px]">
            Test Case Results
          </h2>
          <div className="flex gap-2">
            {["All", "Positive", "Negative"].map((filter) => (
              <button
                key={filter}
                className="px-3 py-1 rounded-md text-[12px] font-medium transition-colors"
                style={
                  filter === "All"
                    ? { background: "var(--color-primary-soft)", color: "var(--color-primary-bright)" }
                    : { background: "transparent", color: "var(--color-text-muted)" }
                }
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--color-border)]">
              {["Test ID", "Scenario", "Type", "Status", "HTTP Code", "Assertions", "Duration", "Detail"].map((h) => (
                <th
                  key={h}
                  className="text-left text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider px-5 py-3"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr
                key={r.id}
                className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-surface-2)] transition-colors"
              >
                <td className="px-5 py-3.5">
                  <span
                    style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)" }}
                    className="text-xs"
                  >
                    {r.id}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-[13px] font-medium text-[var(--color-text)]">
                  {r.scenario}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={r.type} size="sm" />
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={r.status} size="sm" />
                </td>
                <td className="px-5 py-3.5">
                  <span
                    style={{
                      fontFamily: "var(--font-mono)",
                      color: r.statusCode < 300 ? "var(--color-success)" : r.statusCode < 500 ? "var(--color-warning)" : "var(--color-danger)",
                      background: r.statusCode < 300 ? "var(--color-success-soft)" : r.statusCode < 500 ? "var(--color-warning-soft)" : "var(--color-danger-soft)",
                    }}
                    className="text-xs px-2 py-0.5 rounded font-semibold"
                  >
                    {r.statusCode}
                  </span>
                </td>
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-semibold" style={{ color: "var(--color-success)" }}>{r.passed}</span>
                    <span className="text-[var(--color-text-disabled)] text-xs">/</span>
                    <span className="text-[var(--color-text-muted)] text-xs">{r.assertions}</span>
                  </div>
                </td>
                <td className="px-5 py-3.5">
                  <span style={{ fontFamily: "var(--font-mono)" }} className="text-xs text-[var(--color-text-muted)]">
                    {r.duration}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-[12px] text-[var(--color-text-muted)] max-w-[200px] truncate">
                  {r.detail}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Type breakdown */}
      <div className="grid grid-cols-2 gap-5 mt-5">
        {[
          { label: "Positive Scenarios", count: positiveResults.length, passed: positiveResults.filter((result) => result.status === "success").length, color: "var(--color-success)", bg: "var(--color-success-soft)", border: "color-mix(in srgb, var(--color-success) 30%, transparent)" },
          { label: "Negative Scenarios", count: negativeResults.length, passed: negativeResults.filter((result) => result.status === "success").length, color: "var(--color-warning)", bg: "var(--color-warning-soft)", border: "color-mix(in srgb, var(--color-warning) 30%, transparent)" },
        ].map((g) => (
          <div
            key={g.label}
            className="rounded-xl border p-5"
            style={{ background: g.bg, borderColor: g.border }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-[var(--color-text)] text-[14px]">{g.label}</span>
              <span className="font-bold text-[13px]" style={{ color: g.color }}>
                {g.passed}/{g.count} passed
              </span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--color-surface-3)" }}>
              <div
                className="h-full rounded-full"
                style={{ width: "100%", background: g.color }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Integration Agent */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5 mt-5">
        <div className="flex items-center justify-between mb-1">
          <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-semibold text-[15px]">
            Integration Agent
          </h2>
          <button
            onClick={checkConsistency}
            disabled={consistencyLoading}
            className="px-3.5 py-1.5 rounded-lg text-[12px] font-semibold text-white disabled:opacity-60"
            style={{ background: "var(--color-primary)" }}
          >
            {consistencyLoading ? "Checking..." : "Check Consistency"}
          </button>
        </div>
        <p className="text-[11px] text-[var(--color-text-muted)] mb-4">
          Cross-checks every Scenario Agent scenario against Script Agent's output: does each scenario have a
          matching generated script, and are there any scripts left over that no longer correspond to a scenario?
          Read-only -- it flags gaps, it doesn't fix them.
        </p>

        {consistencyError && (
          <p className="text-[12px]" style={{ color: "var(--color-danger)" }}>{consistencyError}</p>
        )}

        {consistency && (
          <>
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="rounded-lg p-3" style={{ background: "var(--color-surface-2)" }}>
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Scenarios</div>
                <div className="text-lg font-bold text-[var(--color-text)]">{consistency.total_scenarios}</div>
              </div>
              <div className="rounded-lg p-3" style={{ background: "var(--color-surface-2)" }}>
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Scripts</div>
                <div className="text-lg font-bold text-[var(--color-text)]">{consistency.total_scripts}</div>
              </div>
              <div className="rounded-lg p-3" style={{ background: "var(--color-surface-2)" }}>
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Consistent</div>
                <div className="text-lg font-bold" style={{ color: consistency.missing_scripts.length ? "var(--color-warning)" : "var(--color-success)" }}>
                  {consistency.consistent}/{consistency.total_scenarios}
                </div>
              </div>
            </div>

            {consistency.missing_scripts.length > 0 && (
              <div className="mb-3">
                <div className="text-[11px] font-semibold text-[var(--color-warning)] mb-1.5">
                  ⚠ {consistency.missing_scripts.length} scenario(s) with no matching script
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {consistency.missing_scripts.slice(0, 20).map((m) => (
                    <span
                      key={m.scenario_id}
                      style={{ fontFamily: "var(--font-mono)", background: "var(--color-warning-soft)", color: "var(--color-warning)" }}
                      className="text-[10.5px] px-2 py-0.5 rounded"
                    >
                      {m.scenario_id}
                    </span>
                  ))}
                  {consistency.missing_scripts.length > 20 && (
                    <span className="text-[10.5px] text-[var(--color-text-muted)]">+{consistency.missing_scripts.length - 20} more</span>
                  )}
                </div>
              </div>
            )}

            {consistency.orphan_scripts.length > 0 && (
              <div>
                <div className="text-[11px] font-semibold text-[var(--color-text-muted)] mb-1.5">
                  {consistency.orphan_scripts.length} script(s) with no matching scenario (orphaned)
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {consistency.orphan_scripts.slice(0, 20).map((id) => (
                    <span
                      key={id}
                      style={{ fontFamily: "var(--font-mono)", background: "var(--color-surface-2)", color: "var(--color-text-muted)" }}
                      className="text-[10.5px] px-2 py-0.5 rounded"
                    >
                      {id}
                    </span>
                  ))}
                  {consistency.orphan_scripts.length > 20 && (
                    <span className="text-[10.5px] text-[var(--color-text-muted)]">+{consistency.orphan_scripts.length - 20} more</span>
                  )}
                </div>
              </div>
            )}

            {consistency.missing_scripts.length === 0 && consistency.orphan_scripts.length === 0 && (
              <p className="text-[12px]" style={{ color: "var(--color-success)" }}>
                ✓ Every scenario has a matching script, and no orphaned scripts were found.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
