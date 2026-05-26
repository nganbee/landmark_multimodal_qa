from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from PIL import Image

import io

from src.backend.app.graph.workflow import (
    run_agent_workflow
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(

    title="Multimodal Travel Agent API"
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def health_check():

    return {

        "status": "running",

        "message":
        "Multimodal Travel Agent API is active."
    }


# =========================================================
# MAIN PROCESS ENDPOINT
# =========================================================

@app.post("/process")
async def process_request(

    prompt: str = Form(...),

    image: UploadFile | None = File(None)
):

    print("\n===================================")
    print(" NEW REQUEST ")
    print("===================================\n")

    print("\n===== USER PROMPT =====\n")

    print(prompt)

    # =====================================================
    # IMAGE HANDLING
    # =====================================================

    pil_image = None

    try:

        if image is not None:

            print("\n===== IMAGE RECEIVED =====\n")

            print(image.filename)

            image_bytes = await image.read()

            pil_image = Image.open(

                io.BytesIO(image_bytes)

            ).convert("RGB")

    except Exception as e:

        print("\n===== IMAGE ERROR =====\n")

        print(str(e))

        pil_image = None

    # =====================================================
    # INITIAL STATE
    # =====================================================

    state = {

        "user_query":
        prompt,

        "image":
        pil_image
    }

    print("\n===== INITIAL STATE =====\n")

    print(state)

    # =====================================================
    # RUN AGENT WORKFLOW
    # =====================================================

    try:

        result = run_agent_workflow(
            state
        )

    except Exception as e:

        print("\n===== WORKFLOW ERROR =====\n")

        print(str(e))

        return {

            "success": False,

            "error":
            str(e)
        }

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    response = {

        "success": True,

        "answer":
        result.get(
            "final_answer",
            "No response generated."
        ),

        "landmark":
        result.get(
            "landmark_name",
            "Unknown"
        ),

        "city":
        result.get(
            "detected_city",
            "Unknown"
        ),

        "country":
        result.get(
            "detected_country",
            "Unknown"
        ),

        "confidence":
        result.get(
            "reasoning_confidence",
            0.0
        ),

        "weather":
        result.get(
            "weather_result",
            {}
        ),

        "nearby_places":
        result.get(
            "nearby_places_result",
            {}
        )
    }

    print("\n===== FINAL API RESPONSE =====\n")

    print(response)

    return response