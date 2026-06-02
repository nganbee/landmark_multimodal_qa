from src.backend.app.graph.nodes.planner_node import (
    planner_node
)


state = {

    "user_query":
    """
Can you recommend nearby attractions
and tell me the weather there?
"""
}


result = planner_node(
    state
)

print("\n===== PLANNER RESULT =====\n")

print(result)