import json

from src.backend.app.graph.state import (
    AgentState
)

from src.backend.app.llm.groq_client import (
    invoke_llm
)

from src.backend.app.llm.prompts.response_prompts import (
    RESPONSE_SYSTEM_PROMPT
)


# =========================================================
# RESPONSE NODE
# =========================================================

def response_node(
    state: AgentState
):

    print("\n===================================")
    print(" RESPONSE NODE ")
    print("===================================\n")

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context = {

        "landmark_name":
        state.get(
            "landmark_name"
        ),

        "city":
        state.get(
            "detected_city"
        ),

        "country":
        state.get(
            "detected_country"
        ),

        "weather_result":
        state.get(
            "weather_result"
        ),

        "nearby_places_result":
        state.get(
            "nearby_places_result"
        ),

        "search_result":
        state.get(
            "search_result"
        )
    }

    print("\n===== RESPONSE CONTEXT =====\n")

    print(context)

    # =====================================================
    # USER QUERY
    # =====================================================

    user_query = state.get(
        "user_query",
        ""
    )

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = f"""
{RESPONSE_SYSTEM_PROMPT}

=========================================================
USER QUERY
=========================================================

{user_query}

=========================================================
AVAILABLE INFORMATION
=========================================================

{json.dumps(context, indent=2)}
"""

    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    final_response = invoke_llm(
        prompt
    )

    print("\n===== FINAL RESPONSE =====\n")

    print(final_response)

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "final_response":
        final_response
    }