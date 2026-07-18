"""
LangGraph wiring for the SDR (Skill Deprecate Runway) pipeline.
START -> extract_trends -> match_and_score -> END
"""

from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END

# --- Dynamic Mock Layer (Replaces the missing 'agents' folder dependency) ---
def get_market_trends(tech: str):
    # Mock market signal tracking layer
    legacy_keywords = ["excel basic", "data entry", "jquery", "cold calling", "manual filing"]
    if any(l in tech.lower() for l in legacy_keywords):
        return {"emerging_replacement": "AI-Driven Automation"}
    return None

def compute_sdr(user_stack: List[str]):
    # Mock calculation logic tracking layer
    results = []
    for tech in user_stack:
        results.append({
            "tech": tech,
            "runway_days": 365,
            "status": "healthy"
        })
    return results
# ----------------------------------------------------------------------------

class SDRState(TypedDict):
    user_stack: List[str]
    trend_notes: List[str]        
    results: List[dict]       

def extract_trends_node(state: SDRState) -> SDRState:
    notes = []
    for tech in state["user_stack"]:
        trend = get_market_trends(tech)
        if trend:
            notes.append(f"{tech}: signal found -> {trend['emerging_replacement']}")
        else:
            notes.append(f"{tech}: no signal, treated as stable")
    return {**state, "trend_notes": notes}

def match_and_score_node(state: SDRState) -> SDRState:
    results = compute_sdr(state["user_stack"])
    return {**state, "results": results}

def build_sdr_graph():
    graph = StateGraph(SDRState)
    graph.add_node("extract_trends", extract_trends_node)
    graph.add_node("match_and_score", match_and_score_node)
    graph.add_edge(START, "extract_trends")
    graph.add_edge(extract_trends, "match_and_score")
    graph.add_edge(match_and_score, END)
    return graph.compile()

# Compiled once at import time and reused across requests.
sdr_graph = build_sdr_graph()

def run_sdr_pipeline(user_stack: List[str]) -> SDRState:
    initial_state: SDRState = {
        "user_stack": user_stack,
        "trend_notes": [],
        "results": [],
    }
    return sdr_graph.invoke(initial_state)
