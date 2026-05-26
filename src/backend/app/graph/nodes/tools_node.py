from src.backend.app.graph.state import (
    AgentState
)

from src.backend.app.tools.weather_tool import (
    weather_tool
)

from src.backend.app.tools.nearby_places_tool import (
    nearby_places_tool
)

from src.backend.app.tools.search_tool import (
    search_tool
)


# =========================================================
# TOOLS NODE
# =========================================================

def tools_node(
    state: AgentState
):

    print("\n===================================")
    print(" TOOLS NODE ")
    print("===================================\n")

    # =====================================================
    # EXECUTION STEPS
    # =====================================================

    execution_steps = state.get(
        "execution_steps",
        []
    )

    print("\n===== EXECUTION STEPS =====\n")

    print(execution_steps)

    # =====================================================
    # TOOL RESULTS
    # =====================================================

    tool_results = {}

    # =====================================================
    # WEATHER TOOL
    # =====================================================

    if "weather_tool" in execution_steps:

        print("\n===== EXECUTING WEATHER TOOL =====\n")

        city = state.get(
            "detected_city",
            "Unknown"
        )

        weather_result = (
    weather_tool.get_weather_by_query(

        city=city,

        weather_type=state.get(
            "weather_type",
            "current"
        ),

        forecast_days=state.get(
            "forecast_days",
            0
        ),

        forecast_hours=state.get(
            "forecast_hours",
            0
        )
    )
)

        tool_results[
            "weather_result"
        ] = weather_result

    # =====================================================
    # NEARBY PLACES TOOL
    # =====================================================

    if "nearby_places_tool" in execution_steps:

        print("\n===== EXECUTING NEARBY TOOL =====\n")

        city = state.get(
            "detected_city",
            "Unknown"
        )

        nearby_result = (
            nearby_places_tool.search_places(

                city=city
            )
        )

        tool_results[
            "nearby_places_result"
        ] = nearby_result

    # =====================================================
    # SEARCH TOOL
    # =====================================================

    if "search_tool" in execution_steps:

        print("\n===== EXECUTING SEARCH TOOL =====\n")

        landmark_name = state.get(
            "landmark_name",
            "Unknown Landmark"
        )

        query = f"""
history and cultural significance of
{landmark_name}
"""

        search_result = (
            search_tool.search(
                query=query
            )
        )

        tool_results[
            "search_result"
        ] = search_result

    # =====================================================
    # FINAL RESULTS
    # =====================================================

    print("\n===== FINAL TOOL RESULTS =====\n")

    print(tool_results)

    # =====================================================
    # RETURN
    # =====================================================

    return tool_results