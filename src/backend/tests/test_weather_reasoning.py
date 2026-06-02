from src.backend.app.graph.nodes.weather_reasoning_node import (
    weather_reasoning_node
)

from src.backend.app.tools.weather_tool import (
    weather_tool
)


# =========================================================
# TEST STATE
# =========================================================

state = {

    "user_query":
    "What will the weather be like for the next 5 days?"
}


# =========================================================
# WEATHER REASONING
# =========================================================

reasoning_result = weather_reasoning_node(
    state
)

print("\n===== WEATHER REASONING =====\n")

print(reasoning_result)


# =========================================================
# WEATHER TOOL EXECUTION
# =========================================================

weather_result = weather_tool.get_weather_by_query(

    city="Ho Chi Minh",

    weather_type=
    reasoning_result["weather_type"],

    forecast_days=
    reasoning_result["forecast_days"],

    forecast_hours=
    reasoning_result["forecast_hours"]
)

print("\n===== WEATHER RESULT =====\n")

print(weather_result)