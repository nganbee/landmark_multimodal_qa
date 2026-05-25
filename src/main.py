from __future__ import annotations

import io
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, UploadFile
from PIL import Image

from src.services.pipeline import Pipeline

pipeline: Pipeline | None = None
pipeline_error: str | None = None


def _maybe_load_pipeline() -> None:
    global pipeline, pipeline_error

    if pipeline is not None or pipeline_error is not None:
        return

    if os.getenv("DISABLE_PIPELINE", "").strip().lower() in {"1", "true", "yes"}:
        pipeline_error = "Pipeline disabled via DISABLE_PIPELINE=1"
        return

    try:
        print("Loading pipeline...")
        pipeline = Pipeline()
        print("Pipeline ready.")
    except Exception as exc:
        pipeline = None
        pipeline_error = f"{type(exc).__name__}: {exc}"


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("AUTO_LOAD_PIPELINE", "").strip().lower() in {"1", "true", "yes"}:
        _maybe_load_pipeline()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/health")
def health():
    return {
        "ok": True,
        "pipeline_loaded": pipeline is not None,
        "pipeline_error": pipeline_error,
    }


@app.post("/ask")
async def ask(
    file: UploadFile = File(...),
    question: str = Form(...),
):
    _maybe_load_pipeline()
    if pipeline is None:
        return {"success": False, "error": "Pipeline not available", "detail": pipeline_error}

    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result = pipeline.run_image(image, question)

    return {"success": True, "result": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)

