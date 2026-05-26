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
        
        # Ensure it's a list
        intents = parsed.get("intents", [])
        if not isinstance(intents, list):
            intents = [intents] if intents else ["general_info"]

    except Exception:

        # -------------------------------------------------
        # FALLBACK SAFE ROUTING
        # -------------------------------------------------

        intents = ["general_info"]

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return {

        "intents": intents
    }