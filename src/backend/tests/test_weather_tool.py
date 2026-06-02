from PIL import Image

from src.backend.app.graph.nodes.vision_node import (
    vision_node
)

from src.backend.app.tools.weather_tool import (
    weather_tool
)


# =========================================================
# LOAD TEST IMAGE
# =========================================================

image = Image.open(
    "test.jpg"
)


# =========================================================
# INITIAL STATE
# =========================================================

state = {

    "user_query":
    "What is the weather there today?",

    "image": image
}


print("\n===================================")
print(" INITIAL STATE ")
print("===================================\n")

print(state)


# =========================================================
# RUN VISION NODE
# =========================================================

vision_result = vision_node(state)

print("\n===================================")
print(" VISION NODE RESULT ")
print("===================================\n")

print(vision_result)


# =========================================================
# UPDATE STATE
# =========================================================

state.update(vision_result)


print("\n===================================")
print(" UPDATED STATE ")
print("===================================\n")

print(state)


# =========================================================
# EXTRACT CITY
# =========================================================

city = state.get(
    "detected_city",
    "Unknown"
)

print("\n===================================")
print(" EXTRACTED CITY ")
print("===================================\n")

print(city)


# =========================================================
# CALL WEATHER TOOL
# =========================================================

weather_result = weather_tool.get_weather(

    city=city,

    verbose=True
)


print("\n===================================")
print(" FINAL WEATHER RESULT ")
print("===================================\n")

print(weather_result)