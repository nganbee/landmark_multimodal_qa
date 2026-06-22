from src.backend.app.graph.state import AgentState

from src.backend.app.vision.vision_client import (
    vision_client
)


# =========================================================
# VISION NODE
# =========================================================

def vision_node(state: AgentState):

    print("\n===================================")
    print(" VISION NODE ")
    print("===================================\n")
    
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

    print(f"[Vision Node] Calling Vision API on: {vision_client.base_url}/predict_landmark")
    
    result = vision_client.analyze_landmark(

        image=image,

        user_query=query
    )
    
    print(f"[Vision Node] Result from Vision API: {result.get('landmark_name', 'Unknown')} (Error: {result.get('error', 'None')})")

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