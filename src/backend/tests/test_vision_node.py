from PIL import Image

from src.backend.app.graph.nodes.vision_node import (
    vision_node
)


image = Image.open(
    "test1.jpg"
)


state = {

    "user_query":
    "Identify this landmark.",

    "image": image
}


result = vision_node(state)

print(result)