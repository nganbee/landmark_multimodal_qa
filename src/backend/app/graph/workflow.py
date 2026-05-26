from langgraph.graph import StateGraph, END
from src.backend.app.graph.state import AgentState

from src.backend.app.graph.nodes.router_node import router_node
from src.backend.app.graph.nodes.vision_node import vision_node
from src.backend.app.graph.nodes.validation_node import validation_node
from src.backend.app.graph.nodes.weather_node import weather_node
from src.backend.app.graph.nodes.web_search_node import web_search_node
from src.backend.app.graph.nodes.nearby_places_node import nearby_places_node
from src.backend.app.graph.nodes.itinerary_node import itinerary_node
from src.backend.app.graph.nodes.response_node import response_node

# =========================================================
# CONDITIONAL ROUTING FUNCTIONS
# =========================================================

def route_from_validation(state: AgentState):
    """
    Decides where to go after validation.
    If image is invalid or has error -> skip directly to draft/response node.
    If valid -> go to router node.
    """
    is_valid = state.get("is_valid_landmark", True)
    if not is_valid:
        return "draft_node"
    return "router_node"

def route_from_intent(state: AgentState):
    """
    Routes to specialized tools based on multiple intents (parallel execution).
    """
    intents = state.get("intents", ["general_info"])
    
    destinations = []
    
    if "weather" in intents:
        destinations.append("weather_node")
    if "history" in intents or "general_info" in intents:
        destinations.append("web_search_node")
    if "nearby_places" in intents:
        destinations.append("nearby_places_node")
    if "itinerary" in intents:
        destinations.append("itinerary_node")
        
    # If unrelated or no tools matched, go straight to draft
    if "unrelated" in intents or not destinations:
        return ["draft_node"]
        
    # Return unique destinations to prevent running the same node twice
    return list(set(destinations))

# =========================================================
# MAIN AGENT WORKFLOW
# =========================================================

def build_workflow():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("vision_node", vision_node)
    workflow.add_node("validation_node", validation_node)
    workflow.add_node("router_node", router_node)
    
    workflow.add_node("weather_node", weather_node)
    workflow.add_node("web_search_node", web_search_node)
    workflow.add_node("nearby_places_node", nearby_places_node)
    workflow.add_node("itinerary_node", itinerary_node)
    
    workflow.add_node("draft_node", response_node)

    # Set Entry Point
    # If there's an image, we start at vision.
    # Otherwise, maybe we can skip vision? 
    # For now, let's just make vision_node handle the 'no image' case safely as it does already.
    workflow.set_entry_point("vision_node")

    # Edges
    workflow.add_edge("vision_node", "validation_node")
    
    # Conditional edge from validation
    workflow.add_conditional_edges(
        "validation_node",
        route_from_validation,
        {
            "router_node": "router_node",
            "draft_node": "draft_node"
        }
    )
    
    # Conditional edge from router
    workflow.add_conditional_edges(
        "router_node",
        route_from_intent,
        {
            "weather_node": "weather_node",
            "web_search_node": "web_search_node",
            "nearby_places_node": "nearby_places_node",
            "itinerary_node": "itinerary_node",
            "draft_node": "draft_node"
        }
    )

    # All tools converge to draft node
    workflow.add_edge("weather_node", "draft_node")
    workflow.add_edge("web_search_node", "draft_node")
    workflow.add_edge("nearby_places_node", "draft_node")
    workflow.add_edge("itinerary_node", "draft_node")

    # Draft node finishes the graph
    workflow.add_edge("draft_node", END)

    return workflow.compile()

# Instantiate the compiled graph so it can be called.
# You can use app.invoke(state)
compiled_workflow = build_workflow()

def run_agent_workflow(state: AgentState):
    print("\n===================================")
    print(" STARTING AGENT WORKFLOW (LANGGRAPH) ")
    print("===================================\n")
    
    # Pass the initial state to the compiled graph
    final_state = compiled_workflow.invoke(state)
    return final_state