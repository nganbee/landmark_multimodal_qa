import json
import requests

from io import BytesIO

from PIL import Image

from src.backend.app.config.settings import settings

from src.backend.app.llm.prompts.vision_prompts import (
    VISION_SYSTEM_PROMPT
)


# =========================================================
# VISION CLIENT
# =========================================================

class VisionClient:

    def __init__(self):

        self.base_url = settings.PINGGY_URL

    # =====================================================
    # IMAGE -> STRUCTURED LANDMARK ANALYSIS
    # =====================================================

    def analyze_landmark(
        self,
        image: Image,
        user_query: str = ""
    ):

        # -------------------------------------------------
        # BUILD PROMPT
        # -------------------------------------------------

        prompt = f"""
{VISION_SYSTEM_PROMPT}

=========================================================
USER QUERY
=========================================================

{user_query}
"""

        # -------------------------------------------------
        # CONVERT IMAGE
        # -------------------------------------------------

        buffer = BytesIO()

        image.save(buffer, format="JPEG")

        buffer.seek(0)

        # -------------------------------------------------
        # REMOTE INFERENCE
        # -------------------------------------------------
        try:
            response = requests.post(
                f"{self.base_url}/predict_landmark",
                files={"file": buffer.getvalue()},
                data={"prompt": prompt},
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"[VisionClient Error] Server returned HTTP {response.status_code}: {response.text}")
                return {
                    "landmark_name": "Unknown",
                    "reasoning_confidence": 0.0,
                    "vision_reasoning": "Vision API request failed.",
                    "alternative_candidates": [],
                    "error": f"HTTP {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "landmark_name": "Unknown",
                "reasoning_confidence": 0.0,
                "vision_reasoning": f"Cannot connect to Vision Server (Ngrok might be down). Error: {str(e)}",
                "alternative_candidates": [],
                "error": "VISION_SERVER_UNREACHABLE"
            }

        # -------------------------------------------------
        # PARSE RESPONSE
        # -------------------------------------------------

        try:

            result = response.json()

        except Exception:

            return {

                "landmark_name": "Unknown",

                "reasoning_confidence": 0.0,

                "vision_reasoning":
                "Invalid JSON response from vision model.",

                "alternative_candidates": [],

                "error": "JSON_PARSE_ERROR"
            }

        # -------------------------------------------------
        # SAFE FALLBACKS
        # -------------------------------------------------

        return {

            "landmark_name":
            result.get(
                "landmark_name",
                "Unknown"
            ),

            "city":
            result.get(
                "city",
                "Unknown"
            ),

            "country":
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
            )
        }


# =========================================================
# GLOBAL SINGLETON
# =========================================================

vision_client = VisionClient()