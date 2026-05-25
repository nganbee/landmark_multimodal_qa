from src.backend.app.graph.state import (
    AgentState
)

from src.backend.app.tools.weather_tool import (
    weather_tool
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
    # EXTRACT EXECUTION PLAN
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

        weather_type = state.get(
            "weather_type",
            "current"
        )

        forecast_days = state.get(
            "forecast_days",
            0
        )

        forecast_hours = state.get(
            "forecast_hours",
            0
        )

        print("\n===== WEATHER INPUT =====\n")

        print({

            "city":
            city,

            "weather_type":
            weather_type,

            "forecast_days":
            forecast_days,

            "forecast_hours":
            forecast_hours
        })

        weather_result = (
            weather_tool.get_weather_by_query(

                city=city,

                weather_type=weather_type,

                forecast_days=forecast_days,

                forecast_hours=forecast_hours
            )
        )

        tool_results[
            "weather_result"
        ] = weather_result

    # =====================================================
    # FINAL TOOL RESULTS
    # =====================================================

    print("\n===== TOOL RESULTS =====\n")

    print(tool_results)

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return tool_results