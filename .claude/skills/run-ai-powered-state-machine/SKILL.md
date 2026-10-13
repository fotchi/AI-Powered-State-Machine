---
name: run-ai-powered-state-machine
description: Build, run, and drive the FLYNC AI test-generation platform (FastAPI backend + React/Vite frontend, backed by the phase1 scenario-generation and phase2 script-generation pipelines). Use when asked to start the app, run the backend or frontend dev servers, take a screenshot of the UI, verify the API, or interact with the running dashboard.
---

This is a Windows project: a FastAPI backend (`backend/`, port 8000) serving
a React/Vite SPA (`frontend/`, port 8443). The backend shells out to two
sibling pipelines — `phase1/` (LangGraph scenario generation) and `phase2/`
(script generation) — as subprocesses; they are not run independently.
Drive the running app via `curl`/`Invoke-WebRequest` for the API and via
the Playwright-core driver at
`.claude/skills/run-ai-powered-state-machine/driver.mjs` for the UI (no
`chromium-cli` is installed on this machine; the driver uses the
system-installed Edge browser instead of downloading one).

All paths below are relative to the repo root
(`C:\Users\AZIZ\Desktop\AI-Powered-State-Machine`).

## Prerequisites

- Python 3.13+ on PATH as `python` (verified: `python --version` -> `Python 3.13.5`).
- Node 22+, and `pnpm` on PATH (verified: `node --version` -> `v24.13.0`, `pnpm --version` -> `10.28.2`).
- Microsoft Edge or Google Chrome installed (used by the UI driver via Playwright's `channel` option — no browser download needed).

## Setup

```powershell
# Python venv (repo root) + the backend's OWN lightweight runtime deps.
# Do NOT run the full `pip install -r requirements.txt` just to run the
# app — see Gotchas: it pulls langchain/langgraph/torch (100s of MB) that
# only phase1's pipeline needs, not the FastAPI process itself.
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" "pydantic>=2.5,<3" "sqlalchemy>=2.0,<3" "boto3>=1.34" python-dotenv
```

```powershell
# Frontend deps
cd frontend
pnpm install
cd ..
```

```powershell
# UI driver deps (one-time; installs playwright-core only — no browser
# binary download, ~8s)
cd .claude\skills\run-ai-powered-state-machine
npm install
cd ..\..\..
```

## Run (agent path)

Start both dev servers in the background and poll for readiness (don't
use a blocking `npm start`/`uvicorn` in the foreground — the agent needs
its shell back). Verified this session, from a bash-style shell:

```bash
cd backend && ../.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$TEMP/backend_dev.log" 2>&1 &
disown
cd ../frontend && pnpm run dev > "$TEMP/frontend_dev.log" 2>&1 &
disown
```

Wait for readiness by polling, not `sleep`:

```bash
timeout 30 bash -c 'until curl -sf http://localhost:8000/health >/dev/null 2>&1; do sleep 1; done; echo BACKEND_READY'
timeout 30 bash -c 'until curl -sf http://localhost:8443/ >/dev/null 2>&1; do sleep 1; done; echo FRONTEND_READY'
```

### Verify the API

```bash
curl http://localhost:8000/health
# -> {"status":"ok","service":"flync-backend","teams":["phase1","phase2"]}
curl http://localhost:8000/scenarios   # -> {"run_id":null,"scenarios":[...158 items from phase1/output/*.json...]}
curl http://localhost:8000/scripts     # -> {"run_id":null,"scripts":[...117 items from phase2/generated_scripts_/**/*.py...]}
```

`/scenarios` and `/scripts` with no `run_id` read directly off disk
(`phase1/output/scenarios_submodels.json` + `scenarios_cross_module.json`,
and `phase2/generated_scripts_/**/*.py`) — this is what the Dashboard,
Scenario History, Scenario Details, State Machine, and Generated Code
screens all render by default.

### Drive the UI

```bash
cd .claude/skills/run-ai-powered-state-machine
node driver.mjs smoke-script.txt
```

`smoke-script.txt` (committed alongside the driver) is a plain text
script, one command per line, same vocabulary as `chromium-cli`:

```
nav http://localhost:8443/
sleep 1500
screenshot 01-landing
click-text Generated Code
sleep 800
screenshot 02-generated-code
click-text Scenario History
sleep 800
screenshot 03-scenario-history
console
```

Verified output (this session, against the servers started above):

```
nav -> http://localhost:8443/
screenshot -> .../screenshots/01-landing.png
click-text OK: Generated Code
screenshot -> .../screenshots/02-generated-code.png
click-text OK: Scenario History
screenshot -> .../screenshots/03-scenario-history.png
console --errors -> Failed to load resource: the server responded with a status of 404 (Not Found)
```

(That 404 is benign — see Gotchas.) Screenshots land in
`.claude/skills/run-ai-powered-state-machine/screenshots/` (override with
`SCREENSHOT_DIR`). Write your own command file for a different flow —
the driver doesn't require `smoke-script.txt` specifically.

| command | what it does |
|---|---|
| `nav <url>` | navigate |
| `wait-for <css-sel>` or `wait-for text=<text>` | wait up to 15s for an element |
| `click <css-sel>` | click element |
| `click-text <text>` | click first element containing this text |
| `fill <css-sel> <value>` | fill an input |
| `press <key>` | keyboard key press |
| `screenshot [name]` | full-page screenshot -> `screenshots/<name>.png` |
| `eval <js-expr>` | evaluate JS in the page, print JSON |
| `text [css-sel]` | print `innerText` of an element (default `body`) |
| `console` | print collected `console.error`/`pageerror` messages since launch |
| `sleep <ms>` | pause (use `wait-for` instead where possible) |

### Stop

```powershell
(Get-NetTCPConnection -LocalPort 8000 -State Listen).OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
(Get-NetTCPConnection -LocalPort 8443 -State Listen).OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

This is the normal Windows recipe (kill by port, since `$!`/job objects
from `Start-Process`/`&` only give you a wrapper PID, not the real
`uvicorn`/`node` worker) and it worked the first time I verified this
skill, from a plain interactive PowerShell/bash session. **If you're an
agent driving this through Claude Code's own Bash/PowerShell tools,
read the Gotcha below before relying on this** — it stopped working the
second time, in a way worth knowing about in advance.

## Run (human path)

```powershell
cd backend; ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload   # Ctrl-C to stop
cd frontend; pnpm run dev                                                  # Ctrl-C to stop
```

Then open `http://localhost:8443/` in a browser.

## Test

There is no automated test suite for the backend or frontend (no
`pytest`/`vitest` config, no `test` script in `frontend/package.json`).
Use the driver above as the verification method: a clean landing-page
screenshot with real data plus an empty (or known-benign) `console
--errors` is the smoke signal.

## Gotchas

- **The full `pip install -r requirements.txt` is NOT needed to run the
  app.** It pulls `langchain`/`langgraph`/`sentence-transformers`/`torch`
  (torch alone is a 124MB wheel) — those are only used when the backend
  actually spawns `phase1/main.py` to run a *new* generation pipeline, not
  by the FastAPI process itself. Install just the backend's own deps
  (Setup, above) to get the server running fast; install the full
  `requirements.txt` separately only if you need to trigger a new run
  from the "Generate Scenario" screen.
- **A checked-in `.venv/` can be stale.** This repo had a committed
  `.venv` whose `pyvenv.cfg` pointed at a Python install path from a
  different machine/user — every `.venv\Scripts\python.exe` invocation
  failed with `did not find executable at '...'`. Fix: delete `.venv`
  and recreate it with the local `python -m venv .venv`.
- **No `chromium-cli` on this machine, and Playwright's own Chromium
  download is impractical here** (slow/limited network — the backend
  deps install alone took a long time for a 124MB file). The driver
  uses `playwright-core` with `channel: 'msedge'`, which drives the
  already-installed system Edge — no browser download at all.
- **A benign 404 always shows up in `console --errors`** on the
  frontend routes exercised above. It is NOT from the backend — the
  backend's own log (`$TEMP/backend_dev.log`) shows only `200 OK` for
  every `/scenarios`/`/scripts` call made during the same run. It's a
  Vite-dev-server-side asset (looks like a missing favicon), not a
  functional break. Don't chase it as a real bug; do treat a *new*,
  different console error as a real signal.
- **`pnpm install` can refuse to touch an existing `node_modules/`
  non-interactively**: `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`.
  Fix: set `CI=true` (`CI=true pnpm install` in bash, or `$env:CI="true"`
  in PowerShell before the call) when running it from an agent/script.
- **A server started with `run_in_background: true` can become
  unkillable-by-PID from a later, separate tool call.** Verified this
  session: after restarting the backend via a backgrounded Bash call, a
  *later* ad-hoc call's `Get-NetTCPConnection` correctly identified the
  listening PID and traffic flowed to it (`curl` got `200`, `netstat -ano`
  showed it `LISTENING`) — but `Stop-Process -Id`, `taskkill /PID`, *and*
  WMI's `Get-CimInstance Win32_Process` + `.Terminate()` all independently
  reported "no such process" for that exact PID, from both the Bash and
  PowerShell tools. Three different process-management APIs agreed the
  PID doesn't exist while the kernel's own TCP table (`netstat`) showed
  it very much alive and serving requests. This looks like each ad-hoc
  tool invocation getting its own process-table view while sharing the
  host's network stack with whatever a backgrounded call left running —
  i.e. a property of the Bash/PowerShell tool sandbox itself, not of
  uvicorn, Windows, or this app. Practical takeaway: don't count on
  killing a backgrounded dev server by PID/port from a fresh tool call.
  If you need a clean restart, do the stop attempt from the *same*
  Bash invocation that's about to relaunch it (kill, then immediately
  `&&` the relaunch in one call), or just accept the old instance keeps
  running in the background and start the replacement on a different
  port.
- **Data is file-backed, not run-backed, by default.** `/scenarios` and
  `/scripts` with no `run_id` read straight off
  `phase1/output/*.json` / `phase2/generated_scripts_/**/*.py` on disk —
  this is what you see on first load with zero pipeline runs. Only the
  "Agent Pipeline" screen (and `GET /runs/{id}`) care about a specific
  `run_id`, which is only set in `localStorage` after starting a run
  from the "Generate Scenario" screen.

## Troubleshooting

- **`curl: (7) Failed to connect` / `TcpTestSucceeded: False` on 8000 or
  8443**: the corresponding dev server isn't up yet or crashed on start.
  Check `$env:TEMP\backend_dev.log` / `$env:TEMP\frontend_dev.log` — a
  backend crash here is almost always a missing Python package (see the
  Setup deps list); a frontend crash is almost always a `pnpm install`
  that didn't complete.
- **`did not find executable at 'C:\Users\<other-user>\...\python.exe'`**
  when running anything under `.venv\Scripts\`: see the stale-venv
  Gotcha above — recreate `.venv`.
- **`pip install -r requirements.txt` hangs for a very long time on
  `Downloading torch-...whl`**: this is real progress on a slow link,
  not a hang (confirm with `pip cache info` — the cache size should be
  slowly growing). Either wait it out, or skip it entirely per the first
  Gotcha if you only need to run the app, not trigger a new pipeline.
- **PowerShell one-liners with `$_` mangled/misparsed when run through a
  wrapper that itself does shell-style `$`-substitution** (e.g. a bash
  tool invoking `powershell -Command "...$_..."`): the `$_` gets consumed
  before PowerShell sees it. Use a PowerShell-native tool/session, or
  single-quote the whole `-Command` argument so the outer shell doesn't
  touch it.
