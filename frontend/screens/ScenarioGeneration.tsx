import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import Button from "../components/Button";
import { apiFetch } from "../src/api";
import { MACHINE_LABELS } from "../src/machines";

// All 12 State Machines from phase1/coverage/state_machines/ -- see
// GET /coverage/machines for the live phase1_module mapping. Several
// machines can map to the same "Module / Feature" (e.g. Communication
// covers Ethernet + Socket + Endpoint + Deployment), so the module
// dropdown alone doesn't pick a machine -- see machinesForModule below.

// Doit matcher phase1/single_run.py::AGENTS_BY_KEY -- ce sont les 11 vrais
// submodels FLYNC, pas des modules d'app générique.
const FLYNC_MODULES: { key: string; label: string }[] = [
  { key: "app", label: "App" },
  { key: "bus", label: "Bus" },
  { key: "communication", label: "Communication" },
  { key: "ecu", label: "ECU" },
  { key: "metadata", label: "Metadata" },
  { key: "nm", label: "NM (Network Management)" },
  { key: "security", label: "Security" },
  { key: "signal", label: "Signal" },
  { key: "someip", label: "SOME/IP" },
  { key: "topology", label: "Topology" },
  { key: "tsn", label: "TSN" },
];

interface ScenarioGenerationProps {
  onNavigate: (screen: string) => void;
}

export default function ScenarioGeneration({ onNavigate }: ScenarioGenerationProps) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    name: "",
    module: "bus",
    description: "",
    scenarioType: "both",
    preconditions: "",
    expectedBehavior: "",
    tags: "",
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [machines, setMachines] = useState<{ key: string; phase1_module: string }[]>([]);
  const [selectedMachine, setSelectedMachine] = useState("");
  const [coverage, setCoverage] = useState<{ expected_total: number; covered: number; gaps: any[]; verification_method?: string } | null>(null);
  const [coverageLoading, setCoverageLoading] = useState(false);
  const [fillingGaps, setFillingGaps] = useState(false);
  const [fillResult, setFillResult] = useState<string | null>(null);

  // Fully automatic path: scan every one of the 12 machines, pick whichever
  // has the lowest covered/expected_total ratio (not raw gap count -- a
  // machine with 2 tags and 1 gap is "worse off" than one with 8 tags and
  // 3 gaps), and fill it. No module/machine choice from the user at all.
  const [autoRunning, setAutoRunning] = useState(false);
  const [autoProgress, setAutoProgress] = useState<
    { key: string; status: "pending" | "checking" | "done" | "error"; covered?: number; expected_total?: number }[]
  >([]);
  const [autoError, setAutoError] = useState("");

  useEffect(() => {
    apiFetch("/coverage/machines")
      .then((res) => (res.ok ? res.json() : []))
      .then(setMachines)
      .catch(() => setMachines([]));
  }, []);

  // Coverage is a standalone tool (any of the 12 State Machines), independent
  // of whichever Module/Feature the requirements form below is currently
  // set to -- so it only needs to pick a default once, when the machine
  // list first loads, not every time form.module changes.
  useEffect(() => {
    if (machines.length && !selectedMachine) setSelectedMachine(machines[0].key);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [machines]);

  const selectMachine = (key: string) => {
    setSelectedMachine(key);
    setCoverage(null);
    setFillResult(null);
  };

  const checkCoverage = async () => {
    if (!selectedMachine) return;
    setCoverageLoading(true);
    setCoverage(null);
    setFillResult(null);
    try {
      const res = await apiFetch(`/coverage/${selectedMachine}`);
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      setCoverage(await res.json());
    } catch {
      setError(`Could not check coverage for '${selectedMachine}'.`);
    } finally {
      setCoverageLoading(false);
    }
  };

  // Same full pipeline as the automatic button, but for the machine picked in
  // the Coverage card: generates the missing scenarios (Phase 1) and their
  // scripts + validation (Phase 2), streamed live in Agent Pipeline.
  const fillGaps = async () => {
    if (!selectedMachine) return;
    setFillingGaps(true);
    setFillResult(null);
    try {
      const res = await apiFetch(`/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requirements: {
            mode: "fill_coverage",
            machine: selectedMachine,
            name: `Auto coverage fill - ${MACHINE_LABELS[selectedMachine] || selectedMachine}`,
          },
        }),
      });
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const run = await res.json();
      if (run.run_id) window.localStorage.setItem("flync_active_run_id", String(run.run_id));
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
      queryClient.invalidateQueries({ queryKey: ["scripts"] });
      onNavigate("pipeline");
    } catch {
      setError(`Could not start generation for '${selectedMachine}'.`);
    } finally {
      setFillingGaps(false);
    }
  };

  const autoGenerate = async () => {
    if (!machines.length || autoRunning) return;
    setAutoRunning(true);
    setAutoError("");
    setAutoProgress(machines.map((m) => ({ key: m.key, status: "pending" as const })));

    // Sequential, on purpose, after actually measuring the alternative:
    // checking 3 machines at once was tried and reverted -- each check can
    // spend several real seconds inside a Groq call, and 3 concurrent ones
    // compete for the SAME small round-robin key pool, which made
    // individual calls slow enough under contention to blow past the
    // backend's subprocess timeout (confirmed in backend logs: a "report"
    // call that hit the 45s ceiling). One at a time is slower end-to-end
    // but every call gets the full pool to itself, so it's the reliable
    // choice, not just the simple one.
    const results: { key: string; covered: number; expected_total: number }[] = [];
    for (const m of machines) {
      setAutoProgress((prev) => prev.map((p) => (p.key === m.key ? { ...p, status: "checking" } : p)));
      try {
        const res = await apiFetch(`/coverage/${m.key}`);
        if (!res.ok) throw new Error(`Backend returned ${res.status}`);
        const data = await res.json();
        results.push({ key: m.key, covered: data.covered, expected_total: data.expected_total });
        setAutoProgress((prev) =>
          prev.map((p) => (p.key === m.key ? { ...p, status: "done", covered: data.covered, expected_total: data.expected_total } : p))
        );
      } catch {
        setAutoProgress((prev) => prev.map((p) => (p.key === m.key ? { ...p, status: "error" } : p)));
      }
    }

    const withGaps = results.filter((r) => r.covered < r.expected_total);
    if (withGaps.length === 0) {
      setAutoError("Every machine is already fully covered -- nothing to generate.");
      setAutoRunning(false);
      return;
    }
    // Lowest ratio first; a tie breaks toward whichever has more absolute gaps.
    withGaps.sort((a, b) => {
      const ratioA = a.covered / a.expected_total;
      const ratioB = b.covered / b.expected_total;
      if (ratioA !== ratioB) return ratioA - ratioB;
      return (b.expected_total - b.covered) - (a.expected_total - a.covered);
    });
    const picked = withGaps[0];

    // Same pipeline as the form's "Generate with AI Agents": a real run that
    // generates the scenarios (Phase 1, gap filling for the picked machine)
    // AND their scripts (Phase 2, only for those new scenarios), so it shows
    // up live in Agent Pipeline, Generated Code and Validation Results.
    try {
      const res = await apiFetch(`/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requirements: {
            mode: "fill_coverage",
            machine: picked.key,
            name: `Auto coverage fill - ${MACHINE_LABELS[picked.key] || picked.key}`,
          },
        }),
      });
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      const run = await res.json();
      if (run.run_id) window.localStorage.setItem("flync_active_run_id", String(run.run_id));
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
      queryClient.invalidateQueries({ queryKey: ["scripts"] });
      onNavigate("pipeline");
    } catch {
      setAutoError(`Found the least-covered machine ('${picked.key}') but could not start generation for it.`);
    } finally {
      setAutoRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!form.name.trim() || !form.description.trim()) {
      setError("Scenario name and description are required.");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const response = await apiFetch(`/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requirements: form,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const result = await response.json();
      if (result.run_id) {
        window.localStorage.setItem("flync_active_run_id", String(result.run_id));
      }
      queryClient.invalidateQueries({ queryKey: ["scenarios"] });
      queryClient.invalidateQueries({ queryKey: ["scripts"] });

      onNavigate("pipeline");
    } catch (requestError) {
      setError("Unable to connect to the backend. Start FastAPI on port 8000.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-sm mb-2">
          <button onClick={() => onNavigate("dashboard")} className="hover:text-[var(--color-primary-bright)] transition-colors">
            Dashboard
          </button>
          <span>/</span>
          <span className="text-[var(--color-text-secondary)]">Generate Scenario</span>
        </div>
        <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
          New Scenario Generation
        </h1>
        <p className="text-[var(--color-text-muted)] text-sm mt-1">
          Define requirements and let the AI agent pipeline generate, build, and validate your test scenario.
        </p>
      </div>

      {/* Fully automatic path: no module, no name, no description -- scans
          all 12 machines, picks the least-covered one, generates for its gaps. */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5 mb-6">
        <div className="flex items-center justify-between mb-1">
          <h2 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-semibold text-[15px]">
            Generate New Scenario
          </h2>
          <Button variant="primary" size="sm" onClick={autoGenerate} disabled={autoRunning || !machines.length}>
            {autoRunning ? "Scanning..." : "Generate New Scenario"}
          </Button>
        </div>
        <p className="text-[11px] text-[var(--color-text-muted)] mb-3">
          No form to fill in: scans all 12 State Machines, picks whichever has the least coverage, then
          generates scenarios for its unconfirmed cases and their test scripts automatically.
        </p>

        {autoRunning && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {autoProgress.map((p) => (
              <span
                key={p.key}
                className="text-[10px] px-2 py-0.5 rounded font-mono"
                style={{
                  background:
                    p.status === "done"
                      ? "var(--color-success-soft)"
                      : p.status === "checking"
                      ? "var(--color-primary-soft)"
                      : p.status === "error"
                      ? "var(--color-danger-soft)"
                      : "var(--color-surface-2)",
                  color:
                    p.status === "done"
                      ? "var(--color-success)"
                      : p.status === "checking"
                      ? "var(--color-primary-bright)"
                      : p.status === "error"
                      ? "var(--color-danger)"
                      : "var(--color-text-muted)",
                }}
              >
                {p.key}
                {p.status === "done" ? ` ${p.covered}/${p.expected_total}` : p.status === "checking" ? "…" : ""}
              </span>
            ))}
          </div>
        )}

        {autoError && (
          <p className="text-[12px]" style={{ color: "var(--color-warning)" }}>{autoError}</p>
        )}

      </div>

      {/* Coverage -- standalone tool, all 12 State Machines from
          phase1/coverage/state_machines/, independent of the requirements
          form below (it used to live in the form's sidebar and only show
          the 1-2 machines tied to whichever Module/Feature was selected). */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5 mb-6">
        <h2
          style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
          className="font-semibold text-[15px] mb-3"
        >
          Coverage
        </h2>

        <div className="flex flex-wrap gap-1.5 mb-3">
          {machines.map((m) => (
            <button
              key={m.key}
              onClick={() => selectMachine(m.key)}
              className="px-2.5 py-1 rounded-md text-[11px] font-medium transition-all"
              style={
                selectedMachine === m.key
                  ? { background: "var(--color-primary-soft)", color: "var(--color-primary-bright)" }
                  : { background: "var(--color-surface-2)", color: "var(--color-text-muted)" }
              }
            >
              {MACHINE_LABELS[m.key] || m.key}
            </button>
          ))}
        </div>

        <p className="text-[11px] text-[var(--color-text-muted)] mb-3">
          Checks the {MACHINE_LABELS[selectedMachine] || selectedMachine} State Machine against what already
          exists, and can generate the missing PASS/FAIL cases with their scripts and validation.
        </p>

        <div className="rounded-lg px-3 py-2 mb-3 text-[10.5px] leading-relaxed" style={{ background: "var(--color-surface-2)", color: "var(--color-text-muted)" }}>
          Checks each rule two ways: an exact keyword match first, then -- for anything that misses --
          a single AI review of the rule against every existing scenario's actual meaning (so a scenario
          worded differently can still count). Not infallible on judgment calls, so an "unconfirmed"
          result is still worth a glance before filling, just far rarer than a pure keyword check.
        </div>

        {coverage && (
          <div className="text-[12px] text-[var(--color-text-secondary)] mb-3 flex items-center justify-between">
            <span>
              {coverage.covered}/{coverage.expected_total} cases covered
              {coverage.verification_method === "keyword" ? " (keyword only -- AI review unavailable)" : ""}
            </span>
            {coverage.gaps.length > 0 && (
              <span className="font-semibold px-2 py-0.5 rounded" style={{ color: "var(--color-warning)", background: "var(--color-warning-soft)" }}>
                {coverage.gaps.length} unconfirmed
              </span>
            )}
          </div>
        )}
        {fillResult && <p className="text-[11px] mb-3" style={{ color: "var(--color-success)" }}>{fillResult}</p>}

        <div className="flex gap-2 max-w-sm">
          <Button variant="secondary" size="sm" onClick={checkCoverage} disabled={coverageLoading || !selectedMachine} fullWidth>
            {coverageLoading ? "Checking..." : "Check Coverage"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fillGaps}
            disabled={fillingGaps || !coverage || coverage.gaps.length === 0}
            fullWidth
          >
            {fillingGaps ? "Starting..." : "Fill Unconfirmed"}
          </Button>
        </div>
        {coverage && coverage.gaps.length > 0 && (
          <p className="text-[10.5px] mt-2" style={{ color: "var(--color-warning)" }}>
            ⚠ May generate scenarios that duplicate ones already covered by different wording.
          </p>
        )}
      </div>

      {/* Pipeline indicator */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5 mb-6">
        <div className="flex items-center">
          {[
            { step: 1, label: "Submit Requirements", sub: "Define scenario", color: "var(--color-primary)" },
            { step: 2, label: "Analyst Agent", sub: "Analyzes requirements", color: "var(--color-primary)" },
            { step: 3, label: "Developer Agent", sub: "Generates Python code", color: "var(--color-primary)" },
            { step: 4, label: "Validator Agent", sub: "Executes & validates", color: "var(--color-success-strong)" },
          ].map((s, i, arr) => (
            <div key={s.step} className="flex items-center flex-1">
              <div className="flex flex-col items-center gap-1.5">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                  style={{
                    background: s.step === 1 ? s.color : "var(--color-surface-2)",
                    color: s.step === 1 ? "white" : "var(--color-text-muted)",
                  }}
                >
                  {s.step}
                </div>
                <div className="text-center">
                  <div
                    className="text-[11px] font-semibold"
                    style={{ color: s.step === 1 ? "var(--color-text)" : "var(--color-text-muted)" }}
                  >
                    {s.label}
                  </div>
                  <div className="text-[10px] text-[var(--color-text-muted)]">{s.sub}</div>
                </div>
              </div>
              {i < arr.length - 1 && (
                <div className="flex-1 h-px mx-3 mt-[-16px]" style={{ background: "var(--color-border-strong)" }} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-5">
          {/* Basic info */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-6">
            <h2
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
              className="font-semibold text-[15px] mb-5"
            >
              Scenario Requirements
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                  Scenario Name <span className="text-[var(--color-danger)]">*</span>
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. User Login with Invalid Credentials"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] bg-[var(--color-surface-2)] transition-all placeholder:text-[var(--color-text-disabled)]"
                />
              </div>

              <div>
                <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                  Module / Feature
                </label>
                <select
                  value={form.module}
                  onChange={(e) => setForm({ ...form, module: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] bg-[var(--color-surface-2)]"
                >
                  {FLYNC_MODULES.map((m) => (
                    <option key={m.key} value={m.key}>{m.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                  Description <span className="text-[var(--color-danger)]">*</span>
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={4}
                  placeholder="Describe the test scenario in detail. Include the functionality to test, the expected behavior, and any special constraints..."
                  className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] bg-[var(--color-surface-2)] resize-none placeholder:text-[var(--color-text-disabled)]"
                />
              </div>

              <button
                type="button"
                onClick={() => setShowAdvanced((v) => !v)}
                className="flex items-center gap-1.5 text-[12px] font-semibold text-[var(--color-primary-bright)] hover:opacity-80 transition-opacity"
              >
                <span style={{ transform: showAdvanced ? "rotate(90deg)" : "none", display: "inline-block", transition: "transform 0.15s" }}>
                  ▸
                </span>
                {showAdvanced ? "Hide" : "Add"} optional details (preconditions, expected behavior, tags)
              </button>

              {showAdvanced && (
                <>
                  <div>
                    <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                      Preconditions
                    </label>
                    <textarea
                      value={form.preconditions}
                      onChange={(e) => setForm({ ...form, preconditions: e.target.value })}
                      rows={2}
                      placeholder="e.g. User is registered, application is running, test database is seeded..."
                      className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] bg-[var(--color-surface-2)] resize-none placeholder:text-[var(--color-text-disabled)]"
                    />
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                      Expected Behavior
                    </label>
                    <textarea
                      value={form.expectedBehavior}
                      onChange={(e) => setForm({ ...form, expectedBehavior: e.target.value })}
                      rows={2}
                      placeholder="e.g. System should return error code 401 with message 'Invalid credentials'..."
                      className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] bg-[var(--color-surface-2)] resize-none placeholder:text-[var(--color-text-disabled)]"
                    />
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                      Tags
                    </label>
                    <input
                      type="text"
                      value={form.tags}
                      onChange={(e) => setForm({ ...form, tags: e.target.value })}
                      placeholder="auth, security, login (comma separated)"
                      className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] bg-[var(--color-surface-2)] placeholder:text-[var(--color-text-disabled)]"
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Right panel */}
        <div className="space-y-5">
          {/* Scenario type */}
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-5">
            <h2
              style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
              className="font-semibold text-[15px] mb-4"
            >
              Scenario Type
            </h2>
            <div className="space-y-2.5">
              {[
                { val: "positive", label: "Positive Only", desc: "Valid inputs, expected success paths", color: "var(--color-success)" },
                { val: "negative", label: "Negative Only", desc: "Invalid inputs, error & edge cases", color: "var(--color-warning)" },
                { val: "both", label: "Both Types", desc: "Generate positive + negative scenarios", color: "var(--color-primary-bright)" },
              ].map((opt) => (
                <label
                  key={opt.val}
                  className="flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all"
                  style={{
                    borderColor: form.scenarioType === opt.val ? opt.color : "var(--color-border-strong)",
                    background: form.scenarioType === opt.val ? `color-mix(in srgb, ${opt.color} 8%, transparent)` : "transparent",
                  }}
                >
                  <input
                    type="radio"
                    name="scenarioType"
                    value={opt.val}
                    checked={form.scenarioType === opt.val}
                    onChange={() => setForm({ ...form, scenarioType: opt.val })}
                    className="mt-0.5 accent-[var(--color-primary-bright)]"
                  />
                  <div>
                    <div className="text-[13px] font-semibold text-[var(--color-text)]">{opt.label}</div>
                    <div className="text-[11px] text-[var(--color-text-muted)] mt-0.5">{opt.desc}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Submit */}
          <Button
            variant="primary"
            fullWidth
            onClick={handleSubmit}
            disabled={submitting}
            icon={
              submitting ? (
                <svg className="animate-spin" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="6" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
                  <path d="M8 2a6 6 0 016 6" stroke="white" strokeWidth="2" strokeLinecap="round" />
                </svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 1l1.5 4.5H13L9.5 8l1.5 4.5L7 10 3 12.5 4.5 8 1 5.5h4.5L7 1z" fill="white" />
                </svg>
              )
            }
          >
            {submitting ? "Submitting to AI Pipeline..." : "Generate with AI Agents"}
          </Button>
          {error && (
            <p className="text-xs text-[var(--color-danger)]" role="alert">
              {error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}