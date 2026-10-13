import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { apiFetch } from "../src/api";
import { MACHINE_LABELS, type MachineDef, type MachineMap } from "../src/machines";
import Button from "../components/Button";

interface StateMachineProps {
  onNavigate: (screen: string) => void;
}

type Direction = "top" | "bottom" | "left" | "right";
type CoverageStatus = "structural" | "covered" | "gap";

interface LayoutNode {
  id: string;
  x: number;
  y: number;
  onFail: string;
  coverageTag?: string;
}

const NODE_W = 220;
const NODE_H = 46;
const FAIL_W = 150;
const FAIL_H = 34;
const ROW_GAP = 110;
const MAIN_X = 260;
const FAIL_X = MAIN_X + NODE_W / 2 + 90;

function buildLayout(machine: MachineDef): { nodes: LayoutNode[]; terminalY: number } {
  const ids = Object.keys(machine.states);
  const nodes: LayoutNode[] = ids.map((id, i) => ({
    id,
    x: MAIN_X,
    y: 70 + i * ROW_GAP,
    onFail: machine.states[id].on_fail,
    coverageTag: machine.states[id].coverage_tag,
  }));
  return { nodes, terminalY: 70 + ids.length * ROW_GAP };
}

function getPoint(x: number, y: number, w: number, h: number, dir: Direction): [number, number] {
  if (dir === "top") return [x, y - h / 2];
  if (dir === "bottom") return [x, y + h / 2];
  if (dir === "left") return [x - w / 2, y];
  return [x + w / 2, y];
}

export default function StateMachine({ onNavigate }: StateMachineProps) {
  const [machines, setMachines] = useState<MachineMap>({});
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [machineKey, setMachineKey] = useState("ecu");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [coverage, setCoverage] = useState<{ expected_total: number; covered: number; gaps: { state: string; expected_outcome: string }[]; verification_method?: string } | null>(null);
  const [coverageLoading, setCoverageLoading] = useState(false);

  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState({ x: 40, y: 20, scale: 0.85 });
  const [panning, setPanning] = useState(false);
  const panStart = useRef({ mx: 0, my: 0, tx: 0, ty: 0 });

  useEffect(() => {
    apiFetch("/coverage/machines/describe")
      .then((res) => {
        if (!res.ok) throw new Error(`Backend returned ${res.status}`);
        return res.json();
      })
      .then((data: MachineMap) => setMachines(data))
      .catch((err) => setLoadError(err instanceof Error ? err.message : "Failed to load State Machines."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    setSelectedId(null);
    setCoverage(null);
  }, [machineKey]);

  // Non-passive wheel handler (same pan/zoom mechanics as before)
  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.88 : 1.14;
      const rect = el.getBoundingClientRect();
      const cx = e.clientX - rect.left;
      const cy = e.clientY - rect.top;
      setTransform((t) => {
        const ns = Math.max(0.2, Math.min(3, t.scale * delta));
        const ratio = ns / t.scale;
        return { x: cx - (cx - t.x) * ratio, y: cy - (cy - t.y) * ratio, scale: ns };
      });
    };
    el.addEventListener("wheel", handler, { passive: false });
    return () => el.removeEventListener("wheel", handler);
  }, []);

  const handleSvgMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    const target = e.target as SVGElement;
    if (target.tagName === "svg" || target.classList.contains("canvas-bg")) {
      setPanning(true);
      panStart.current = { mx: e.clientX, my: e.clientY, tx: transform.x, ty: transform.y };
      setSelectedId(null);
    }
  };
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!panning) return;
    const dx = e.clientX - panStart.current.mx;
    const dy = e.clientY - panStart.current.my;
    setTransform((t) => ({ ...t, x: panStart.current.tx + dx, y: panStart.current.ty + dy }));
  }, [panning]);
  const handleMouseUp = useCallback(() => setPanning(false), []);
  useEffect(() => {
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => { window.removeEventListener("mousemove", handleMouseMove); window.removeEventListener("mouseup", handleMouseUp); };
  }, [handleMouseMove, handleMouseUp]);

  const zoom = (factor: number) => {
    const el = containerRef.current;
    if (!el) return;
    const { width, height } = el.getBoundingClientRect();
    const cx = width / 2, cy = height / 2;
    setTransform((t) => {
      const ns = Math.max(0.2, Math.min(3, t.scale * factor));
      const ratio = ns / t.scale;
      return { x: cx - (cx - t.x) * ratio, y: cy - (cy - t.y) * ratio, scale: ns };
    });
  };

  const machine = machines[machineKey];
  const layout = useMemo(() => (machine ? buildLayout(machine) : null), [machine]);

  const fitToScreen = () => {
    const el = containerRef.current;
    if (!el || !layout) return;
    const { width, height } = el.getBoundingClientRect();
    const dH = layout.terminalY + 130;
    const dW = FAIL_X + FAIL_W;
    const s = Math.min((width - 60) / dW, (height - 60) / dH, 1.2);
    setTransform({ x: (width - dW * s) / 2, y: 20, scale: s });
  };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(fitToScreen, [machineKey, layout]);

  const checkCoverage = async () => {
    setCoverageLoading(true);
    setCoverage(null);
    try {
      const res = await apiFetch(`/coverage/${machineKey}`);
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);
      setCoverage(await res.json());
    } catch {
      /* left silent -- the panel below simply won't light up */
    } finally {
      setCoverageLoading(false);
    }
  };

  function statusFor(node: LayoutNode): CoverageStatus {
    if (!node.coverageTag) return "structural";
    if (!coverage) return "structural";
    const hasGap = coverage.gaps.some((g) => g.state === node.id);
    return hasGap ? "gap" : "covered";
  }

  const STATUS_COLOR: Record<CoverageStatus, { fill: string; stroke: string; text: string }> = {
    structural: { fill: "var(--color-surface)", stroke: "var(--color-border-strong)", text: "var(--color-text)" },
    covered: { fill: "var(--color-success-soft)", stroke: "var(--color-success)", text: "var(--color-success)" },
    gap: { fill: "var(--color-warning-soft)", stroke: "var(--color-warning)", text: "var(--color-warning)" },
  };

  const selectedNode = layout?.nodes.find((n) => n.id === selectedId) ?? null;
  const selectedTransitions = selectedId ? machine?.states[selectedId] : null;

  const groupedMachineKeys = useMemo(() => {
    const groups: Record<string, string[]> = {};
    for (const key of Object.keys(machines)) {
      const mod = machines[key].phase1_module;
      (groups[mod] ??= []).push(key);
    }
    return groups;
  }, [machines]);

  if (loading) {
    return <div className="p-8 text-[13px] text-[var(--color-text-muted)]">Loading State Machines…</div>;
  }
  if (loadError) {
    return <div className="p-8 text-[13px]" style={{ color: "var(--color-danger)" }}>{loadError}</div>;
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-3 flex items-center justify-between flex-shrink-0 z-10 flex-wrap gap-3">
        <div className="flex items-center gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-xs mb-0.5">
              <button onClick={() => onNavigate("dashboard")} className="hover:text-[var(--color-primary-bright)]">Dashboard</button>
              <span>/</span>
              <span className="text-[var(--color-text-secondary)] font-medium">State Machine</span>
            </div>
            <div style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-bold text-[15px]">
              {MACHINE_LABELS[machineKey] || machineKey} State Machine
            </div>
            <div className="text-[10px] text-[var(--color-text-muted)]">
              phase1/coverage/state_machines/{machineKey}_machine.py &middot; maps to the "{machine?.phase1_module}" agent
            </div>
          </div>

          {/* Machine picker, grouped by the module it maps to */}
          <div className="flex items-center gap-3 flex-wrap ml-2 pl-4 border-l border-[var(--color-border)]">
            {Object.entries(groupedMachineKeys).map(([mod, keys]) => (
              <div key={mod} className="flex items-center gap-1">
                <span className="text-[10px] text-[var(--color-text-disabled)] uppercase tracking-wider mr-1">{mod}</span>
                {keys.map((key) => (
                  <button
                    key={key}
                    onClick={() => setMachineKey(key)}
                    className="px-2 py-1 rounded-md text-[11px] font-medium transition-all"
                    style={
                      machineKey === key
                        ? { background: "var(--color-primary-soft)", color: "var(--color-primary-bright)" }
                        : { background: "var(--color-surface-2)", color: "var(--color-text-muted)" }
                    }
                  >
                    {MACHINE_LABELS[key] || key}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-[var(--color-surface-2)] border border-[var(--color-border)] rounded-lg p-1">
            <button onClick={() => zoom(0.82)} className="w-7 h-7 rounded flex items-center justify-center text-[var(--color-text-muted)] hover:bg-[var(--color-surface-3)] text-sm font-bold transition-all">−</button>
            <button onClick={fitToScreen} className="px-2 h-7 rounded text-[11px] font-semibold text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-3)] transition-all min-w-[46px]">
              {Math.round(transform.scale * 100)}%
            </button>
            <button onClick={() => zoom(1.22)} className="w-7 h-7 rounded flex items-center justify-center text-[var(--color-text-muted)] hover:bg-[var(--color-surface-3)] text-sm font-bold transition-all">+</button>
          </div>
          <Button variant="secondary" size="sm" onClick={fitToScreen}>Fit</Button>
          <Button variant="primary" size="sm" onClick={checkCoverage} disabled={coverageLoading}>
            {coverageLoading ? "Checking…" : "Check Coverage"}
          </Button>
          <Button variant="outline" size="sm" onClick={() => onNavigate("generation")}>
            Generate Scenario
          </Button>
        </div>
      </div>

      {/* Canvas + Panel */}
      <div className="flex flex-1 overflow-hidden">
        <div ref={containerRef} className="flex-1 overflow-hidden relative" style={{ background: "var(--color-bg)", cursor: panning ? "grabbing" : "grab" }}>
          <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
            <defs>
              <pattern id="grid-dots" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="0.8" fill="var(--color-border-strong)" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid-dots)" />
          </svg>

          <svg ref={svgRef} width="100%" height="100%" onMouseDown={handleSvgMouseDown} style={{ userSelect: "none" }}>
            <defs>
              <marker id="arrow-pass" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto" markerUnits="userSpaceOnUse">
                <polygon points="0 0, 8 3, 0 6" fill="var(--color-success)" />
              </marker>
              <marker id="arrow-fail" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto" markerUnits="userSpaceOnUse">
                <polygon points="0 0, 8 3, 0 6" fill="var(--color-danger)" />
              </marker>
            </defs>
            <rect className="canvas-bg" x="-99999" y="-99999" width="199999" height="199999" fill="transparent" />

            {layout && machine && (
              <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
                {layout.nodes.map((node, i) => {
                  const next = layout.nodes[i + 1];
                  const nextY = next ? next.y : layout.terminalY;
                  const [sx, sy] = getPoint(node.x, node.y, NODE_W, NODE_H, "bottom");
                  const [tx, ty] = [node.x, nextY - (next ? NODE_H / 2 : 22)];
                  const [fsx, fsy] = getPoint(node.x, node.y, NODE_W, NODE_H, "right");
                  const [ftx] = getPoint(FAIL_X, node.y, FAIL_W, FAIL_H, "left");
                  return (
                    <g key={node.id}>
                      {/* on_pass arrow down */}
                      <path d={`M ${sx} ${sy} V ${ty}`} stroke="var(--color-success)" strokeWidth="1.6" fill="none" markerEnd="url(#arrow-pass)" opacity="0.7" />
                      {/* on_fail arrow to the side label */}
                      <path d={`M ${fsx} ${fsy} H ${ftx}`} stroke="var(--color-danger)" strokeWidth="1.4" strokeDasharray="4 3" fill="none" markerEnd="url(#arrow-fail)" opacity="0.6" />
                      <rect x={FAIL_X - FAIL_W / 2} y={node.y - FAIL_H / 2} width={FAIL_W} height={FAIL_H} rx={6}
                        fill="var(--color-danger-soft)" stroke="var(--color-danger)" strokeOpacity="0.5" strokeWidth="1" />
                      <text x={FAIL_X} y={node.y} textAnchor="middle" dominantBaseline="middle" fontSize="9.5" fontWeight="600" fill="var(--color-danger)" fontFamily="var(--font-mono)">
                        {node.onFail}
                      </text>
                    </g>
                  );
                })}

                {/* Terminal pass pill */}
                {(() => {
                  const last = layout.nodes[layout.nodes.length - 1];
                  if (!last) return null;
                  return (
                    <g>
                      <rect x={MAIN_X - 90} y={layout.terminalY - 22} width={180} height={44} rx={22}
                        fill="var(--color-success-strong)" stroke="var(--color-success)" strokeWidth="1.5" />
                      <text x={MAIN_X} y={layout.terminalY} textAnchor="middle" dominantBaseline="middle" fontSize="12" fontWeight="700" fill="#052e13" fontFamily="var(--font-display)">
                        {machine.terminal_pass}
                      </text>
                    </g>
                  );
                })()}

                {/* State nodes */}
                {layout.nodes.map((node) => {
                  const status = statusFor(node);
                  const colors = STATUS_COLOR[status];
                  const selected = selectedId === node.id;
                  return (
                    <g key={node.id} onClick={(e) => { e.stopPropagation(); setSelectedId(node.id); }} style={{ cursor: "pointer" }}>
                      <rect
                        x={node.x - NODE_W / 2} y={node.y - NODE_H / 2} width={NODE_W} height={NODE_H} rx={8}
                        fill={colors.fill} stroke={selected ? "var(--color-primary-bright)" : colors.stroke}
                        strokeWidth={selected ? 2.5 : 1.5}
                      />
                      <text x={node.x} y={node.y - (node.coverageTag ? 6 : 0)} textAnchor="middle" dominantBaseline="middle" fontSize="10.5" fontWeight="700" fill={colors.text} fontFamily="var(--font-mono)">
                        {node.id}
                      </text>
                      {node.coverageTag && (
                        <text x={node.x} y={node.y + 11} textAnchor="middle" dominantBaseline="middle" fontSize="8.5" fill={colors.text} opacity="0.75" fontFamily="var(--font-mono)">
                          {status === "gap" ? "? unconfirmed" : status === "covered" ? "✓ covered" : node.coverageTag}
                        </text>
                      )}
                    </g>
                  );
                })}
              </g>
            )}
          </svg>

          <div className="absolute bottom-4 left-4 text-[10px] text-[var(--color-text-muted)] font-medium select-none">
            Scroll to zoom &middot; Drag to pan &middot; Click a state to inspect &middot; green = on_pass, red dashed = on_fail
          </div>
        </div>

        {/* Properties Panel */}
        <aside className="w-80 border-l border-[var(--color-border)] bg-[var(--color-surface)] flex flex-col overflow-hidden flex-shrink-0">
          {selectedNode && selectedTransitions ? (
            <div className="flex-1 overflow-y-auto">
              <div className="px-5 py-4 border-b border-[var(--color-border)]">
                <span
                  className="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider"
                  style={{ background: STATUS_COLOR[statusFor(selectedNode)].fill, color: STATUS_COLOR[statusFor(selectedNode)].text }}
                >
                  {statusFor(selectedNode) === "structural" ? "Structural State" : statusFor(selectedNode) === "covered" ? "Covered" : "Unconfirmed"}
                </span>
                <h3 style={{ fontFamily: "var(--font-mono)", color: "var(--color-text)" }} className="font-bold text-[14px] leading-tight mt-2">
                  {selectedNode.id}
                </h3>
              </div>

              <div className="px-5 py-4 border-b border-[var(--color-border)]">
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Transitions</div>
                <div className="space-y-2 text-[12px]">
                  <div className="flex justify-between gap-2">
                    <span style={{ color: "var(--color-success)" }}>on_pass →</span>
                    <span style={{ fontFamily: "var(--font-mono)", color: "var(--color-text)" }}>{selectedTransitions.on_pass}</span>
                  </div>
                  <div className="flex justify-between gap-2">
                    <span style={{ color: "var(--color-danger)" }}>on_fail →</span>
                    <span style={{ fontFamily: "var(--font-mono)", color: "var(--color-text)" }}>{selectedTransitions.on_fail}</span>
                  </div>
                </div>
              </div>

              <div className="px-5 py-4 border-b border-[var(--color-border)]">
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Coverage Tag</div>
                {selectedTransitions.coverage_tag ? (
                  <>
                    <span style={{ fontFamily: "var(--font-mono)", color: "var(--color-primary-bright)", background: "var(--color-primary-soft)" }} className="text-[11px] px-2 py-0.5 rounded font-medium">
                      {selectedTransitions.coverage_tag}
                    </span>
                    <p className="text-[11px] text-[var(--color-text-muted)] mt-2 leading-relaxed">
                      The Test Mutation Engine expects one PASS and one {selectedTransitions.on_fail} scenario for
                      this tag. Click "Check Coverage" above to see whether they already exist in phase1/output.
                    </p>
                  </>
                ) : (
                  <p className="text-[11px] text-[var(--color-text-muted)] leading-relaxed">
                    No coverage_tag -- this is a structural step in the chain (e.g. object creation), not a point
                    the coverage engine tracks on its own.
                  </p>
                )}
              </div>

              <div className="px-5 py-4">
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Maps To</div>
                <p className="text-[12px] text-[var(--color-text-secondary)]">
                  Scenario Agent module: <span style={{ fontFamily: "var(--font-mono)", color: "var(--color-text)" }}>{machine?.phase1_module}</span>
                </p>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto">
              <div className="px-5 py-4 border-b border-[var(--color-border)]">
                <h3 style={{ fontFamily: "var(--font-display)", color: "var(--color-text)" }} className="font-bold text-[14px] mb-1">
                  {MACHINE_LABELS[machineKey] || machineKey} Machine
                </h3>
                <p className="text-[11px] text-[var(--color-text-muted)] leading-relaxed">
                  Click any state to inspect its transitions and coverage tag. This is the real
                  state machine defined in code -- not an illustrative example.
                </p>
              </div>

              <div className="px-5 py-4 border-b border-[var(--color-border)]">
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Diagram Statistics</div>
                <div className="space-y-2">
                  {[
                    { label: "Total States", value: `${layout?.nodes.length ?? 0}` },
                    { label: "Coverage Points", value: `${layout?.nodes.filter((n) => n.coverageTag).length ?? 0}` },
                    { label: "Terminal (pass)", value: machine?.terminal_pass ?? "—" },
                  ].map((s) => (
                    <div key={s.label} className="flex justify-between">
                      <span className="text-[11px] text-[var(--color-text-muted)]">{s.label}</span>
                      <span style={{ fontFamily: "var(--font-mono)" }} className="text-[11px] font-semibold text-[var(--color-text)]">{s.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {coverage && (
                <div className="px-5 py-4 border-b border-[var(--color-border)]">
                  <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Coverage Result</div>
                  <p className="text-[12px] text-[var(--color-text-secondary)]">
                    {coverage.covered}/{coverage.expected_total} theoretical PASS/FAIL cases are covered;{" "}
                    {coverage.gaps.length} unconfirmed. Highlighted on the diagram in green / amber.
                  </p>
                  <p className="text-[10.5px] leading-relaxed mt-2" style={{ color: "var(--color-text-muted)" }}>
                    {coverage.verification_method === "keyword"
                      ? "Keyword-only check right now (AI review unavailable) -- \"unconfirmed\" isn't a guarantee nothing exists; verify before filling."
                      : "Checked by exact keyword first, then an AI review of each remaining rule against every existing scenario's actual meaning. Not infallible on judgment calls, so still worth a glance before filling."}
                  </p>
                </div>
              )}

              <div className="px-5 py-4">
                <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Legend</div>
                <div className="space-y-2">
                  {[
                    { label: "Structural state", color: "var(--color-border-strong)" },
                    { label: "Covered", color: "var(--color-success)" },
                    { label: "Unconfirmed", color: "var(--color-warning)" },
                    { label: "FAIL_* target", color: "var(--color-danger)" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center gap-2.5">
                      <div className="w-3 h-3 rounded-sm flex-shrink-0" style={{ background: `color-mix(in srgb, ${item.color} 25%, transparent)`, border: `1.5px solid ${item.color}` }} />
                      <span className="text-[11px] text-[var(--color-text-secondary)]">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
