import torch
import time
from PIL import Image
import random #add

from agents.agent import generate_answer, plan_actions
from model.load_model import get_model
from tools.weather_tool import get_current_weather


class Pipeline:
    def __init__(self):
        print("Initializing pipeline...")
        # self.model, self.processor = get_model()
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("MOCK Pipeline initialized - No real models loaded")

    def clean_text(self, text: str):
        if "assistant" in text:
            text = text.split("assistant")[-1]
        return text.strip()

    def detect_landmark(self, image):
        # print(">>> [VISION] Start detect_landmark")
        # t0 = time.time()

        # prompt = "What is this place? Answer short."

        # messages = [
        #     {
        #         "role": "user",
        #         "content": [
        #             {"type": "image", "image": image},
        #             {"type": "text", "text": prompt},
        #         ],
        #     }
        # ]

        # text = self.processor.apply_chat_template(
        #     messages,
        #     tokenize=False,
        #     add_generation_prompt=True,
        # )

        # print(">>> [VISION] Encoding input...")

        # inputs = self.processor(
        #     text=[text],
        #     images=[image],
        #     return_tensors="pt",
        # )

        # inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # print(">>> [VISION] Generating... (THIS IS SLOW)")

        # with torch.no_grad():
        #     outputs = self.model.generate(**inputs, max_new_tokens=50)

        # print(">>> [VISION] Decoding...")

        # result = self.processor.decode(outputs[0], skip_special_tokens=True)

        # print(f">>> [VISION] DONE in {time.time() - t0:.2f}s")

        # return self.clean_text(result)
        
        # Using Mock Data
        landmarks = ["Dinh Độc Lập", "Hồ Gươm", "Đại Nội Huế"]
        selected = random.choice(landmarks)
        print(f">>> [MOCK VISION] Random detect: {selected}")
        return selected

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

        landmark = self.detect_landmark(image)
        print("Landmark:", landmark)
        
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
            "status": "success"
        }