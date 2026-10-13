import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

const TOKEN_KEY = "flync_auth_token";

export interface AuthUser {
  email: string;
  full_name: string;
  role: string;
}

export function getToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function setToken(token: string) {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* ignore (private browsing, storage disabled, ...) */
  }
}

function clearToken() {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

// api.ts calls this when a request comes back 401, so an expired/invalid
// token gets the user bounced back to the sign-in screen without api.ts
// needing to import the auth context directly.
let unauthorizedHandler: (() => void) | null = null;
export function setUnauthorizedHandler(fn: () => void) {
  unauthorizedHandler = fn;
}
export function notifyUnauthorized() {
  unauthorizedHandler?.();
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleUnauthorized = () => {
    clearToken();
    setUser(null);
  };

  useEffect(() => {
    setUnauthorizedHandler(handleUnauthorized);
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    fetch(`${API_URL}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error("Session expired");
        return res.json();
      })
      .then((me: AuthUser) => setUser(me))
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    setError(null);
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => null);
      const message = detail?.detail || "Incorrect email or password.";
      setError(message);
      throw new Error(message);
    }
    const payload = await response.json();
    setToken(payload.access_token);
    setUser(payload.user);
  };

  const logout = () => {
    const token = getToken();
    clearToken();
    setUser(null);
    if (token) {
      fetch(`${API_URL}/auth/logout`, { method: "POST", headers: { Authorization: `Bearer ${token}` } }).catch(() => {});
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
