from src.backend.app.graph.state import AgentState
from src.backend.app.tools.weather_tool import weather_tool

import re
import unicodedata

def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

# =========================================================
# WEATHER NODE
# =========================================================

def weather_node(state: AgentState):
    print("\n===================================")
    print(" WEATHER NODE ")
    print("===================================\n")

    city = state.get("detected_city", "Unknown")

    if city == "Unknown" or not city:
        city = state.get("landmark_name", "Unknown")
        
    # OpenWeatherMap API works better without Vietnamese accents
    city_normalized = remove_accents(city)

    user_query = state.get("user_query", "")
    
    weather_type = "current"
    forecast_days = 0
    forecast_hours = 0
    
    if user_query:
        from src.backend.app.llm.groq_client import invoke_json_llm
        from src.backend.app.llm.prompts.weather_prompts import WEATHER_REASONING_PROMPT
        import json
        
        prompt = f"""
{WEATHER_REASONING_PROMPT}

USER QUERY:
{user_query}
"""
        try:
            response = invoke_json_llm(prompt)
            parsed = json.loads(response)
            weather_type = parsed.get("weather_type", "current")
            forecast_days = parsed.get("forecast_days", 0)
            forecast_hours = parsed.get("forecast_hours", 0)
            
            # API constraint limits
            if forecast_days > 5:
                forecast_days = 5
        except Exception:
            pass

    weather_result = weather_tool.get_weather_by_query(
        city=city_normalized,
        weather_type=weather_type,
        forecast_days=forecast_days,
        forecast_hours=forecast_hours
    )

    tool_results = state.get("tool_results", {})
    if tool_results is None:
        tool_results = {}
        
    tool_results["weather"] = weather_result

    return {
        "tool_results": tool_results
    }
