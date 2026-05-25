import json

from src.backend.app.graph.state import AgentState

from src.backend.app.llm.groq_client import (
    invoke_json_llm
)

from src.backend.app.llm.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT
)


# =========================================================
# PLANNER NODE
# =========================================================

def planner_node(state: AgentState):

    # =====================================================
    # EXTRACT STATE
    # =====================================================

    query = state.get(
        "user_query",
        ""
    )

    landmark_name = state.get(
        "landmark_name",
        "Unknown"
    )

    city = state.get(
        "detected_city",
        "Unknown"
    )

    country = state.get(
        "detected_country",
        "Unknown"
    )

    confidence = state.get(
        "reasoning_confidence",
        0.0
    )

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""
{PLANNER_SYSTEM_PROMPT}

=========================================================
CURRENT CONTEXT
=========================================================

User Query:
{query}

Detected Landmark:
{landmark_name}

Detected City:
{city}

Detected Country:
{country}

Reasoning Confidence:
{confidence}
"""

    # =====================================================
    # CALL LLM
    # =====================================================

    response = invoke_json_llm(prompt)

    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        parsed = json.loads(response)

    except Exception:

        parsed = {

            "execution_steps": [
                "landmark_information_tool"
            ],

            "planning_reasoning":
            "Fallback planning activated."
        }

    # =====================================================
    # SAFE FALLBACKS
    # =====================================================

    execution_steps = parsed.get(
        "execution_steps",
        []
    )

    planning_reasoning = parsed.get(
        "planning_reasoning",
        ""
    )

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return {

        "execution_steps":
        execution_steps,

        "planning_reasoning":
        planning_reasoning
    }