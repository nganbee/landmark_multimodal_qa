# backend/main.py
from fastapi import FastAPI, UploadFile, Form, File
from pipeline import Pipeline
import io
from PIL import Image

app = FastAPI()
pipeline = Pipeline()

@app.post("/process")
async def process_request(
    prompt: str = Form(...), 
    image: UploadFile = File(...)
):

    image_data = await image.read()
    img = Image.open(io.BytesIO(image_data))

    result = pipeline.run_image(img, prompt)
    
    return {
        "answer": result["answer"],
        "landmark": result["landmark"],
        "weather": result["weather"],
        "confidence": result["confidence"],
        "sources": ["Wikipedia", "OpenWeather"]
    }