from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    BackgroundTasks
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from PIL import Image

import io

from src.backend.app.graph.workflow import (
    run_agent_workflow
)

from contextlib import asynccontextmanager
import time
import uuid
from src.backend.app.config.db import init_db, log_request, log_feedback, get_dashboard_metrics, get_recent_logs
from src.backend.app.image_utils import preprocess_image
from pydantic import BaseModel

# =========================================================
# FASTAPI APP
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Multimodal Travel Agent API",
    lifespan=lifespan
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
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),

    image: UploadFile | None = File(None)
):

    start_time = time.time()
    req_id = str(uuid.uuid4())

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
            
            # Apply padding and resizing optimizations
            pil_image = preprocess_image(pil_image)

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
        
        latency_ms = (time.time() - start_time) * 1000
        background_tasks.add_task(log_request, req_id, "/process", latency_ms, "Unknown", 0.0, False)

        return {

            "success": False,
            "request_id": req_id,

            "error":
            str(e)
        }

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    response = {

        "success": True,
        
        "request_id": req_id,

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
    
    latency_ms = (time.time() - start_time) * 1000
    background_tasks.add_task(log_request, req_id, "/process", latency_ms, response["landmark"], response["confidence"], True)

    return response

# =========================================================
# ADMIN DASHBOARD ENDPOINTS
# =========================================================

@app.get("/admin/metrics")
def get_metrics():
    """Returns aggregated metrics for the dashboard."""
    return get_dashboard_metrics()

@app.get("/admin/logs")
def get_logs(limit: int = 50):
    """Returns recent requests logs."""
    return get_recent_logs(limit)

class FeedbackRequest(BaseModel):
    request_id: str
    is_correct: bool
    actual_landmark: str | None = None

@app.post("/admin/feedback")
def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for a specific request."""
    return log_feedback(feedback.request_id, feedback.is_correct, feedback.actual_landmark)