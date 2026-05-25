from src.backend.app.graph.state import AgentState

from src.backend.app.vision.vision_client import (
    vision_client
)


# =========================================================
# VISION NODE
# =========================================================

def vision_node(state: AgentState):

    # =====================================================
    # EXTRACT STATE
    # =====================================================

    image = state.get("image")

    query = state.get(
        "user_query",
        ""
    )

    # =====================================================
    # NO IMAGE SAFETY
    # =====================================================

    if image is None:

        return {

            "landmark_name": "Unknown",

            "reasoning_confidence": 0.0,

            "vision_reasoning":
            "No image provided.",

            "alternative_candidates": [],

            "error":
            "VISION_NODE_NO_IMAGE"
        }

    # =====================================================
    # RUN VISION ANALYSIS
    # =====================================================

    result = vision_client.analyze_landmark(

        image=image,

        user_query=query
    )

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return {

        "landmark_name":
        result.get(
            "landmark_name",
            "Unknown"
        ),

        "detected_city":
        result.get(
            "city",
            "Unknown"
        ),

        "detected_country":
        result.get(
            "country",
            "Unknown"
        ),

        "architectural_style":
        result.get(
            "architectural_style",
            "Unknown"
        ),

        "cultural_significance":
        result.get(
            "cultural_significance",
            "Unknown"
        ),

        "reasoning_confidence":
        result.get(
            "reasoning_confidence",
            0.0
        ),

        "vision_reasoning":
        result.get(
            "vision_reasoning",
            "No reasoning provided."
        ),

        "alternative_candidates":
        result.get(
            "alternative_candidates",
            []
        ),

        "error":
        result.get(
            "error",
            ""
        )
    }