# AI Career Advisor — SDG 8 (Decent Work & Economic Growth)

## What this project is
An agentic system that tracks "Market-Facing Adaptability Metrics" instead of
a simple resume match score. Three KPIs, each implemented as its own
LangGraph pipeline:

1. **SDR — Skill Deprecate Runway** (BUILT, prototype stage)
   How many days until a user's current tech stack is meaningfully outdated
   vs. emerging market trends. Dashboard shows a runway progress bar per
   technology.

2. **PECC — Portfolio Edge-Case Coverage** (NOT YET BUILT)
   Given a project's code/flow description, score how many enterprise-grade
   edge cases (security, validation, error handling) are actually covered.
   Dashboard: radial "Enterprise Failure Shielding Score".

3. **UPE — Upskilling Pivot Elasticity** (NOT YET BUILT)
   Given a Current_State and Target_State (e.g. MERN -> ML pipelines),
   estimate pivot friction as a 1-10 "Pivot Effort Score" using a
   cross-domain semantic graph.

## Tech stack
- Backend: Python, LangGraph (agent orchestration), FastAPI (REST API)
- Frontend: plain HTML/JS dashboard (frontend/index.html) — no build step
- Data: MOCKED for prototype phase (see backend/agents/market_extractor.py).
  Swap for a real web-search/scraping extractor later without touching the
  graph or matching engine.

## Current file layout
```
backend/
  agents/
    market_extractor.py   # mocked trend data lookup
    matching_engine.py     # computes runway score per tech
  graph.py                 # LangGraph StateGraph wiring (extract -> match)
  main.py                  # FastAPI app, exposes POST /analyze
  requirements.txt
frontend/
  index.html               # single-file dashboard, calls localhost:8001
```

## How to run
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
Then open `frontend/index.html` directly in a browser (or serve it with
`python -m http.server` from the frontend folder).

## Conventions / notes for Claude Code
- Keep each KPI as its own LangGraph graph file (graph.py, graph_pecc.py,
  graph_upe.py) rather than merging into one giant graph, so KPIs can be
  demoed independently.
- Mocked data lives only in the `agents/` layer — never hardcode mock values
  directly inside graph.py or main.py, so real data sources can be swapped
  in later with minimal diff.
- Frontend stays framework-free (plain HTML/JS) unless explicitly asked to
  move to React — this is a hackathon-speed prototype.
- When adding PECC or UPE, follow the same pattern as SDR: agent module(s)
  in agents/, a graph.py-style wiring file, and a FastAPI endpoint.

## Next build steps (in order)
1. PECC: accept a code snippet or flow description, mock a "Code Reviewer
   Node" that flags presence/absence of security & validation patterns.
2. UPE: accept current_state + target_state strings, mock a semantic
   distance score between them, output a 1-10 pivot effort score.
3. Combine all 3 into one dashboard with tabs.
4. Replace mocked market_extractor with real web-search based trend
   fetching.
