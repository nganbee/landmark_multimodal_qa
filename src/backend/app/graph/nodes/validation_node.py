from src.backend.app.graph.state import AgentState


# =========================================================
# VALIDATION NODE
# =========================================================

def validation_node(state: AgentState):

    # =====================================================
    # EXTRACT STATE
    # =====================================================

    landmark_name = state.get(
        "landmark_name",
        "Unknown"
    )

    confidence = state.get(
        "reasoning_confidence",
        0.0
    )

    candidates = state.get(
        "alternative_candidates",
        []
    )

    error = state.get(
        "error",
        ""
    )

    # =====================================================
    # DEFAULT FLAGS
    # =====================================================

    is_valid_landmark = True

    requires_retry = False

    validation_error = ""

    reflection_reason = ""

    # =====================================================
    # API FAILURE
    # =====================================================

    if error:

        is_valid_landmark = False

        requires_retry = True

        validation_error = error

        reflection_reason = (
            "Vision system returned an error."
        )

    # =====================================================
    # OUT OF DOMAIN (PRIVACY & ROBUSTNESS)
    # =====================================================

    elif landmark_name == "OUT_OF_DOMAIN":

        is_valid_landmark = False

        requires_retry = False

        validation_error = (
            "The image does not contain a valid landmark, landscape, or monument. Please provide another image."
        )

        reflection_reason = (
            "Vision model rejected the image due to privacy/out-of-domain policies."
        )

    # =====================================================
    # UNKNOWN LANDMARK
    # =====================================================

    elif landmark_name == "Unknown":

        city = state.get("detected_city", "Unknown")
        
        if city and city != "Unknown":
            # We have a city, even if we don't have a specific landmark.
            is_valid_landmark = True
            requires_retry = False
            validation_error = ""
            reflection_reason = "Landmark unknown, but city detected. Proceeding with city context."
        else:
            is_valid_landmark = False
            requires_retry = True
            validation_error = "Landmark could not be identified."
            reflection_reason = "Vision model failed to identify landmark or city."

    # =====================================================
    # LOW CONFIDENCE
    # =====================================================

    elif confidence < 0.5:

        is_valid_landmark = False

        requires_retry = True

        validation_error = (
            "Low reasoning confidence."
        )

        reflection_reason = (
            "Model confidence too low."
        )

    # =====================================================
    # AMBIGUOUS PREDICTION
    # =====================================================

    elif len(candidates) >= 3:

        is_valid_landmark = False

        requires_retry = True

        validation_error = (
            "Too many possible landmarks."
        )

        reflection_reason = (
            "Prediction ambiguity too high."
        )

    # =====================================================
    # OVERCONFIDENCE DETECTION
    # =====================================================

    elif confidence >= 0.99:

        reflection_reason = (
            "Possible overconfidence detected."
        )

    # =====================================================
    # RETURN STATE UPDATE
    # =====================================================

    return {

        "is_valid_landmark":
        is_valid_landmark,

        "requires_retry":
        requires_retry,

        "validation_error":
        validation_error,

        "reflection_reason":
        reflection_reason
    }