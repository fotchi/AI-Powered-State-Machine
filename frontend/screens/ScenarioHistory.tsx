import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import { getScenarios, getScripts } from "../src/api";
import { scenarioIdFromScriptId } from "../src/hooks";

interface ScenarioHistoryProps {
  onNavigate: (screen: string) => void;
}

export default function ScenarioHistory({ onNavigate }: ScenarioHistoryProps) {
  const [allScenarios, setAllScenarios] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterType, setFilterType] = useState("all");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  useEffect(() => {
    Promise.all([getScenarios(), getScripts()]).then(([items, scripts]) => {
      const scriptByScenarioId = new Map(scripts.map((s) => [scenarioIdFromScriptId(s.id), s]));
      setAllScenarios(items.map((scenario) => {
        const script = scriptByScenarioId.get(scenario.id);
        const status = !script || script.execution_success === null || script.execution_success === undefined
          ? "pending"
          : script.execution_success === true ? "success" : "failed";
        return {
          id: scenario.id,
          name: scenario.title,
          module: scenario.submodel,
          type: scenario.type.toLowerCase(),
          status,
          hasScript: !!script,
          date: "",
        };
      }));
    }).catch(() => setAllScenarios([]));
  }, []);

  const filtered = allScenarios.filter((s) => {
    const matchSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.id.toLowerCase().includes(search.toLowerCase()) ||
      s.module.toLowerCase().includes(search.toLowerCase());
    const matchStatus = filterStatus === "all" || s.status === filterStatus;
    const matchType = filterType === "all" || s.type === filterType;
    return matchSearch && matchStatus && matchType;
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const paginated = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
            Scenario History
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">
            All generated and executed scenarios — {allScenarios.length} total
          </p>
        </div>
        <button
          onClick={() => onNavigate("generation")}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-white text-sm font-semibold"
          style={{ background: "var(--color-primary)" }}
        >
          + New Scenario
        </button>
      </div>

      {/* Filters */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm p-4 mb-5 flex items-center gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <svg
            width="16" height="16" viewBox="0 0 16 16" fill="none"
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]"
          >
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5" />
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by name, ID, or module..."
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-surface-2)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] placeholder:text-[var(--color-text-disabled)]"
          />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[12px] text-[var(--color-text-muted)] font-medium">Status:</span>
          {["all", "success", "pending", "failed"].map((s) => (
            <button
              key={s}
              onClick={() => { setFilterStatus(s); setPage(1); }}
              className="px-3 py-1.5 rounded-lg text-[12px] font-medium capitalize transition-all"
              style={
                filterStatus === s
                  ? { background: "var(--color-primary)", color: "white" }
                  : { background: "var(--color-surface-2)", color: "var(--color-text-muted)" }
              }
            >
              {s === "all" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[12px] text-[var(--color-text-muted)] font-medium">Type:</span>
          {["all", "positive", "negative"].map((t) => (
            <button
              key={t}
              onClick={() => { setFilterType(t); setPage(1); }}
              className="px-3 py-1.5 rounded-lg text-[12px] font-medium capitalize transition-all"
              style={
                filterType === t
                  ? { background: "var(--color-primary)", color: "white" }
                  : { background: "var(--color-surface-2)", color: "var(--color-text-muted)" }
              }
            >
              {t === "all" ? "All" : t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-[var(--color-surface-2)]">
              {["Scenario ID", "Name", "Module", "Type", "Status", "Script", ""].map((h) => (
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
            {paginated.map((s) => {
              return (
                <tr
                  key={s.id}
                  className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-surface-2)] transition-colors cursor-pointer"
                  onClick={() => {
                    window.localStorage.setItem("flync_selected_scenario_id", s.id);
                    onNavigate("scenario-details");
                  }}
                >
                  <td className="px-5 py-3.5">
                    <span
                      style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)" }}
                      className="text-xs font-medium"
                    >
                      {s.id}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-[13px] font-medium text-[var(--color-text)] max-w-[200px]">
                    <div className="truncate">{s.name}</div>
                  </td>
                  <td className="px-5 py-3.5 text-[12px] text-[var(--color-text-muted)]">{s.module}</td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={s.type as any} size="sm" />
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={s.status as any} size="sm" />
                  </td>
                  <td className="px-5 py-3.5 text-[12px] text-[var(--color-text-muted)]">
                    {s.hasScript ? "Generated" : "Not generated yet"}
                  </td>
                  <td className="px-5 py-3.5">
                    <button className="text-[var(--color-primary-bright)] text-[12px] font-medium hover:opacity-80">
                      View →
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <EmptyState
            icon={
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.4" />
                <path d="M13.5 13.5L17 17" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            }
            title={allScenarios.length === 0 ? "No scenarios yet" : "No scenarios match your filters"}
            description={
              allScenarios.length === 0
                ? "Generate your first FLYNC test scenario to start building your history."
                : "Try widening your search or clearing the status/type filters."
            }
            action={
              allScenarios.length === 0
                ? { label: "Generate a scenario", onClick: () => onNavigate("generation") }
                : { label: "Clear filters", onClick: () => { setSearch(""); setFilterStatus("all"); setFilterType("all"); setPage(1); } }
            }
          />
        )}

        {filtered.length > 0 && (
          <div className="px-6 py-3 border-t border-[var(--color-border)] bg-[var(--color-surface-2)] flex justify-between items-center">
            <span className="text-[12px] text-[var(--color-text-muted)]">
              Showing {paginated.length ? (currentPage - 1) * pageSize + 1 : 0}–{(currentPage - 1) * pageSize + paginated.length} of {filtered.length} scenarios
            </span>
            {totalPages > 1 && (
              <div className="flex gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className="w-7 h-7 rounded text-[12px] font-medium transition-colors"
                    style={p === currentPage ? { background: "var(--color-primary)", color: "white" } : { color: "var(--color-text-muted)" }}
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}