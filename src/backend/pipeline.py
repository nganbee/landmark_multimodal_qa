import torch
import time
import io
import os
import requests
from PIL import Image
import random #add
from dotenv import load_dotenv

load_dotenv()

from agents.agent import generate_answer, plan_actions
from model.load_model import get_model
from model.vision_model import LandmarkModel
from tools.weather_tool import get_current_weather


class Pipeline:
    def __init__(self):
        print("Initializing pipeline...")
        # self.model, self.processor = get_model()
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("Connect Model to Colab")
        self.pinggy_url = os.getenv("PINGGY_URL")
        self.landmark_model = LandmarkModel(self.pinggy_url)
        
        

    def clean_text(self, text: str):
        if "assistant" in text:
            text = text.split("assistant")[-1]
        return text.strip()

    def detect_landmark(self, image):
        print(">>> [VISION] Start detect_landmark")
        print(f">>> [VISION] Connecting to Remote Model")
        t0 = time.time()

        result = self.landmark_model.predict(image)
        
        raw_text = result.get("landmark", "Outside scope")
        confidence = result.get("confidence", 0.0)
        
        print(f">>> [VISION] DONE in {time.time() - t0:.2f}s")
        
        #prefix = "Based on the visual features, this is "
        #clean_name = raw_text.replace(prefix, "").strip()

        return raw_text, confidence

    def extract_location(self, landmark: str):
        print(">>> [LLM] Extract location...")
        t0 = time.time()

        prompt = f"""
Extract the city or country from this landmark:
{landmark}

Answer only the location name. No explanation.
"""
        location = generate_answer(prompt).strip()

        print(f">>> [LLM] Location extracted in {time.time() - t0:.2f}s")

        if not location:
            return landmark

        return location

    def format_weather(self, data, fields):
        if not data:
            return "N/A"

        if "all" in fields:
            return f"""
Weather in {data['location']}:
- Temperature: {data['temp']}°C
- Feels like: {data['feels_like']}°C
- Humidity: {data['humidity']}%
- Condition: {data['description']}
- Wind: {data['wind_speed']} m/s
"""

        result = []

        if "temp" in fields:
            result.append(f"Temperature: {data['temp']}°C")

        if "humidity" in fields:
            result.append(f"Humidity: {data['humidity']}%")

        if "wind" in fields:
            result.append(f"Wind: {data['wind_speed']} m/s")

        if "description" in fields:
            result.append(f"Condition: {data['description']}")

        return "\n".join(result)

    def run(self, image_path: str, question: str):
        print("\n=== STEP 1: Vision ===")
        image = Image.open(image_path).convert("RGB")
        return self.run_image(image, question)

    def run_image(self, image, question: str):
        print(">>> RUN IMAGE START")

        landmark, score = self.detect_landmark(image)
        print("Landmark:", landmark)
        
        if "Outside scope" in landmark or landmark == "Unknown":
            return {
                "answer": "Sorry this landmark is outside of my knowledge.",
                "landmark": "Unknown",
                "weather": "N/A",
                "confidence": score,
                "status": "success"
            }
        
        weather_text = "None"

        print("\n=== STEP 2: Planning ===")
        plan = plan_actions(question)
        print("Plan:", plan)

        if plan.get("need_weather"):
            print(">>> [TOOL] Calling weather")

            location = self.extract_location(landmark)
            print("Location:", location)

            t0 = time.time()
            try:
                weather_data = get_current_weather.invoke({"location_name": location})
                weather_text = self.format_weather(weather_data, plan.get("weather_fields", []))
            except Exception as e:
                print(f"Error from calling Weather API: {e}")
                # weather_text = "Không thể lấy dữ liệu thời tiết lúc này."
                
            print(f">>> [TOOL] Weather done in {time.time() - t0:.2f}s")

        # weather_text = self.format_weather(
        #     weather_data,
        #     plan.get("weather_fields", [])
        # )

        print("\n=== STEP 3: Generate ===")
        print(">>> [LLM] Generating final answer...")

        t0 = time.time()

        prompt = f"""
Landmark: {landmark}
Weather: {weather_text}
Question: {question}
"""

        answer = generate_answer(prompt)

        print(f">>> [LLM] DONE in {time.time() - t0:.2f}s")

        print("\n=== FINAL ===")
        print(answer)

        return {
            "answer": answer,
            "landmark": landmark,
            "weather": weather_text,
            "confidence" : score,
            "status": "success"
        }