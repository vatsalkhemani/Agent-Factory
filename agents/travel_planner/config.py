import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY", "")

GEMINI_MODEL = "gemini-2.0-flash"

MAX_TRIP_DAYS = 14
MAX_CHAT_HISTORY = 10

# Foursquare category IDs mapped to user interests
INTEREST_TO_FOURSQUARE = {
    "Food": "13065",
    "History": "16000",
    "Nature": "16032",
    "Art": "10027",
    "Nightlife": "10032",
    "Shopping": "17000",
    "Adventure": "16032,16000",
    "Relaxation": "16032",
}

AVAILABLE_INTERESTS = list(INTEREST_TO_FOURSQUARE.keys())

BUDGET_TIERS = ["Budget", "Moderate", "Luxury"]

# Day pin colors for the map
DAY_COLORS = [
    "blue", "green", "red", "purple", "orange",
    "darkblue", "darkgreen", "darkred", "cadetblue", "pink",
    "lightblue", "lightgreen", "lightred", "beige", "gray",
]

SYSTEM_PROMPT = """You are an expert travel planner who creates detailed, realistic day-by-day itineraries.

Rules:
- Consider practical logistics: travel time between locations, opening hours, meal timing
- Respect the traveler's budget tier and interests
- Include latitude and longitude for every activity (must be accurate real coordinates)
- Estimate costs in USD
- Use your knowledge for weather expectations based on destination and season
- Include local tips (tipping customs, transit, safety, cultural norms)
- Include packing suggestions based on expected weather and activities
- When refining an existing itinerary, return the FULL updated itinerary, not just changed parts
- Suggest real, well-known places. If place data from Foursquare is provided, prefer those real venues.
- Each day should have 3 time slots: morning, afternoon, evening
- Each time slot should include a meal recommendation where appropriate (breakfast for morning, lunch for afternoon, dinner for evening)

Always respond with valid JSON matching the requested schema exactly."""
