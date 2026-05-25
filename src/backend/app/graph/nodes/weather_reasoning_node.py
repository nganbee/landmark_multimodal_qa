import json

from src.backend.app.graph.state import AgentState

from src.backend.app.llm.groq_client import (
    invoke_json_llm
)

from src.backend.app.llm.prompts.weather_prompts import (
    WEATHER_REASONING_PROMPT
)


# =========================================================
# PROVIDER LIMITS
# =========================================================

MAX_FORECAST_DAYS = 5


# =========================================================
# WEATHER REASONING NODE
# =========================================================

def weather_reasoning_node(
    state: AgentState
):

    query = state.get(
        "user_query",
        ""
    )

    prompt = f"""
{WEATHER_REASONING_PROMPT}

=========================================================
USER QUERY
=========================================================

{query}
"""

    response = invoke_json_llm(prompt)

    try:

        parsed = json.loads(response)

    except Exception:

        parsed = {

            "weather_type":
            "current",

            "forecast_days":
            0,

            "forecast_hours":
            0,

            "reasoning":
            "Fallback reasoning."
        }

    # =====================================================
    # NORMALIZE FORECAST DAYS
    # =====================================================

    forecast_days = parsed.get(
        "forecast_days",
        0
    )

    forecast_days = min(

        forecast_days,

        MAX_FORECAST_DAYS
    )

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "weather_type":
        parsed.get(
            "weather_type",
            "current"
        ),

        "forecast_days":
        forecast_days,

        "forecast_hours":
        parsed.get(
            "forecast_hours",
            0
        ),

        "weather_reasoning":
        parsed.get(
            "reasoning",
            ""
        ),

        "provider_max_days":
        MAX_FORECAST_DAYS
    }