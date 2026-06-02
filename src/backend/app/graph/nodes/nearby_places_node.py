from src.backend.app.graph.state import AgentState
from src.backend.app.tools.nearby_places_tool import nearby_places_tool
from src.backend.app.llm.groq_client import invoke_json_llm
from src.backend.app.llm.prompts.nearby_places_prompts import NEARBY_PLACES_PROMPT
import json
import unicodedata

def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

# =========================================================
# NEARBY PLACES NODE
# =========================================================

def nearby_places_node(state: AgentState):
    print("\n===================================")
    print(" NEARBY PLACES NODE ")
    print("===================================\n")

    user_query = state.get("user_query", "")
    city = state.get("detected_city", "Unknown")
    landmark_name = state.get("landmark_name", "Unknown")

    if city == "Unknown" or not city:
        location_query = landmark_name
    else:
        location_query = f"{landmark_name}, {city}"
        
    location_normalized = remove_accents(location_query)

    # Use LLM to determine exact query type
    prompt = f"""
{NEARBY_PLACES_PROMPT}

USER QUERY:
{user_query}
"""
    try:
        response = invoke_json_llm(prompt)
        parsed = json.loads(response)
        query_type = parsed.get("query_type", "tourist attractions")
    except Exception:
        query_type = "tourist attractions"

    nearby_result = nearby_places_tool.search_places(
        location_query=location_normalized,
        query_type=query_type,
        limit=5
    )

    tool_results = state.get("tool_results", {})
    if tool_results is None:
        tool_results = {}
        
    tool_results["nearby_places_result"] = nearby_result

    return {
        "tool_results": tool_results
    }
