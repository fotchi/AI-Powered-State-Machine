import { getToken, notifyUnauthorized } from "./auth";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Scenario {
  id: string;
  submodel: string;
  type: "Positive" | "Negative" | string;
  title: string;
  description: string;
  injected_fault?: string | null;
  expected_result: string;
}

export interface GeneratedScript {
  id: string;
  name: string;
  path: string;
  content: string;
  execution_success?: boolean | null;
  skipped?: boolean;
  error?: string | null;
  duration_seconds?: number | null;
}

/** Authenticated fetch: attaches the JWT, and bounces the user back to the
 * sign-in screen on a 401 (expired/invalid token) instead of failing silently. */
export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (response.status === 401) notifyUnauthorized();
  return response;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await apiFetch(path);
  if (!response.ok) throw new Error(`Backend returned ${response.status}`);
  return response.json() as Promise<T>;
}

/** The most recently started run, stashed by ScenarioGeneration.tsx after a
 * successful submit -- the same key AgentPipeline.tsx reads to decide
 * between "show live run" and "show existing outputs". Screens that render
 * scenarios/scripts after a run (GeneratedCode, ScenarioDetails,
 * ValidationResults) need this too: without it they always show the old
 * historical backlog instead of what the user just generated. */
export function getActiveRunId(): string | undefined {
  return window.localStorage.getItem("flync_active_run_id") || undefined;
}

export async function getScenarios(runId?: string): Promise<Scenario[]> {
  const query = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
  const payload = await getJson<{ scenarios: Scenario[] }>(`/scenarios${query}`);
  return payload.scenarios;
}

export async function getScripts(runId?: string): Promise<GeneratedScript[]> {
  const query = runId ? `?run_id=${encodeURIComponent(runId)}` : "";
  const payload = await getJson<{ scripts: GeneratedScript[] }>(`/scripts${query}`);
  return payload.scripts;
}

/** WebSockets can't carry an Authorization header from browser JS, so the
 * token travels as a query param instead -- see main.py's /runs/{id}/stream. */
export function authenticatedWebSocketUrl(path: string): string {
  const token = getToken();
  const base = API_URL.replace(/^http/, "ws").replace(/\/$/, "");
  const separator = path.includes("?") ? "&" : "?";
  return `${base}${path}${token ? `${separator}token=${encodeURIComponent(token)}` : ""}`;
}
