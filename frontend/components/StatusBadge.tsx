type Status = "pending" | "running" | "success" | "failed" | "positive" | "negative" | "skipped";

interface StatusBadgeProps {
  status: Status;
  size?: "sm" | "md";
}

const config: Record<Status, { label: string; bg: string; text: string; dot?: string }> = {
  pending: { label: "Pending", bg: "var(--color-surface-3)", text: "var(--color-text-muted)", dot: "var(--color-text-muted)" },
  running: { label: "Running", bg: "var(--color-primary-soft)", text: "var(--color-primary-bright)", dot: "var(--color-primary-bright)" },
  success: { label: "Success", bg: "var(--color-success-soft)", text: "var(--color-success)", dot: "var(--color-success)" },
  failed: { label: "Failed", bg: "var(--color-danger-soft)", text: "var(--color-danger)", dot: "var(--color-danger)" },
  positive: { label: "Positive", bg: "var(--color-success-soft)", text: "var(--color-success)", dot: "var(--color-success)" },
  negative: { label: "Negative", bg: "var(--color-warning-soft)", text: "var(--color-warning)", dot: "var(--color-warning)" },
  skipped: { label: "N/A", bg: "var(--color-surface-3)", text: "var(--color-text-muted)", dot: "var(--color-text-disabled)" },
};

export default function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const c = config[status];
  const isRunning = status === "running";

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full font-medium"
      style={{
        background: c.bg,
        color: c.text,
        padding: size === "sm" ? "2px 8px" : "3px 10px",
        fontSize: size === "sm" ? "11px" : "12px",
      }}
    >
      <span
        className="rounded-full flex-shrink-0"
        style={{
          width: 6,
          height: 6,
          background: c.dot,
          animation: isRunning ? "pulse 1.5s infinite" : "none",
        }}
      />
      {c.label}
    </span>
  );
}
