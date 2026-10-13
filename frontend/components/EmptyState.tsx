import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}

export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-14 px-6">
      <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ background: "var(--color-surface-2)", color: "var(--color-text-muted)" }}>
        {icon}
      </div>
      <div
        style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }}
        className="font-semibold text-[14px] mb-1.5"
      >
        {title}
      </div>
      <p className="text-[12px] max-w-[280px] leading-relaxed" style={{ color: "var(--color-text-muted)" }}>{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-4 text-[12px] font-semibold transition-colors"
          style={{ color: "var(--color-primary)" }}
        >
          {action.label} →
        </button>
      )}
    </div>
  );
}
