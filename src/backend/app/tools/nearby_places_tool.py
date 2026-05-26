from serpapi import GoogleSearch

from src.backend.app.config.settings import (
    settings
)


# =========================================================
# NEARBY PLACES TOOL
# =========================================================

class NearbyPlacesTool:

    def __init__(self):

        self.api_key = (
            settings.SERPAPI_API_KEY
        )

    # =====================================================
    # SEARCH PLACES
    # =====================================================

    def search_places(

        self,

        city: str,

        query_type: str = "tourist attractions",

        limit: int = 5
    ):

        print("\n===================================")
        print(" SERPAPI NEARBY TOOL ")
        print("===================================\n")

        query = f"""
{query_type} in {city}
"""

        print("\n===== SEARCH QUERY =====\n")

        print(query)

        # =================================================
        # SEARCH PARAMS
        # =================================================

        params = {

            "engine":
            "google_maps",

            "q":
            query,

            "type":
            "search",

            "api_key":
            self.api_key
        }

        # =================================================
        # EXECUTE SEARCH
        # =================================================

        search = GoogleSearch(
            params
        )

        results = search.get_dict()

        print("\n===== RAW SERPAPI RESULT =====\n")

        print(results)

        # =================================================
        # EXTRACT LOCAL RESULTS
        # =================================================

        local_results = results.get(
            "local_results",
            []
        )

        places = []

        for item in local_results[:limit]:

            places.append({

                "name":
                item.get(
                    "title"
                ),

                "rating":
                item.get(
                    "rating"
                ),

                "reviews":
                item.get(
                    "reviews"
                ),

                "address":
                item.get(
                    "address"
                ),

                "type":
                item.get(
                    "type"
                ),

                "gps_coordinates":
                item.get(
                    "gps_coordinates",
                    {}
                )
            })

        # =================================================
        # RETURN
        # =================================================

        return {

            "success": True,

            "places":
            places
        }


# =========================================================
# SINGLETON
# =========================================================

nearby_places_tool = (
    NearbyPlacesTool()
)