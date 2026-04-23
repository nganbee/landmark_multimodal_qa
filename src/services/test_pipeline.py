import os
from src.services.pipeline import Pipeline

BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "test", "bigben.jpg")


def run_test(pipeline, question):
    print("\n" + "=" * 80)
    print("❓ QUESTION:", question)
    print("=" * 80)

    try:
        result = pipeline.run(IMAGE_PATH, question)
        print("\n✅ RESULT:", result)
    except Exception as e:
        print("\n❌ ERROR:", str(e))


if __name__ == "__main__":

    print("🔥 ROBUST TEST PIPELINE 🔥")

    pipeline = Pipeline()

    # # ================= NORMAL =================
    # run_test(pipeline, "What is this place?")
    # run_test(pipeline, "Tell me about this place.")

    # ================= WEATHER BASIC =================
    run_test(pipeline, "What is the weather there?")
    run_test(pipeline, "How is the weather?")
    run_test(pipeline, "Is it hot there?")

    # ================= TYPO =================
    run_test(pipeline, "What is the temperatureeeeeee there?")
    run_test(pipeline, "temprature there??")
    run_test(pipeline, "nhiet do o do?")
    run_test(pipeline, "troi hom nay sao vay")

    # ================= SPECIFIC FIELD =================
    run_test(pipeline, "humidity there?")
    run_test(pipeline, "wind speed?")
    run_test(pipeline, "how windy is it?")

    # ================= MULTI =================
    run_test(pipeline, "Tell me about this place and weather")
    run_test(pipeline, "Info + temperature pls")

    # ================= RANDOM / VAGUE =================
    run_test(pipeline, "what's going on there?")
    run_test(pipeline, "is it nice?")
    run_test(pipeline, "should I go there now?")
    run_test(pipeline, "is it a good time to visit?")

    # ================= CHAOTIC USER =================
    run_test(pipeline, "uhh idk like weather maybe???")
    run_test(pipeline, "bro what’s the vibe there")
    run_test(pipeline, "tell me everything lol")

    print("\n🎯 ALL TESTS DONE")