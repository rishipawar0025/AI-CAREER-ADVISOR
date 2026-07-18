"""
Market Data Extractor Agent
---------------------------
For the prototype phase this returns MOCKED trend data instead of live
scraping. Swap `get_market_trends()` internals later for a real web-scraping
/ web-search based extractor without touching any other file — the rest of
the graph only depends on the dict shape returned here.

Each entry represents a "current -> emerging" pair for a technology, with a
rough deprecation-speed rating (how fast the market is moving away from the
current tech) used later by the matching engine to compute a runway.
"""

from typing import Dict, List, TypedDict


class TrendEntry(TypedDict):
    current_tech: str
    emerging_replacement: str
    deprecation_speed: str   # "slow" | "moderate" | "fast"
    signal_sources: List[str]


# Mocked trend dataset. Keys are lowercased tech names for easy matching.
MOCK_TREND_DB: Dict[str, TrendEntry] = {
    "react": {
        "current_tech": "React 18 (Client Components)",
        "emerging_replacement": "React Server Components / Next.js Server Actions",
        "deprecation_speed": "moderate",
        "signal_sources": ["Job postings trending toward RSC", "Next.js adoption surge"],
    },
    "react 18": {
        "current_tech": "React 18",
        "emerging_replacement": "React Server Components / Next.js Server Actions",
        "deprecation_speed": "moderate",
        "signal_sources": ["Job postings trending toward RSC", "Next.js adoption surge"],
    },
    "jquery": {
        "current_tech": "jQuery",
        "emerging_replacement": "Vanilla JS / Modern frameworks (React, Vue, Svelte)",
        "deprecation_speed": "fast",
        "signal_sources": ["Declining jQuery job listings", "Framework-first hiring"],
    },
    "mern": {
        "current_tech": "MERN Stack",
        "emerging_replacement": "Full-stack TS (Next.js + tRPC + Postgres)",
        "deprecation_speed": "slow",
        "signal_sources": ["Still widely hired for", "Gradual shift to typed full-stack"],
    },
    "python 2": {
        "current_tech": "Python 2",
        "emerging_replacement": "Python 3.12+",
        "deprecation_speed": "fast",
        "signal_sources": ["EOL long past", "Zero new job listings"],
    },
    "tensorflow 1": {
        "current_tech": "TensorFlow 1.x",
        "emerging_replacement": "PyTorch / TensorFlow 2.x",
        "deprecation_speed": "fast",
        "signal_sources": ["Research community fully on PyTorch"],
    },
    "manual ml pipelines": {
        "current_tech": "Manual ML pipeline scripting",
        "emerging_replacement": "LangGraph / Agentic orchestration frameworks",
        "deprecation_speed": "moderate",
        "signal_sources": ["Rising demand for agentic AI engineers"],
    },
}

# Speed -> baseline runway in days (before adjustments in matching_engine.py)
SPEED_TO_BASE_DAYS = {
    "fast": 60,
    "moderate": 150,
    "slow": 365,
}


def get_market_trends(tech_query: str) -> TrendEntry | None:
    """Look up mocked trend data for a given technology name.

    Returns None if we have no signal for that tech (caller should treat
    this as 'currently stable / no strong deprecation signal').
    """
    key = tech_query.strip().lower()
    return MOCK_TREND_DB.get(key)


def list_known_techs() -> List[str]:
    """Utility for the frontend to show autocomplete / demo suggestions."""
    return sorted({v["current_tech"] for v in MOCK_TREND_DB.values()})
