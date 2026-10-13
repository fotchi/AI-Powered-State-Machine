import { useState } from "react";
import { useAuth } from "../src/auth";
import Button from "../components/Button";

export default function SignIn() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Trim the password too, not just the email -- copy-pasting credentials
    // very easily picks up a trailing space/newline, which would otherwise
    // fail as a "wrong password" even though the visible text matches.
    const trimmedPassword = password.trim();
    if (!email.trim() || !trimmedPassword) {
      setError("Enter your email and password.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await login(email.trim().toLowerCase(), trimmedPassword);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="flex items-center justify-center h-full"
      style={{ background: "var(--color-bg)", fontFamily: "var(--font-body)" }}
    >
      <div className="w-full max-w-[380px] px-6">
        <div className="flex flex-col items-center mb-8">
          <div
            style={{ background: "var(--color-primary)" }}
            className="w-11 h-11 rounded-xl flex items-center justify-center mb-4"
          >
            <svg width="20" height="20" viewBox="0 0 16 16" fill="none">
              <path d="M3 8a5 5 0 0110 0" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="8" cy="8" r="2" fill="white" />
              <path d="M8 10v3" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </div>
          <div style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-bold text-lg tracking-wide">
            FLYNC
          </div>
          <div className="text-[var(--color-text-muted)] text-[11px] font-medium tracking-widest uppercase mt-0.5">
            AI QA Platform
          </div>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 shadow-lg">
          <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-semibold text-[17px] mb-1">
            Sign in
          </h1>
          <p className="text-[var(--color-text-muted)] text-[12px] mb-5">
            Use your FLYNC account to access the pipeline dashboard.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] font-semibold text-[var(--color-text-secondary)] mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="qa@flync.io"
                autoComplete="username"
                autoFocus
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-surface-2)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] transition-all placeholder:text-[var(--color-text-disabled)]"
              />
            </div>

            <div>
              <label className="block text-[12px] font-semibold text-[var(--color-text-secondary)] mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border-strong)] bg-[var(--color-surface-2)] text-sm text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-bright)]/30 focus:border-[var(--color-primary-bright)] transition-all placeholder:text-[var(--color-text-disabled)]"
              />
            </div>

            {error && (
              <p className="text-[12px]" style={{ color: "var(--color-danger)" }} role="alert">
                {error}
              </p>
            )}

            <Button type="submit" variant="primary" fullWidth disabled={submitting}>
              {submitting ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
