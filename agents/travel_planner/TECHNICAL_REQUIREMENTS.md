# Technical Requirements Document: Travel Planner Agent

## Architecture Overview

```
User (Streamlit UI)
    │
    ├── Form Input (destination, dates, budget, interests)
    │
    ▼
app.py (Streamlit)
    │
    ├── Calls api_clients.py ──► Foursquare API (real places)
    │
    ├── Calls agent.py ──► Gemini 2.0 Flash (itinerary generation)
    │                       │
    │                       ├── System prompt + trip details + place data
    │                       └── Returns structured JSON (Pydantic validated)
    │
    ├── Renders itinerary (day-by-day expanders)
    ├── Renders map (Folium) with daily pins + routes
    ├── Chat refinement loop (user ↔ Gemini)
    │
    └── Export (Markdown download)
```

## File Structure

```
agents/travel_planner/
├── app.py              # Streamlit entry point: layout, forms, chat, map, session state
├── agent.py            # Gemini integration: prompts, structured output, multi-turn chat
├── models.py           # Pydantic models: Activity, DayPlan, Itinerary, TripInput
├── api_clients.py      # Foursquare API wrapper with error handling
├── map_builder.py      # Folium map generation: pins per day, color-coded, route lines
├── export.py           # Markdown export of itinerary
├── config.py           # Constants, prompt templates, Foursquare category mappings
├── requirements.txt
├── .env.example
├── README.md
└── TECHNICAL_REQUIREMENTS.md
```

## Data Models (models.py)

```python
class TripInput:
    destination: str
    start_date: date
    end_date: date
    budget_tier: str          # "Budget" | "Moderate" | "Luxury"
    interests: list[str]      # ["Food", "History", "Nature", ...]
    notes: str                # Free-form special requests

class MealRecommendation:
    restaurant_name: str
    cuisine: str
    price_range: str          # "$", "$$", "$$$"

class Activity:
    time_slot: str            # "morning", "afternoon", "evening"
    time_range: str           # "09:00 - 11:30"
    name: str                 # "Visit the Colosseum"
    location: str             # Address or area name
    latitude: float           # For map pins
    longitude: float          # For map pins
    description: str          # 2-3 sentences
    estimated_cost_usd: float
    category: str             # "History", "Food", "Nature"
    meal: MealRecommendation | None

class DayPlan:
    day_number: int
    date: str
    theme: str                # "Ancient Rome & Historic Center"
    weather_note: str         # Gemini's seasonal knowledge
    activities: list[Activity]

class Itinerary:
    destination: str
    total_days: int
    currency: str
    estimated_total_cost_usd: float
    local_tips: list[str]     # 3-5 tips (tipping, transit, safety)
    packing_suggestions: list[str]
    days: list[DayPlan]
```

Key: Activities include `latitude`/`longitude` so we can plot them on the map without a separate geocoding call. Gemini provides these as part of structured output.

## Gemini Integration (agent.py)

**Model**: `gemini-2.0-flash` via `google-generativeai` SDK

**Structured output**: Use `response_mime_type="application/json"` + `response_schema` mapped to the Pydantic models. Gemini returns valid JSON matching our schema directly.

**Prompt flow**:
1. System prompt: "You are an expert travel planner..." (sets persona, rules, output expectations)
2. Initial generation: Trip details + Foursquare place data injected into prompt
3. Refinement: Current itinerary JSON + user's change request → returns full updated itinerary

**Multi-turn chat**: Use `model.start_chat(history=...)` for refinements. Cap at 10 exchanges to stay within context limits.

**Key design decision**: API calls (Foursquare) happen BEFORE the LLM call. We don't use Gemini's function-calling. The agent always needs place data for an itinerary - there's no conditional logic about when to call APIs. Simpler and more predictable.

## Foursquare Integration (api_clients.py)

**Endpoint**: `GET https://api.foursquare.com/v3/places/search`

**Parameters**:
- `near={destination}`
- `categories={mapped_category_ids}` based on user interests
- `limit=20`
- `sort=RELEVANCE`

**Category mapping** (user interest → Foursquare category ID):
- Food → 13065 (Dining)
- History → 16000 (Landmarks)
- Nature → 16032 (Parks & Outdoors)
- Art → 10027 (Museums)
- Nightlife → 10032 (Nightlife)
- Shopping → 17000 (Shopping)
- Adventure → 16000 + 16032

**Error handling**: If Foursquare fails, the agent still works - Gemini uses its own knowledge. Show a subtle warning that place data may be less precise.

## Map (map_builder.py)

**Library**: Folium + streamlit-folium

**Features**:
- One map showing all days
- Color-coded pins per day (Day 1 = blue, Day 2 = green, Day 3 = red, etc.)
- Popup on each pin: activity name + time
- Dashed lines connecting activities within the same day (route visualization)
- Auto-zoom to fit all pins

## Streamlit Layout (app.py)

```
SIDEBAR                          MAIN AREA
┌──────────────────┐  ┌──────────────────────────────────────┐
│ Trip Details Form │  │ [Trip Summary Bar]                   │
│                  │  │  Destination | Days | Budget | Cost   │
│ Destination: ___ │  │                                      │
│ Start: ___       │  │ [Interactive Map - Folium]            │
│ End: ___         │  │                                      │
│ Budget: [▼]      │  │ [Day 1 Expander]                     │
│ Interests: [✓✓]  │  │   Morning: activity...               │
│ Notes: ___       │  │   Afternoon: activity...             │
│                  │  │   Evening: activity...               │
│ [Plan My Trip]   │  │ [Day 2 Expander]                     │
│                  │  │   ...                                │
│ ─── Export ───   │  │                                      │
│ [📥 Download MD] │  │ ─── Chat Refinement ───              │
│                  │  │ [user]: make day 2 relaxed           │
└──────────────────┘  │ [agent]: Updated! Swapped hiking...  │
                      │ [___ type here ___]                  │
                      └──────────────────────────────────────┘
```

## Session State

| Key | Type | Purpose |
|-----|------|---------|
| `trip_input` | dict | Current form submission |
| `itinerary` | Itinerary | Current itinerary object |
| `chat_history` | list[dict] | Chat messages for display |
| `gemini_chat` | ChatSession | Gemini multi-turn object |
| `places_data` | list[dict] | Cached Foursquare results |

## Error Handling

| Scenario | Response |
|----------|----------|
| Gemini returns invalid JSON | Retry once, then show error with "Try again" button |
| Gemini rate limited (429) | Show warning: "Please wait a moment" |
| API key missing | Show specific error on app load with link to get the key |
| Foursquare fails | Continue without place data, show subtle warning |
| End date before start date | Form validation, inline error |
| Trip > 14 days | Cap with warning message |
