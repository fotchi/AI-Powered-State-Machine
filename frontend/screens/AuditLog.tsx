import { useEffect, useState } from "react";
import { apiFetch } from "../src/api";
import { useAuth } from "../src/auth";
import EmptyState from "../components/EmptyState";

interface AuditEvent {
  id: number;
  run_id: string | null;
  event_type: string;
  message: string;
  created_at: string;
}

const EVENT_COLORS: Record<string, string> = {
  user_login: "var(--color-success)",
  user_logout: "var(--color-text-muted)",
  run_saved: "var(--color-primary-bright)",
  scenarios_saved: "var(--color-primary-bright)",
  scripts_saved: "var(--color-primary-bright)",
  artifacts_synced: "var(--color-warning)",
};

export default function AuditLog() {
  const { user } = useAuth();
  const isAdmin = user?.role === "administrator";
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAdmin) {
      setLoading(false);
      return;
    }
    apiFetch("/audit")
      .then((res) => {
        if (!res.ok) throw new Error(res.status === 403 ? "Administrator role required." : `Backend returned ${res.status}`);
        return res.json();
      })
      .then((data) => setEvents(data.events || []))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load audit log."))
      .finally(() => setLoading(false));
  }, [isAdmin]);

  if (!isAdmin) {
    return (
      <div className="p-8">
        <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold mb-6">
          Audit Log
        </h1>
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)]">
          <EmptyState
            icon={
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="4" y="8" width="12" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
                <path d="M7 8V6a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.4" />
              </svg>
            }
            title="Administrator role required"
            description="The audit log is a role-restricted view. Sign in with an administrator account to see it."
          />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
            Audit Log
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">
            History of pipeline and account events · administrator-only · {events.length} events
          </p>
        </div>
      </div>

      <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-[13px] text-[var(--color-text-muted)]">Loading…</div>
        ) : error ? (
          <div className="p-8 text-center text-[13px]" style={{ color: "var(--color-danger)" }}>{error}</div>
        ) : events.length === 0 ? (
          <EmptyState
            icon={
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <rect x="4" y="8" width="12" height="9" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
                <path d="M7 8V6a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.4" />
              </svg>
            }
            title="No events yet"
            description="Pipeline runs and sign-ins will show up here as they happen."
          />
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--color-border)] bg-[var(--color-surface-2)]">
                {["Event", "Message", "Run", "When"].map((h) => (
                  <th key={h} className="text-left text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider px-5 py-3">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id} className="border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-surface-2)] transition-colors">
                  <td className="px-5 py-3">
                    <span
                      className="text-[11px] font-medium px-2 py-0.5 rounded"
                      style={{
                        color: EVENT_COLORS[event.event_type] || "var(--color-text-secondary)",
                        background: `color-mix(in srgb, ${EVENT_COLORS[event.event_type] || "var(--color-text-muted)"} 14%, transparent)`,
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {event.event_type}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-[13px] text-[var(--color-text)]">{event.message}</td>
                  <td className="px-5 py-3 text-[12px]" style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)" }}>
                    {event.run_id || "—"}
                  </td>
                  <td className="px-5 py-3 text-[12px] text-[var(--color-text-muted)]" style={{ fontFamily: "var(--font-mono)" }}>
                    {new Date(event.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
