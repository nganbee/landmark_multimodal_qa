from src.agents.agent import agent_executor


def run_test(name: str, query: str):
    print("\n" + "=" * 70)
    print(f"🧪 TEST: {name}")
    print("=" * 70)
    print(f"INPUT: {query}\n")

    try:
        result = agent_executor.invoke({
            "input": query
        })

        print("\n✅ OUTPUT:")
        print(result["output"])

        # 🔥 Debug nâng cao
        if "intermediate_steps" in result:
            print("\n🔍 INTERMEDIATE STEPS:")
            for step in result["intermediate_steps"]:
                print(step)

    except Exception as e:
        print("\n❌ ERROR:")
        print(str(e))


if __name__ == "__main__":

    print("\n🔥 STARTING FULL AGENT TEST SUITE 🔥")

    # ================= BASIC =================
    run_test(
        "Normal question",
        "Tell me about Paris."
    )

    # ================= WEATHER =================
    run_test(
        "Weather direct",
        "What is the weather in Hanoi?"
    )

    # ================= LANDMARK =================
    run_test(
        "Landmark only",
        "Tell me about Big Ben."
    )

    # ================= LANDMARK + WEATHER =================
    run_test(
        "Landmark + weather",
        "What is the weather at Big Ben?"
    )

    # ================= MULTI TASK =================
    run_test(
        "Info + weather",
        "Tell me about the Eiffel Tower and the weather there."
    )

    # ================= FORCE TOOL =================
    run_test(
        "Force tool usage",
        "Use the weather tool to tell me the weather in Tokyo."
    )

    # ================= EDGE CASE =================
    run_test(
        "Ambiguous question",
        "What's it like there?"
    )

    # ================= INVALID LOCATION =================
    run_test(
        "Invalid location",
        "What is the weather in asdasdasd?"
    )

    # ================= MULTI LOCATION =================
    run_test(
        "Compare weather",
        "Compare the weather in Hanoi and Tokyo."
    )

    # ================= LONG QUERY =================
    run_test(
        "Complex reasoning",
        "I see Big Ben in the image. Can you tell me about it and also the weather there now?"
    )

    print("\n🎯 ALL TESTS COMPLETED")