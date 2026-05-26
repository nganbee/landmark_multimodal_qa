from src.backend.app.graph.state import AgentState
from src.backend.app.llm.groq_client import invoke_json_llm
from src.backend.app.llm.prompts.itinerary_prompts import ITINERARY_PROMPT
from src.backend.app.tools.nearby_places_tool import nearby_places_tool
import json
import unicodedata

def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

# =========================================================
# ITINERARY NODE
# =========================================================

def itinerary_node(state: AgentState):
    print("\n===================================")
    print(" ITINERARY PLANNER NODE ")
    print("===================================\n")

    user_query = state.get("user_query", "")
    city = state.get("detected_city", "Unknown")
    landmark_name = state.get("landmark_name", "Unknown")

    if city == "Unknown" or not city:
        location_query = landmark_name
    else:
        location_query = f"{landmark_name}, {city}"
        
    location_normalized = remove_accents(location_query)

    # Extract constraints
    prompt = f"""
{ITINERARY_PROMPT}

USER QUERY:
{user_query}
"""
    budget = "Unknown"
    duration_days = 1
    
    try:
        response = invoke_json_llm(prompt)
        parsed = json.loads(response)
        budget = parsed.get("budget", "Unknown")
        duration_days = parsed.get("duration_days", 1)
    except Exception:
        pass

    # Fetch places to prevent hallucination
    # Get 10 attractions, 10 restaurants, and 3 hotels
    attractions = nearby_places_tool.search_places(
        location_query=location_normalized,
        query_type="tourist attractions",
        limit=10
    )
    
    restaurants = nearby_places_tool.search_places(
        location_query=location_normalized,
        query_type="restaurants",
        limit=10
    )
    
    hotels = nearby_places_tool.search_places(
        location_query=location_normalized,
        query_type="hotels",
        limit=3
    )

    tool_results = state.get("tool_results", {})
    if tool_results is None:
        tool_results = {}
        
    tool_results["itinerary_constraints"] = {
        "budget": budget,
        "duration_days": duration_days
    }
    
    tool_results["itinerary_places"] = {
        "attractions": attractions,
        "restaurants": restaurants,
        "hotels": hotels
    }

    return {
        "tool_results": tool_results
    }
