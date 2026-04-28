import os
from dotenv import load_dotenv

from src.agents.agent import agent_executor

from langchain_groq import ChatGroq

load_dotenv()


# ================= RAW LLM =================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


def run_agent(query: str):
    try:
        result = agent_executor.invoke({
            "input": query
        })
        return result["output"]
    except Exception as e:
        return f"ERROR: {str(e)}"


def run_llm(query: str):
    try:
        response = llm.invoke(query)
        return response.content
    except Exception as e:
        return f"ERROR: {str(e)}"


def run_compare(name: str, query: str):
    print("\n" + "=" * 80)
    print(f"🧪 TEST: {name}")
    print("=" * 80)

    print(f"\n📥 INPUT:\n{query}")

    # ================= AGENT =================
    print("\n🤖 AGENT (with tools):")
    agent_output = run_agent(query)
    print(agent_output)

    # ================= RAW LLM =================
    print("\n🧠 RAW LLM (no tools):")
    llm_output = run_llm(query)
    print(llm_output)

    print("\n" + "-" * 80)
    print("🔍 INSIGHT:")
    print("- Agent: uses REAL data (API)")
    print("- LLM: guesses (may hallucinate)")
    print("-" * 80)


if __name__ == "__main__":

    print("\n🔥 STARTING AGENT vs LLM COMPARISON 🔥")

    # ================= TEST 1 =================
    run_compare(
        "Weather Hanoi",
        "What is the weather in Hanoi?"
    )

    # ================= TEST 2 =================
    run_compare(
        "Weather Big Ben",
        "What is the weather at Big Ben?"
    )

    # ================= TEST 3 =================
    run_compare(
        "Weather Tokyo",
        "Tell me the weather in Tokyo right now."
    )

    # ================= TEST 4 =================
    run_compare(
        "Info + weather",
        "Tell me about the Eiffel Tower and the weather there."
    )

    # ================= TEST 5 =================
    run_compare(
        "Invalid location",
        "What is the weather in asdasdasd?"
    )

    print("\n🎯 DONE COMPARISON")