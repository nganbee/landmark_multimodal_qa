from PIL import Image

from src.backend.app.graph.nodes.vision_node import (
    vision_node
)

from src.backend.app.graph.nodes.validation_node import (
    validation_node
)


# =========================================================
# LOAD IMAGE
# =========================================================

image = Image.open(
    "test1.jpg"
)


# =========================================================
# INITIAL STATE
# =========================================================

state = {

    "user_query":
    "Identify this landmark.",

    "image": image
}


# =========================================================
# RUN VISION NODE
# =========================================================

vision_result = vision_node(state)

print("\n===== VISION RESULT =====\n")

print(vision_result)


# =========================================================
# MERGE STATE
# =========================================================

state.update(vision_result)


# =========================================================
# RUN VALIDATION NODE
# =========================================================

validation_result = validation_node(state)

print("\n===== VALIDATION RESULT =====\n")

print(validation_result)