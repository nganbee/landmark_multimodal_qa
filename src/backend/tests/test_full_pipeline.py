from PIL import Image

from src.backend.app.graph.nodes.router_node import (
    router_node
)

from src.backend.app.graph.nodes.vision_node import (
    vision_node
)

from src.backend.app.graph.nodes.validation_node import (
    validation_node
)

from src.backend.app.graph.nodes.planner_node import (
    planner_node
)

from src.backend.app.graph.nodes.weather_reasoning_node import (
    weather_reasoning_node
)

from src.backend.app.graph.nodes.tools_node import (
    tools_node
)

from src.backend.app.graph.nodes.response_node import (
    response_node
)


# =========================================================
# LOAD IMAGE
# =========================================================

image = Image.open(

    "test.jpg"
)

# =========================================================
# INITIAL STATE
# =========================================================

state = {

    "user_query":
    """
What should I visit nearby
and what will the weather be like
for the next 3 days?
""",

    "image":
    image
}

print("\n===================================")
print(" INITIAL STATE ")
print("===================================\n")

print(state)

# =========================================================
# ROUTER NODE
# =========================================================

router_result = router_node(
    state
)

state.update(
    router_result
)

print("\n===================================")
print(" ROUTER RESULT ")
print("===================================\n")

print(router_result)

# =========================================================
# VISION NODE
# =========================================================

vision_result = vision_node(
    state
)

state.update(
    vision_result
)

print("\n===================================")
print(" VISION RESULT ")
print("===================================\n")

print(vision_result)

# =========================================================
# VALIDATION NODE
# =========================================================

validation_result = validation_node(
    state
)

state.update(
    validation_result
)

print("\n===================================")
print(" VALIDATION RESULT ")
print("===================================\n")

print(validation_result)

# =========================================================
# PLANNER NODE
# =========================================================

planner_result = planner_node(
    state
)

state.update(
    planner_result
)

print("\n===================================")
print(" PLANNER RESULT ")
print("===================================\n")

print(planner_result)

# =========================================================
# WEATHER REASONING NODE
# =========================================================

weather_reasoning_result = (
    weather_reasoning_node(
        state
    )
)

state.update(
    weather_reasoning_result
)

print("\n===================================")
print(" WEATHER REASONING RESULT ")
print("===================================\n")

print(weather_reasoning_result)

# =========================================================
# TOOLS NODE
# =========================================================

tools_result = tools_node(
    state
)

state.update(
    tools_result
)

print("\n===================================")
print(" TOOLS RESULT ")
print("===================================\n")

print(tools_result)

# =========================================================
# RESPONSE NODE
# =========================================================

response_result = response_node(
    state
)

state.update(
    response_result
)

print("\n===================================")
print(" FINAL RESPONSE ")
print("===================================\n")

print(

    state[
        "final_response"
    ]
)