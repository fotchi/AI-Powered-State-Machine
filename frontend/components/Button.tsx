import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from "react";

type Variant = "primary" | "secondary" | "outline" | "danger" | "ghost";
type Size = "sm" | "md";

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "style"> {
  variant?: Variant;
  size?: Size;
  fullWidth?: boolean;
  icon?: ReactNode;
  style?: CSSProperties;
  children?: ReactNode;
}

const variantStyles: Record<Variant, CSSProperties> = {
  primary: {
    background: "var(--color-primary)",
    color: "#FFFFFF",
    border: "1px solid transparent",
  },
  secondary: {
    background: "var(--color-surface-2)",
    color: "var(--color-text)",
    border: "1px solid transparent",
  },
  outline: {
    background: "transparent",
    color: "var(--color-text)",
    border: "1px solid var(--color-border-strong)",
  },
  danger: {
    background: "var(--color-danger-strong)",
    color: "#FFFFFF",
    border: "1px solid transparent",
  },
  ghost: {
    background: "transparent",
    color: "var(--color-text-muted)",
    border: "1px solid transparent",
  },
};

const variantHoverClass: Record<Variant, string> = {
  primary: "hover:bg-[var(--color-primary-hover)]",
  secondary: "hover:bg-[var(--color-surface-3)]",
  outline: "hover:border-[var(--color-text-muted)] hover:text-[var(--color-text)]",
  danger: "hover:opacity-90",
  ghost: "hover:bg-[var(--color-surface-2)] hover:text-[var(--color-text)]",
};

const sizeClass: Record<Size, string> = {
  sm: "h-8 px-3 text-[12px] gap-1.5",
  md: "h-10 px-4 text-[13px] gap-2",
};

export default function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  icon,
  style,
  disabled,
  children,
  className,
  ...rest
}: ButtonProps) {
  return (
    <button
      disabled={disabled}
      className={[
        "inline-flex items-center justify-center rounded-lg font-semibold transition-all",
        sizeClass[size],
        !disabled && variantHoverClass[variant],
        disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer",
        fullWidth ? "w-full" : "",
        className || "",
      ].join(" ").trim()}
      style={{ ...variantStyles[variant], ...style }}
      {...rest}
    >
      {icon}
      {children}
    </button>
  );
}
