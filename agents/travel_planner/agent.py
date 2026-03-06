import json
from google import genai
from google.genai import types
from models import Itinerary, TripInput
from config import GOOGLE_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, MAX_CHAT_HISTORY
from api_clients import fetch_places, format_places_for_prompt


def _get_client() -> genai.Client:
    return genai.Client(api_key=GOOGLE_API_KEY)


def _get_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        systemInstruction=SYSTEM_PROMPT,
        responseMimeType="application/json",
        responseSchema=Itinerary,
        temperature=0.8,
    )


def _build_generation_prompt(trip: TripInput, places_context: str) -> str:
    return f"""Plan a trip to {trip.destination} from {trip.start_date} to {trip.end_date}.

Traveler Profile:
- Budget tier: {trip.budget_tier}
- Interests: {', '.join(trip.interests)}
- Special notes: {trip.notes or 'None'}

{places_context}

Create a day-by-day itinerary with morning, afternoon, and evening activities for each day.
Include meal recommendations, accurate lat/lng coordinates, cost estimates in USD,
local tips, and packing suggestions."""


def generate_itinerary(trip: TripInput) -> Itinerary:
    """Generate a new itinerary from trip input."""
    client = _get_client()

    # Fetch real places from Foursquare
    places = fetch_places(trip.destination, trip.interests)
    places_context = format_places_for_prompt(places)

    prompt = _build_generation_prompt(trip, places_context)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=_get_config(),
    )

    data = json.loads(response.text)
    return Itinerary(**data)


def refine_itinerary(
    current_itinerary: Itinerary,
    user_message: str,
    chat_history: list[dict],
) -> Itinerary:
    """Refine an existing itinerary based on user feedback."""
    client = _get_client()

    # Build history for multi-turn context
    history = []
    recent = chat_history[-MAX_CHAT_HISTORY:]
    for msg in recent:
        role = "user" if msg["role"] == "user" else "model"
        history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=_get_config(),
        history=history,
    )

    refinement_prompt = f"""Here is the current itinerary:
{current_itinerary.model_dump_json(indent=2)}

The traveler requests: "{user_message}"

Return the complete updated itinerary with the requested changes applied.
Keep everything else the same unless the change logically affects other parts."""

    response = chat.send_message(refinement_prompt)
    data = json.loads(response.text)
    return Itinerary(**data)
