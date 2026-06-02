from src.backend.app.tools.nearby_places_tool import (
    nearby_places_tool
)


# =========================================================
# TEST
# =========================================================

result = nearby_places_tool.search_places(

    city="Ho Chi Minh City"
)

print("\n===== FINAL RESULT =====\n")

print(result)