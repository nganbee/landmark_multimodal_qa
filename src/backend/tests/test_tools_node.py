from src.backend.app.graph.nodes.tools_node import (
    tools_node
)


state = {

    "execution_steps": [

        "weather_tool",

        "nearby_places_tool",

        "search_tool"
    ],

    "detected_city":
    "Ho Chi Minh City",

    "landmark_name":
    "Ben Thanh Market",

    "weather_type":
    "daily",

    "forecast_days":
    3,

    "forecast_hours":
    0
}


result = tools_node(
    state
)

print("\n===== FINAL RESULT =====\n")

print(result)