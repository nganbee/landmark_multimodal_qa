from typing import TypedDict, Optional, Dict, Any, List
from PIL.Image import Image


# =========================================================
# TOOL RESULT TYPE
# =========================================================

class ToolResult(TypedDict, total=False):

    success: bool

    data: Dict[str, Any]

    error: str


# =========================================================
# MAIN AGENT STATE
# =========================================================

class AgentState(TypedDict, total=False):

    # =====================================================
    # USER INPUT
    # =====================================================

    user_query: str

    image: Optional[Image]

    # =====================================================
    # ROUTER NODE
    # =====================================================

    intent: str

    requires_vision: bool

    requires_weather: bool

    requires_information: bool

    requires_comparison: bool

    # =====================================================
    # VISION NODE
    # =====================================================

    landmark_name: str

    confidence: float

    detected_city: str

    detected_country: str

    alternative_candidates: List[str]

    # =====================================================
    # VALIDATION NODE
    # =====================================================

    is_valid_landmark: bool

    validation_error: str

    # =====================================================
    # PLANNER NODE
    # =====================================================

    execution_plan: List[str]

    # Example:
    #
    # [
    #   "get_weather",
    #   "get_landmark_info"
    # ]

    # =====================================================
    # TOOL EXECUTION NODE
    # =====================================================

    tool_results: Dict[str, ToolResult]

    # Example:
    #
    # {
    #     "weather": {
    #         "success": True,
    #         "data": {...}
    #     }
    # }

    # =====================================================
    # REFLECTION NODE
    # =====================================================

    requires_retry: bool

    retry_count: int

    reflection_reason: str

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    final_answer: str

    response_sources: List[str]

    # =====================================================
    # GLOBAL ERROR
    # =====================================================

    error: str