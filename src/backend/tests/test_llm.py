from src.backend.app.llm.groq_client import invoke_llm


response = invoke_llm(

    "What is the capital of Vietnam?"

)

print(response)