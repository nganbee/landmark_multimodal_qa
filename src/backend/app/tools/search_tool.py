from serpapi import GoogleSearch

from src.backend.app.config.settings import (
    settings
)


# =========================================================
# SEARCH TOOL
# =========================================================

class SearchTool:

    def __init__(self):

        self.api_key = (
            settings.SERPAPI_API_KEY
        )

    # =====================================================
    # SEARCH WEB
    # =====================================================

    def search(

        self,

        query: str
    ):

        print("\n===================================")
        print(" SEARCH TOOL ")
        print("===================================\n")

        print("\n===== QUERY =====\n")

        print(query)

        params = {

            "engine":
            "google",

            "q":
            query,

            "api_key":
            self.api_key
        }

        search = GoogleSearch(
            params
        )

        results = search.get_dict()

        print("\n===== RAW RESULTS =====\n")

        print(results)

        organic_results = results.get(
            "organic_results",
            []
        )

        extracted_results = []

        for item in organic_results[:5]:

            extracted_results.append({

                "title":
                item.get(
                    "title"
                ),

                "snippet":
                item.get(
                    "snippet"
                ),

                "link":
                item.get(
                    "link"
                )
            })

        return {

            "success": True,

            "results":
            extracted_results
        }


# =========================================================
# SINGLETON
# =========================================================

search_tool = SearchTool()