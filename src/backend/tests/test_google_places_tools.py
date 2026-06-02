from src.backend.app.tools.nearby_places_tool import (
    nearby_places_tool
)

from src.backend.app.tools.place_details_tool import (
    place_details_tool
)

from src.backend.app.tools.directions_tool import (
    directions_tool
)


# =========================================================
# NEARBY SEARCH
# =========================================================

nearby_result = nearby_places_tool.search_places(

    city="Ho Chi Minh City"
)

print("\n===== NEARBY RESULT =====\n")

print(nearby_result)


# =========================================================
# PLACE DETAILS
# =========================================================

first_place = nearby_result[
    "places"
][0]

place_id = first_place[
    "place_id"
]

details_result = (
    place_details_tool.get_place_details(
        place_id
    )
)

print("\n===== DETAILS RESULT =====\n")

print(details_result)


# =========================================================
# DIRECTIONS
# =========================================================

route_result = (
    directions_tool.get_directions(

        origin="Ben Thanh Market",

        destination=
        "Saigon Central Post Office"
    )
)

print("\n===== DIRECTIONS RESULT =====\n")

print(route_result)