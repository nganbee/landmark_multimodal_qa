import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


# ================= GENERATE FINAL ANSWER =================
def generate_answer(prompt: str):
    return llm.invoke(prompt).content


# ================= PLANNER =================
def plan_actions(question: str):
    prompt = f"""
You are an AI planner.

Analyze the user question and decide what actions are needed.

Return JSON ONLY:
{{
  "need_weather": true/false,
  "weather_fields": ["temp","humidity","wind","description","all"],
  "need_info": true/false
}}

Rules:
- If asking about weather → need_weather = true
- If asking general weather → ["all"]
- If asking specific → only that field
- If asking about place → need_info = true

Examples:

Q: What is the weather?
A: {{"need_weather": true, "weather_fields": ["all"], "need_info": false}}

Q: temperature in London?
A: {{"need_weather": true, "weather_fields": ["temp"], "need_info": false}}

Q: Tell me about Big Ben
A: {{"need_weather": false, "weather_fields": [], "need_info": true}}

Q: Tell me about Big Ben and weather
A: {{"need_weather": true, "weather_fields": ["all"], "need_info": true}}

Now:
Q: {question}
A:
"""

    result = llm.invoke(prompt).content

    try:
        return json.loads(result)
    except:
        # fallback
        return {
            "need_weather": False,
            "weather_fields": [],
            "need_info": True
        }