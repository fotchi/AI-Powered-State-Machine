# AI-Powered State Machine — FLYNC AI QA Platform

An AI-driven QA platform that **generates test scenarios and executable test scripts** for [FLYNC](https://github.com/Technica-Engineering/FLYNC), Technica Engineering's automotive network configuration model (ECUs, buses, SOME/IP, TSN, security, signals, and more).

It combines a multi-agent LLM pipeline, a **coverage engine built on state machines** that finds which validation paths are still untested, and a web dashboard to launch runs, watch them live, and inspect the results.

---

## How it works

```
 FLYNC docs + source code (GitHub, auto-refreshed)
              │
              ▼
┌───────────────────────────┐    ┌───────────────────────────────┐
│ Phase 1 — Scenario Agent  │ ─▶ │ Phase 2 — Script Agent        │
│ 11 submodel agents        │    │ Discovery → Reader → Verifier │
│ + cross-module scenarios  │    │ → Developer (LLM / template)  │
│ + coverage-driven filling │    │ Executes every generated test │
└───────────────────────────┘    └───────────────────────────────┘
              │                                  │
              └──────────────┬───────────────────┘
                             ▼
            FastAPI backend (runs, WebSocket logs, auth, audit)
                             ▼
                 React dashboard (live pipeline view)
```

### Phase 1 — Scenario generation (`phase1/`)

- **11 submodel agents** (`app`, `bus`, `communication`, `ecu`, `metadata`, `nm`, `security`, `signal`, `someip`, `topology`, `tsn`) run in parallel through a LangGraph orchestrator. Each follows an *Actor → Critic* pattern: the actor writes **Positive** scenarios, the critic audits them and mutates them into **Negative** ones with an injected fault.
- **Semantic deduplication** with `all-MiniLM-L6-v2` embeddings and cosine similarity (threshold 0.85), while guaranteeing at least one scenario per submodel survives.
- **Cross-module scenarios grounded in the real code**: a relation graph is extracted from the FLYNC source with `ast` (no LLM cost). Every real cross-module reference gets a Positive and a Dangling-reference scenario; submodel pairs with no real relation get Isolation scenarios. The number of LLM calls is capped.
- **Freshness checks**: FLYNC docs and source are re-downloaded only when the upstream commit changes (throttled to one check every 6 hours).
- **LLM router** with multi-key round-robin, retry with backoff on rate limits/overload, and critic throttling. Defaults: Groq (generator + critic) and Gemini (integrator), configurable via env vars.

### Coverage engine — the state machines (`phase1/coverage/`)

Twelve state machines model the validation chain of FLYNC objects: **ECU, Controller, Ethernet, CAN, LIN, Socket, Endpoint, Deployment, SOME/IP, PDU, Signal, Frame**.

1. Each state with a `coverage_tag` expects one `PASS` case and one `FAIL_*` case.
2. The engine enumerates every expected case, matches them against existing scenarios (including an LLM-based semantic judge), and reports the gaps.
3. The gap filler generates exactly the missing scenarios — the same mechanism as the dashboard's "Generate Scenario" form.

```bash
cd phase1
python coverage_cli.py report <machine_key>   # e.g. ecu, can, someip
python coverage_cli.py fill   <machine_key>   # generate the missing scenarios
```

### Phase 2 — Script generation and execution (`phase2/`)

Turns each scenario into a runnable Python script against the real FLYNC SDK:

| Step | Package | Role |
|------|---------|------|
| 1 | `etape1_discovery` | Clones/updates FLYNC and discovers modules at run time |
| 2 | `etape2_lecteur` | Reads classes, fields and module relations from the source |
| 3 | `etape3_verificateur` | Resolves each scenario against the code index (verifies the target class/field exists) |
| 4 | `etape4_developpeur` | Generates the script (`template` or `llm` mode), **executes it in a subprocess** (30 s timeout), and feeds real stderr back to the LLM for retries |

Scripts are filed by category in `phase2/generated_scripts_/`:

- `mono_module/` — single-submodel scenarios
- `cross_module/` — scenarios spanning two submodels
- `out_of_scope/` — scenarios that cannot be proven or disproved in isolation; these are documented rather than counted as failures

LLM backends for Phase 2: `ollama`, `anthropic`, `gemini`, or `groq`.

### Backend (`backend/`)

FastAPI service that orchestrates a full run (Phase 1 → Phase 2) in a background thread, runs each phase as a subprocess, and streams logs live.

- **Auth**: JWT with role-based access (admin-only audit log and metrics)
- **Storage**: SQLAlchemy — SQLite by default, PostgreSQL via `DATABASE_URL` (`backend/scripts/setup_postgres.py` sets up a local one)
- **Object store**: S3-compatible (AWS S3 or MinIO) when `S3_BUCKET` is set, otherwise Fernet-encrypted local files
- **Realtime**: WebSocket stream per run at `/runs/{run_id}/stream`
- **Endpoints**: `/runs`, `/scenarios`, `/scripts` (incl. execute / execute-all), `/coverage` (machines, consistency, fill), `/artifacts`, `/audit`, `/metrics`, `/health`

### Frontend (`frontend/`)

React 19 + TypeScript + Vite + Tailwind 4 + TanStack Query. Screens: Dashboard, Generate Scenario, Scenario Details, Agent Pipeline, State Machine, Generated Code, Validation Results, Scenario History, and Audit Log.

---

## Repository layout

```
.
├── backend/            FastAPI app (routers, services, auth, DB, object store)
├── frontend/           React dashboard
├── phase1/             Scenario Agent
│   ├── agents/         11 submodel agents + LLM router
│   ├── orchestrator/   LangGraph pipeline (fan-out → dedup → cross-module)
│   ├── coverage/       Coverage engine + 12 state machines
│   ├── graph_builder/  FLYNC source download + relation graph (ast)
│   ├── retriever/      Documentation retrieval
│   ├── knowledge_base/ Domain, automotive and networking rules
│   └── output/         Generated scenarios (JSON)
├── phase2/             Script Agent
│   ├── src/flync_pipeline/   Discovery → Reader → Verifier → Developer
│   └── generated_scripts_/   Generated test scripts
├── requirements.txt    Python deps for phase 1 / phase 2
└── .mise.toml          Node 22 + pnpm
```

---

## Getting started

### Prerequisites

- Python 3.10+
- Node 22 and pnpm (`mise install` reads `.mise.toml`)
- API keys for at least one LLM provider (see below)

### 1. Install

```bash
# Python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r backend/requirements.txt

# Frontend
cd frontend && pnpm install
```

### 2. Configure

Create `phase1/.env` and `phase2/.env` (both are git-ignored):

```env
# LLM providers
GROQ_API_KEYS=key1,key2              # comma-separated for round-robin (or GROQ_API_KEY)
GOOGLE_API_KEYS_INTEGRATOR=key1,key2 # Gemini integrator (or GOOGLE_API_KEY_INTEGRATOR)
ANTHROPIC_API_KEY=                   # optional, Phase 2
GEMINI_API_KEY=                      # optional, Phase 2

# Optional: raises the GitHub API rate limit for docs/source refresh
GITHUB_TOKEN=

# Optional model overrides
GROQ_GENERATOR_MODEL=
GROQ_CRITIC_MODEL=
GEMINI_MODEL=
GROQ_MODEL_PHASE2_MONO=
GROQ_MODEL_PHASE2_CROSS=
OLLAMA_MODEL=
```

Backend settings (environment variables or `backend/.env`):

```env
JWT_SECRET=change-me          # REQUIRED in production (an insecure dev default is used otherwise)
DATABASE_URL=                 # defaults to SQLite at backend/flync.sqlite3
S3_BUCKET=                    # enables S3/MinIO object storage
S3_ENDPOINT_URL=              # e.g. a local MinIO endpoint
OBJECT_STORE_ENCRYPTION_KEY=  # key for the encrypted local fallback store
```

### 3. Run

```bash
# Backend (from the repository root) — http://localhost:8000
uvicorn backend.app.main:app --reload --port 8000

# Frontend — http://localhost:8443
cd frontend && pnpm dev
```

The frontend calls `http://localhost:8000` by default; override with `VITE_API_URL`. Open the dashboard, sign in, and start a run from **Generate Scenario**.

### Command-line usage (no UI)

```bash
# Full Scenario Agent pipeline
cd phase1 && python main.py

# One submodel with a custom requirement
cd phase1 && python run_single_cli.py '{"module": "ecu", ...}'

# Phase 2: generate and run scripts from a scenarios file
python -m phase2.src.flync_pipeline.etape4_developpeur.agent_developpeur \
  --scenarios phase1/output/scenarios_submodels.json \
  --mode llm --llm-backend groq --output-dir phase2/generated_scripts_
```

---

## Notes

- The first run downloads FLYNC docs and source and caches them locally (`phase1/data/`, `~/.flync_kb_cache`). Later runs only refresh when upstream changes.
- Free-tier LLM quotas drive several design choices (key rotation, call caps, critic throttling). Provide multiple keys for larger runs.
- `frontend/vite.config.ts` reads `../.figma/make/site.json`, which comes from the Figma Make export and is not tracked in this repository. Create it (e.g. `{}`) or remove that import if the dev server fails to start.
- The generated scenarios and scripts already committed under `phase1/output/` and `phase2/generated_scripts_/` can be browsed in the dashboard without running the pipeline.

## Acknowledgements

Built on top of [FLYNC](https://github.com/Technica-Engineering/FLYNC) by Technica Engineering.
