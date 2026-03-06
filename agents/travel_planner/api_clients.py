import requests
from config import FOURSQUARE_API_KEY, INTEREST_TO_FOURSQUARE


def fetch_places(destination: str, interests: list[str], limit: int = 20) -> list[dict]:
    """Fetch real places from Foursquare based on destination and interests."""
    if not FOURSQUARE_API_KEY:
        return []

    # Map interests to Foursquare category IDs
    category_ids = set()
    for interest in interests:
        if interest in INTEREST_TO_FOURSQUARE:
            for cat_id in INTEREST_TO_FOURSQUARE[interest].split(","):
                category_ids.add(cat_id)

    if not category_ids:
        category_ids = {"13065", "16000"}  # Default: food + landmarks

    try:
        response = requests.get(
            "https://api.foursquare.com/v3/places/search",
            headers={
                "Authorization": FOURSQUARE_API_KEY,
                "Accept": "application/json",
            },
            params={
                "near": destination,
                "categories": ",".join(category_ids),
                "limit": limit,
                "sort": "RELEVANCE",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        places = []
        for result in data.get("results", []):
            place = {
                "name": result.get("name", ""),
                "address": result.get("location", {}).get("formatted_address", ""),
                "category": (
                    result.get("categories", [{}])[0].get("name", "")
                    if result.get("categories")
                    else ""
                ),
                "latitude": result.get("geocodes", {})
                .get("main", {})
                .get("latitude"),
                "longitude": result.get("geocodes", {})
                .get("main", {})
                .get("longitude"),
            }
            places.append(place)

        return places

    except (requests.RequestException, KeyError, IndexError):
        return []


def format_places_for_prompt(places: list[dict]) -> str:
    """Format Foursquare places data into a string for the LLM prompt."""
    if not places:
        return "No external place data available. Use your own knowledge of popular places."

    lines = ["Here are real places at this destination (prefer these in your itinerary):"]
    for p in places:
        parts = [p["name"]]
        if p.get("category"):
            parts.append(f"({p['category']})")
        if p.get("address"):
            parts.append(f"- {p['address']}")
        lines.append("  - " + " ".join(parts))

    return "\n".join(lines)
