import os
import requests

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

KNOWN_SELF = {
    "siddharth": "Nambs24",
    "nambiar": "Nambs24",
    "nambs24": "Nambs24",
}


def find_github_username(person: str) -> str:
    """
    Returns the correct GitHub username for a person.
    """

    if not person:
        return None

    key = person.lower().strip()

    # ✅ HARD MAP FOR YOU
    if key in KNOWN_SELF:
        return KNOWN_SELF[key]

    # -----------------------------
    # 🔎 TAVILY SEARCH FOR OTHERS
    # -----------------------------
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": f"{person} GitHub profile",
        "search_depth": "advanced",
        "max_results": 5,
    }

    response = requests.post(url, json=payload).json()

    for result in response.get("results", []):
        link = result.get("url", "")

        if "github.com/" in link:
            return link.rstrip("/").split("/")[-1]

    raise ValueError(f"GitHub username not found for {person}")
