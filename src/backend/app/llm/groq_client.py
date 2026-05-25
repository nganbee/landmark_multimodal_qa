from langchain_groq import ChatGroq

from src.backend.app.config.settings import settings


# =========================================================
# MAIN LLM CLIENT
# =========================================================

llm = ChatGroq(

    model="llama-3.3-70b-versatile",

    api_key=settings.GROQ_API_KEY,

    temperature=0,

    max_tokens=1024
)


# =========================================================
# BASIC TEXT GENERATION
# =========================================================

def invoke_llm(prompt: str) -> str:

    response = llm.invoke(prompt)

    return response.content


# =========================================================
# STRUCTURED JSON GENERATION
# =========================================================

def invoke_json_llm(prompt: str) -> str:

    response = llm.invoke(

        prompt,

        response_format={
            "type": "json_object"
        }
    )

    return response.content