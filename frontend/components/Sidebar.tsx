import { useAuth } from "../src/auth";

interface SidebarProps {
  current: string;
  onNavigate: (screen: string) => void;
}

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] || "") + (parts[1]?.[0] || "")).toUpperCase() || "?";
}

const ROLE_LABELS: Record<string, string> = {
  qa_engineer: "QA Engineer",
  administrator: "Administrator",
};

function SignOutIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <path d="M6 2H3.5a1 1 0 00-1 1v10a1 1 0 001 1H6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M10.5 11.5L14 8l-3.5-3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M14 8H6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

const navItems = [
  {
    group: "Overview",
    items: [
      { id: "dashboard", label: "Dashboard", icon: DashboardIcon },
      { id: "history", label: "Scenario History", icon: HistoryIcon },
    ],
  },
  {
    group: "Workflow",
    items: [
      { id: "generation", label: "Generate Scenario", icon: GenerateIcon },
      { id: "scenario-details", label: "Scenario Details", icon: ScenarioIcon },
      { id: "pipeline", label: "Agent Pipeline", icon: PipelineIcon },
      { id: "state-machine", label: "State Machine", icon: StateMachineIcon },
      { id: "code", label: "Generated Code", icon: CodeIcon },
      { id: "validation", label: "Validation Results", icon: ValidationIcon },
    ],
  },
];

// Visible only to the "administrator" role -- the one concrete, in-UI
// example of the Technical Design Document's "role-based access control
// for QA vs. administrative actions" (backed by the admin-only GET /audit
// endpoint; a qa_engineer token gets a 403 from that route).
const adminNavGroup = {
  group: "Administration",
  items: [{ id: "audit-log", label: "Audit Log", icon: AuditIcon }],
};

function AuditIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="2.5" y="1.5" width="11" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.4" />
      <path d="M5 5h6M5 7.5h6M5 10h3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="11.5" cy="11.5" r="2.25" stroke="currentColor" strokeWidth="1.3" />
      <path d="M13.2 13.2L14.5 14.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}

function DashboardIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="1" y="1" width="6" height="6" rx="1.5" fill="currentColor" opacity="0.9" />
      <rect x="9" y="1" width="6" height="6" rx="1.5" fill="currentColor" opacity="0.5" />
      <rect x="1" y="9" width="6" height="6" rx="1.5" fill="currentColor" opacity="0.5" />
      <rect x="9" y="9" width="6" height="6" rx="1.5" fill="currentColor" opacity="0.9" />
    </svg>
  );
}
function HistoryIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M8 4.5V8L10.5 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
function GenerateIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M8 1.5v3M8 11.5v3M1.5 8h3M11.5 8h3M3.4 3.4l2.1 2.1M10.5 10.5l2.1 2.1M3.4 12.6l2.1-2.1M10.5 5.5l2.1-2.1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
function ScenarioIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5 5.5h6M5 8h6M5 10.5h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
function PipelineIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="3" cy="8" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="13" cy="8" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="8" cy="4" r="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5 8h3M8 6v-.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M10 7.5L13 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
function CodeIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M5 5L2 8l3 3M11 5l3 3-3 3M9 3l-2 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function StateMachineIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="3" r="2" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="3" cy="11" r="2" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="13" cy="11" r="2" stroke="currentColor" strokeWidth="1.4" />
      <path d="M8 5v2.5M8 7.5l-3.5 1.5M8 7.5l3.5 1.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}
function ValidationIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M13 4L6.5 11 3 7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function Sidebar({ current, onNavigate }: SidebarProps) {
  const { user } = useAuth();
  const groups = user?.role === "administrator" ? [...navItems, adminNavGroup] : navItems;

  return (
    <aside
      style={{ background: "var(--color-bg)", width: 228, minWidth: 228 }}
      className="flex flex-col h-full border-r border-[var(--color-border)]"
    >
      {/* Logo */}
      <div className="px-5 pt-6 pb-5 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-2.5">
          <div
            style={{ background: "var(--color-primary)" }}
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8a5 5 0 0110 0" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="8" cy="8" r="2" fill="white" />
              <path d="M8 10v3" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <div style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-bold text-sm tracking-wide">
              FLYNC
            </div>
            <div className="text-[var(--color-text-muted)] text-[10px] font-medium tracking-widest uppercase">
              AI QA Platform
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {groups.map((group) => (
          <div key={group.group}>
            <div className="text-[var(--color-text-muted)] text-[10px] font-semibold tracking-widest uppercase px-2 mb-1.5">
              {group.group}
            </div>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const active = current === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-left transition-all duration-150"
                    style={{
                      background: active ? "var(--color-primary-soft)" : "transparent",
                      color: active ? "var(--color-primary-bright)" : "var(--color-text-secondary)",
                    }}
                    onMouseEnter={(e) => {
                      if (!active) (e.currentTarget as HTMLElement).style.background = "var(--color-surface-2)";
                    }}
                    onMouseLeave={(e) => {
                      if (!active) (e.currentTarget as HTMLElement).style.background = "transparent";
                    }}
                  >
                    <item.icon />
                    <span className="text-[13px] font-medium">{item.label}</span>
                    {active && (
                      <div
                        style={{ background: "var(--color-primary-bright)" }}
                        className="ml-auto w-1 h-4 rounded-full"
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <SidebarFooter />
    </aside>
  );
}

function SidebarFooter() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <div className="px-4 py-4 border-t border-[var(--color-border)]">
      <div className="flex items-center gap-2.5">
        <div
          style={{ background: "var(--color-primary)" }}
          className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
        >
          {initials(user.full_name)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[var(--color-text)] text-[12px] font-semibold truncate">{user.full_name}</div>
          <div className="text-[var(--color-text-muted)] text-[11px] truncate">{ROLE_LABELS[user.role] || user.role}</div>
        </div>
        <button
          onClick={logout}
          title="Sign out"
          aria-label="Sign out"
          className="w-7 h-7 rounded-lg flex items-center justify-center text-[var(--color-text-muted)] hover:bg-[var(--color-surface-2)] hover:text-[var(--color-text)] transition-colors flex-shrink-0"
        >
          <SignOutIcon />
        </button>
      </div>
    </div>
  );
}
