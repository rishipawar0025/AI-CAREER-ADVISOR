"""
Matching Engine Node
--------------------
Takes the user's declared tech stack + the market trend signals fetched by
the Market Extractor agent, and computes a "Skill Deprecate Runway" (SDR)
per technology: how many days until it's considered meaningfully outdated
relative to the emerging replacement.
"""

from typing import List, TypedDict

from .market_extractor import SPEED_TO_BASE_DAYS, get_market_trends


class SDRResult(TypedDict):
    tech: str
    runway_days: int
    status: str                # "critical" | "watch" | "healthy"
    replacement_trend: str | None
    note: str


def _status_from_days(days: int) -> str:
    if days <= 60:
        return "critical"
    if days <= 180:
        return "watch"
    return "healthy"


def compute_sdr(user_stack: List[str]) -> List[SDRResult]:
    """Compute SDR for every technology the user listed.

    user_stack: list of tech names as the user typed them, e.g.
        ["React 18", "MERN", "jQuery"]
    """
    results: List[SDRResult] = []

    for tech in user_stack:
        trend = get_market_trends(tech)

        if trend is None:
            # No strong signal in our (mocked) trend DB -> treat as stable.
            results.append(
                {
                    "tech": tech,
                    "runway_days": 365,
                    "status": "healthy",
                    "replacement_trend": None,
                    "note": "No strong deprecation signal detected yet.",
                }
            )
            continue

        base_days = SPEED_TO_BASE_DAYS[trend["deprecation_speed"]]

        results.append(
            {
                "tech": tech,
                "runway_days": base_days,
                "status": _status_from_days(base_days),
                "replacement_trend": trend["emerging_replacement"],
                "note": (
                    f"Market signals: {', '.join(trend['signal_sources'])}"
                ),
            }
        )

    return results
