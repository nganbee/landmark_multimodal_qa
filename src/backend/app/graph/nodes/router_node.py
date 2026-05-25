import json

from src.backend.app.graph.state import AgentState

from src.backend.app.llm.groq_client import invoke_json_llm

from src.backend.app.llm.prompts.router_prompts import (
    ROUTER_SYSTEM_PROMPT
)


# =========================================================
# ROUTER NODE
# =========================================================

def router_node(state: AgentState):

    # =====================================================
    # EXTRACT USER INPUT
    # =====================================================

    query = state["user_query"]

    has_image = state.get("image") is not None

    # =====================================================
    # BUILD ROUTING PROMPT
    # =====================================================

    prompt = f"""
{ROUTER_SYSTEM_PROMPT}

=========================================================
USER INPUT
=========================================================

User Query:
{query}

Has Image:
{has_image}
"""

    # =====================================================
    # LLM ROUTING
    # =====================================================

    response = invoke_json_llm(prompt)

    # =====================================================
    # PARSE JSON OUTPUT
    # =====================================================

    try:

        parsed = json.loads(response)

    except Exception:

        # -------------------------------------------------
        # FALLBACK SAFE ROUTING
        # -------------------------------------------------

        parsed = {

            "intent": "general_landmark_query",

            "requires_vision": has_image,

            "requires_weather": False,

            "requires_information": True,

            "requires_nearby_search": False,

            "requires_itinerary": False,

            "requires_comparison": False
        }

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return {

        "intent": parsed.get(
            "intent",
            "general_landmark_query"
        ),

        "requires_vision": parsed.get(
            "requires_vision",
            has_image
        ),

        "requires_weather": parsed.get(
            "requires_weather",
            False
        ),

        "requires_information": parsed.get(
            "requires_information",
            True
        ),

        "requires_nearby_search": parsed.get(
            "requires_nearby_search",
            False
        ),

        "requires_itinerary": parsed.get(
            "requires_itinerary",
            False
        ),

        "requires_comparison": parsed.get(
            "requires_comparison",
            False
        )
    }