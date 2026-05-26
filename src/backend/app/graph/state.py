from typing import TypedDict, Optional, Dict, Any, List, Annotated
from PIL.Image import Image

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    if a is None:
        a = {}
    if b is None:
        b = {}
    return {**a, **b}

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
    # VISION NODE
    # =====================================================
    landmark_name: str
    detected_city: str
    detected_country: str
    reasoning_confidence: float
    vision_reasoning: str
    alternative_candidates: List[str]

    # =====================================================
    # VALIDATION NODE
    # =====================================================
    is_valid_landmark: bool
    validation_error: str
    requires_retry: bool
    reflection_reason: str

    # =====================================================
    # ROUTER NODE
    # =====================================================
    intents: List[str] # ['weather', 'history', 'general_info', 'unrelated']

    # =====================================================
    # TOOL RESULTS
    # =====================================================
    tool_results: Annotated[Dict[str, Any], merge_dicts]

    # =====================================================
    # FINAL RESPONSE
    # =====================================================
    final_answer: str

    # =====================================================
    # GLOBAL ERROR
    # =====================================================
    error: str