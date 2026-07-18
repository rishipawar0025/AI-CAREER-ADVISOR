# AI Career Advisor — SDG 8 Prototype (SDR module)

Working end-to-end prototype of the **Skill Deprecate Runway** KPI, built
with LangGraph + FastAPI. This is the first of 3 planned KPIs — see
`CLAUDE.md` for the full project context and next steps.

## Quick start

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Then open `frontend/index.html` in your browser (double-click it, or run
`python -m http.server 5500` from inside `frontend/` and visit
`http://localhost:5500`).

Try the input box with: `React 18, MERN, jQuery` — these have mocked trend
data wired up already. Full list of demo-ready techs is served at
`GET /known-techs`.

## Test the API directly

```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"tech_stack": ["React 18", "jQuery", "MERN"]}'
```

## Continuing the build in VS Code with Claude Code

1. Open this folder in VS Code.
2. Install the Claude Code extension (`Ctrl+Shift+X` → search "Claude Code").
3. Open a terminal and run `claude` (or `claude --ide`), sign in.
4. Claude Code will read `CLAUDE.md` automatically for context — ask it to
   build the next KPI (PECC or UPE) following the same pattern as `SDR`.

Example prompt to paste into Claude Code:

> Read CLAUDE.md. Now build the PECC (Portfolio Edge-Case Coverage) module
> following the exact same pattern as the SDR module: a mocked "code
> reviewer" agent in agents/code_reviewer.py, a graph_pecc.py wiring file,
> and a new POST /review-portfolio endpoint in main.py. Also add a radial
> progress chart section to frontend/index.html for the Enterprise Failure
> Shielding Score.
