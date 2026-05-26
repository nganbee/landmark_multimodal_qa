import json

from src.backend.app.graph.state import (
    AgentState
)

from src.backend.app.llm.groq_client import (
    invoke_json_llm
)

from src.backend.app.llm.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT
)


# =========================================================
# VALID TOOLS
# =========================================================

VALID_TOOLS = {

    "weather_tool",

    "nearby_places_tool",

    "search_tool"
}


# =========================================================
# PLANNER NODE
# =========================================================

def planner_node(
    state: AgentState
):

    print("\n===================================")
    print(" PLANNER NODE ")
    print("===================================\n")

    # =====================================================
    # USER QUERY
    # =====================================================

    user_query = state.get(
        "user_query",
        ""
    )

    print("\n===== USER QUERY =====\n")

    print(user_query)

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""
{PLANNER_SYSTEM_PROMPT}

=========================================================
USER REQUEST
=========================================================

{user_query}
"""

    # =====================================================
    # LLM CALL
    # =====================================================

    response = invoke_json_llm(
        prompt
    )
    print("\n===== RAW PLANNER RESPONSE =====\n")

    print(response)

    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        parsed = json.loads(
            response
        )

    except Exception:

        print("\n===== JSON PARSE FAILED =====\n")

        parsed = {

            "execution_steps": [],

            "planning_reasoning":
            "Planner parsing failed."
        }

    # =====================================================
    # SAFE EXTRACTION
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
    # VALIDATE TOOLS
    # =====================================================

    validated_steps = []

    for step in execution_steps:

        if step in VALID_TOOLS:

            validated_steps.append(
                step
            )

    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    validated_steps = list(
        dict.fromkeys(
            validated_steps
        )
    )

    print("\n===== VALIDATED STEPS =====\n")

    print(validated_steps)

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "execution_steps":
        validated_steps,

        "planning_reasoning":
        planning_reasoning
    }