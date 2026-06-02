from src.backend.app.graph.nodes.router_node import (
    router_node
)


state = {

    "user_query":
    "Tell me about this landmark and nearby places.",

    "image": "fake_image"
}


result = router_node(state)

print(result)