from src.backend.app.graph.state import AgentState
from src.backend.app.tools.search_tool import search_tool

# =========================================================
# WEB SEARCH NODE
# =========================================================

def web_search_node(state: AgentState):
    print("\n===================================")
    print(" WEB SEARCH NODE ")
    print("===================================\n")

    landmark_name = state.get("landmark_name", "Unknown")
    city = state.get("detected_city", "Unknown")
    query = state.get("user_query", "")

    if landmark_name == "Unknown":
        if city != "Unknown" and city != "":
            search_query = f"{city} {query}"
        else:
            search_query = query
    else:
        # For history or general info, we craft a query combining the landmark and user query
        search_query = f"{landmark_name} {query}"

    search_result = search_tool.search(query=search_query)

    tool_results = state.get("tool_results", {})
    if tool_results is None:
        tool_results = {}
        
    tool_results["web_search"] = search_result

    return {
        "tool_results": tool_results
    }
