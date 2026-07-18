"""
LangGraph wiring for the SDR (Skill Deprecate Runway) pipeline.

Graph shape:

    START -> extract_trends -> match_and_score -> END

State carries the user's raw stack in, and the computed SDR results out.
This is intentionally a simple linear graph for the prototype — PECC and
UPE will likely become their own graphs (or branches) added later.
"""

from typing import List, TypedDict

from langgraph.graph import StateGraph, START, END

from agents.market_extractor import get_market_trends
from agents.matching_engine import compute_sdr, SDRResult


class SDRState(TypedDict):
    user_stack: List[str]
    trend_notes: List[str]        # populated by extract_trends, used for logging/debug
    results: List[SDRResult]       # final output


def extract_trends_node(state: SDRState) -> SDRState:
    """Market Data Extractor Agent step.

    In this prototype it just confirms which of the user's techs have a
    trend entry available (mocked data). Kept as its own node so it can be
    swapped for real web-scraping/search later without touching the rest
    of the graph.
    """
    notes = []
    for tech in state["user_stack"]:
        trend = get_market_trends(tech)
        if trend:
            notes.append(f"{tech}: signal found -> {trend['emerging_replacement']}")
        else:
            notes.append(f"{tech}: no signal, treated as stable")

    return {**state, "trend_notes": notes}


def match_and_score_node(state: SDRState) -> SDRState:
    """Matching Engine Node step — computes the SDR score per tech."""
    results = compute_sdr(state["user_stack"])
    return {**state, "results": results}


def build_sdr_graph():
    graph = StateGraph(SDRState)

    graph.add_node("extract_trends", extract_trends_node)
    graph.add_node("match_and_score", match_and_score_node)

    graph.add_edge(START, "extract_trends")
    graph.add_edge("extract_trends", "match_and_score")
    graph.add_edge("match_and_score", END)

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
