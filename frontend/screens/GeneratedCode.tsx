import { useEffect, useState } from "react";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import { apiFetch, getScripts, type GeneratedScript } from "../src/api";

// Le type Positive/Negative n'est pas un champ de GeneratedScript --
// il est encodé dans le nom de fichier (suffixe "..._positive.py" ou
// "..._negative.py"), même convention que phase2_service.py.
//
// Bug corrigé : vérifier "_neg_negative" (au lieu de "_negative" seul)
// ratait tout scénario négatif dont l'id ne se termine pas lui-même par
// "-NEG" (ex: "SC-BUS-013", type Negative -> fichier
// "script_sc_bus_013_negative.py", qui ne finit PAS par "_neg_negative")
// -- ces scripts s'affichaient à tort comme "positive".
function scriptType(scriptId: string): "positive" | "negative" {
  return scriptId.endsWith("_negative") ? "negative" : "positive";
}

interface GeneratedCodeProps {
  onNavigate: (screen: string) => void;
}

/* Existing static code samples are kept out of the data path; scripts come from the Script Agent. */
const legacyCodeMap: Record<string, string> = { /*
  login_valid: `<span class="code-keyword">import</span> pytest
<span class="code-keyword">from</span> flync.builder <span class="code-keyword">import</span> ScenarioBuilder, Step
<span class="code-keyword">from</span> flync.validators <span class="code-keyword">import</span> assert_status, assert_body


<span class="code-comment"># Scenario: Login_Valid_Credentials</span>
<span class="code-comment"># Type: POSITIVE | Priority: HIGH | Module: Authentication</span>
<span class="code-class">class</span> <span class="code-function">TestLoginValidCredentials</span>:

    <span class="code-keyword">def</span> <span class="code-function">setup_method</span>(self):
        self.builder = ScenarioBuilder(
            base_url=<span class="code-string">"https://api.flync-app.io/v1"</span>,
            timeout=<span class="code-number">30</span>
        )
        self.headers = {<span class="code-string">"Content-Type"</span>: <span class="code-string">"application/json"</span>}

    <span class="code-keyword">def</span> <span class="code-function">test_login_valid_credentials</span>(self):
        <span class="code-comment"># Step 1: Submit valid credentials</span>
        response = self.builder.step(
            Step.POST,
            endpoint=<span class="code-string">"/auth/login"</span>,
            payload={
                <span class="code-string">"email"</span>: <span class="code-string">"testuser@example.com"</span>,
                <span class="code-string">"password"</span>: <span class="code-string">"SecureP@ss123"</span>
            },
            headers=self.headers
        )

        <span class="code-comment"># Step 2: Validate authentication success</span>
        assert_status(response, expected=<span class="code-number">200</span>)
        assert_body(response, key=<span class="code-string">"status"</span>, expected=<span class="code-string">"success"</span>)
        assert_body(response, key=<span class="code-string">"data.access_token"</span>, not_null=<span class="code-keyword">True</span>)
        assert_body(response, key=<span class="code-string">"data.token_type"</span>, expected=<span class="code-string">"Bearer"</span>)

        <span class="code-comment"># Step 3: Verify token structure</span>
        token = response.json()[<span class="code-string">"data"</span>][<span class="code-string">"access_token"</span>]
        <span class="code-keyword">assert</span> len(token) > <span class="code-number">20</span>, <span class="code-string">"Token length insufficient"</span>
        <span class="code-keyword">assert</span> token.count(<span class="code-string">"."</span>) == <span class="code-number">2</span>, <span class="code-string">"Expected JWT format"</span>`,

  login_invalid_pw: `<span class="code-keyword">import</span> pytest
<span class="code-keyword">from</span> flync.builder <span class="code-keyword">import</span> ScenarioBuilder, Step
<span class="code-keyword">from</span> flync.validators <span class="code-keyword">import</span> assert_status, assert_body, assert_error


<span class="code-comment"># Scenario: Login_Invalid_Password</span>
<span class="code-comment"># Type: NEGATIVE | Priority: HIGH | Module: Authentication</span>
<span class="code-class">class</span> <span class="code-function">TestLoginInvalidPassword</span>:

    <span class="code-keyword">def</span> <span class="code-function">setup_method</span>(self):
        self.builder = ScenarioBuilder(
            base_url=<span class="code-string">"https://api.flync-app.io/v1"</span>,
            timeout=<span class="code-number">30</span>
        )

    @pytest.mark.parametrize(<span class="code-string">"password"</span>, [
        <span class="code-string">"wrongpassword"</span>,
        <span class="code-string">"Password1"</span>,
        <span class="code-string">"123456"</span>,
        <span class="code-string">""</span>,
        <span class="code-string">"A" * 300</span>,
    ])
    <span class="code-keyword">def</span> <span class="code-function">test_login_invalid_password</span>(self, password):
        response = self.builder.step(
            Step.POST,
            endpoint=<span class="code-string">"/auth/login"</span>,
            payload={
                <span class="code-string">"email"</span>: <span class="code-string">"testuser@example.com"</span>,
                <span class="code-string">"password"</span>: password
            }
        )

        <span class="code-comment"># Expect 401 Unauthorized</span>
        assert_status(response, expected=<span class="code-number">401</span>)
        assert_body(response, key=<span class="code-string">"status"</span>, expected=<span class="code-string">"error"</span>)
        assert_error(response, code=<span class="code-string">"INVALID_CREDENTIALS"</span>)

        <span class="code-comment"># Ensure no token is returned on failure</span>
        body = response.json()
        <span class="code-keyword">assert</span> <span class="code-string">"access_token"</span> <span class="code-keyword">not in</span> body.get(<span class="code-string">"data"</span>, {})`
*/ };

export default function GeneratedCode({ onNavigate }: GeneratedCodeProps) {
  const [scripts, setScripts] = useState<GeneratedScript[]>([]);
  const [selected, setSelected] = useState("");
  const [copied, setCopied] = useState(false);
  const [execution, setExecution] = useState<{ success: boolean; output: string } | null>(null);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    const loadScripts = async () => {
      try {
        const items = await getScripts();
        setScripts(Array.isArray(items) ? items : []);
        if (items[0]) setSelected(items[0].id);
      } catch {
        setScripts([]);
      }
    };
    loadScripts();
  }, []);

  const handleCopy = () => {
    if (script?.content) {
      navigator.clipboard?.writeText(script.content);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const script = scripts.find((item) => item.id === selected) || scripts[0];
  const code = script?.content || "No generated script available.";
  const scenario = script || { id: "", name: "No script selected", type: "unknown" };

  const handleExecute = async () => {
    if (!script || executing) return;
    setExecuting(true);
    setExecution(null);
    try {
      const response = await apiFetch(`/scripts/${encodeURIComponent(script.id)}/execute`, { method: "POST" });
      const result = await response.json();
      setExecution({ success: response.ok && result.execution_success === true, output: result.stderr || result.stdout || result.detail || "No output." });
    } catch {
      setExecution({ success: false, output: "Unable to connect to the backend." });
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-sm mb-2">
            <button onClick={() => onNavigate("pipeline")} className="hover:text-[var(--color-primary-bright)]">Pipeline</button>
            <span>/</span>
            <span className="text-[var(--color-text-secondary)]">Generated Code</span>
          </div>
          <h1 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="text-2xl font-bold">
            Generated Python Code
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm mt-1">
            FLYNC test construction code · Script Agent outputs ·{" "}
            <span className="font-medium text-[var(--color-text)]">{scripts.length} files available</span>
          </p>
        </div>
        <Button variant="primary" onClick={() => onNavigate("validation")}>
          View Validation →
        </Button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-5">
        {/* File list */}
        <div
          className="xl:col-span-1 bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-sm overflow-hidden flex flex-col"
          style={{ maxHeight: "calc(100vh - 180px)" }}
        >
          <div className="px-4 py-3 border-b border-[var(--color-border)] flex-shrink-0">
            <div className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">
              Generated Files
            </div>
          </div>
          <div className="p-2 overflow-y-auto flex-1 min-h-0">
            {scripts.map((s) => (
              <button
                key={s.id}
                onClick={() => setSelected(s.id)}
                className="w-full flex items-start gap-2 p-2.5 rounded-lg text-left transition-colors mb-0.5"
                style={{
                  background: selected === s.id ? "var(--color-primary-soft)" : "transparent",
                }}
                onMouseEnter={(e) => {
                  if (selected !== s.id) (e.currentTarget as HTMLElement).style.background = "var(--color-surface-2)";
                }}
                onMouseLeave={(e) => {
                  if (selected !== s.id) (e.currentTarget as HTMLElement).style.background = "transparent";
                }}
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="mt-0.5 flex-shrink-0">
                  <rect x="2" y="1" width="8" height="12" rx="1.5" stroke={selected === s.id ? "var(--color-primary-bright)" : "var(--color-text-muted)"} strokeWidth="1.2" />
                  <path d="M4.5 4.5h4M4.5 6.5h4M4.5 8.5h2.5" stroke={selected === s.id ? "var(--color-primary-bright)" : "var(--color-text-muted)"} strokeWidth="1.2" strokeLinecap="round" />
                </svg>
                <div className="min-w-0">
                  <div
                    style={{ fontFamily: "var(--font-mono)", color: selected === s.id ? "var(--color-primary-bright)" : "var(--color-text-secondary)" }}
                    className="text-[11px] font-medium truncate"
                  >
                    {s.name}
                  </div>
                  <div className="mt-0.5">
                    <StatusBadge status={scriptType(s.id)} size="sm" />
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="px-4 py-3 border-t border-[var(--color-border)] bg-[var(--color-surface-2)] flex-shrink-0">
            <div className="flex justify-between text-[11px] text-[var(--color-text-muted)]">
              <span>{scripts.length} files</span>
              <span>~240 lines</span>
            </div>
          </div>
        </div>

        {/* Code viewer */}
        <div className="xl:col-span-3">
          <div
            className="rounded-xl overflow-hidden shadow-lg border border-[var(--color-border)]"
            style={{ background: "var(--color-code-bg)" }}
          >
            {/* Editor chrome */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/70" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                <div className="w-3 h-3 rounded-full bg-green-500/70" />
                <span
                  style={{ fontFamily: "var(--font-mono)" }}
                  className="text-[var(--color-text-muted)] text-[12px] ml-3"
                >
                  {scenario.name}
                </span>
                <StatusBadge status={scenario.id ? scriptType(scenario.id) : "positive"} size="sm" />
              </div>
              <div className="flex items-center gap-3">
                <span
                  style={{ fontFamily: "var(--font-mono)" }}
                  className="text-[var(--color-text-muted)] text-[11px]"
                >
                  Python 3.11
                </span>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium transition-all"
                  style={{
                    background: copied ? "var(--color-success-soft)" : "rgba(255,255,255,0.08)",
                    color: copied ? "var(--color-success)" : "var(--color-text-muted)",
                  }}
                >
                  {copied ? (
                    <>✓ Copied</>
                  ) : (
                    <>
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                        <rect x="4" y="4" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.2" />
                        <path d="M8 4V3a1 1 0 00-1-1H2a1 1 0 00-1 1v5a1 1 0 001 1h1" stroke="currentColor" strokeWidth="1.2" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
                <button
                  onClick={handleExecute}
                  className="px-3 py-1.5 rounded-md text-[12px] font-medium transition-all"
                  style={{ background: executing ? "var(--color-surface-3)" : "rgba(255,255,255,0.08)", color: "var(--color-text-muted)" }}
                >
                  {executing ? "Running..." : "Run Test"}
                </button>
              </div>
            </div>

            {execution && (
              <div className="mx-5 mb-4 rounded-lg px-4 py-3 text-[11px]" style={{ background: execution.success ? "var(--color-success-soft)" : "var(--color-danger-soft)", color: execution.success ? "var(--color-success)" : "var(--color-danger)", fontFamily: "var(--font-mono)" }}>
                <div className="font-semibold mb-1">{execution.success ? "Execution succeeded" : "Execution failed"}</div>
                <pre className="whitespace-pre-wrap break-words">{execution.output}</pre>
              </div>
            )}

            {/* Line numbers + code */}
            <div className="flex overflow-auto" style={{ maxHeight: "calc(100vh - 320px)" }}>
              <div
                className="flex-shrink-0 px-4 py-5 text-right select-none"
                style={{ background: "var(--color-code-gutter)", minWidth: 44 }}
              >
                {Array.from({ length: 35 }, (_, i) => (
                  <div
                    key={i}
                    style={{ fontFamily: "var(--font-mono)", color: "var(--color-text-disabled)" }}
                    className="text-[12px] leading-6"
                  >
                    {i + 1}
                  </div>
                ))}
              </div>
              <div className="flex-1 px-5 py-5 overflow-x-auto">
                <pre
                  style={{ fontFamily: "var(--font-mono)", color: "var(--color-text)" }}
                  className="text-[13px] leading-6"
                >{code}</pre>
              </div>
            </div>

            {/* Status bar */}
            <div
              className="flex items-center justify-between px-4 py-2 border-t border-white/10 text-[11px]"
              style={{ fontFamily: "var(--font-mono)", color: "var(--color-text-muted)" }}
            >
              <div className="flex items-center gap-4">
                <span style={{ color: "var(--color-success)" }}>● Python</span>
                <span>UTF-8</span>
                <span>LF</span>
              </div>
              <div className="flex items-center gap-4">
                <span>Generated by Developer Agent</span>
                <span>08:42:30</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}