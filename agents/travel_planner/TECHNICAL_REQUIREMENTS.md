# Technical Requirements Document: Travel Planner Agent

## How It Works (End to End)

Here's what happens when a user clicks "Plan My Trip":

```
1. USER fills form (destination, dates, budget, interests)
          │
          ▼
2. APP calls Foursquare API with destination + interests
   → Gets back real places: names, addresses, coordinates
   → If Foursquare fails or no key: skips this, agent still works
          │
          ▼
3. APP builds a prompt combining:
   - System instruction (travel planner persona + rules)
   - Trip details from the form
   - Real place data from Foursquare
          │
          ▼
4. APP sends prompt to Gemini 2.0 Flash
   - Uses structured output mode (responseSchema = Itinerary model)
   - Gemini returns valid JSON matching our Pydantic schema
   - Response is validated through Pydantic
          │
          ▼
5. APP renders the itinerary:
   - Summary bar (destination, days, cost)
   - Folium map with color-coded pins per day + route lines
   - Day-by-day expanders with activities, meals, costs
   - Local tips + packing suggestions
          │
          ▼
6. USER can REFINE via chat:
   - User types "make day 2 more relaxed"
   - App sends current itinerary JSON + user request to Gemini
   - Gemini returns the FULL updated itinerary (not a diff)
   - UI re-renders with changes
   - Multi-turn: up to 10 exchanges, preserving context
          │
          ▼
7. USER can EXPORT as Markdown download
```

### Why this architecture?
- **Foursquare before Gemini** (not function-calling): The agent always needs place data for an itinerary. There's no decision about "should I look up places?" — it always should. So we call the API upfront and inject the data into the prompt. Simpler and more predictable than tool-use loops.
- **Full replacement on refinement** (not diff/patch): When the user changes day 2, Gemini returns the entire itinerary, not just day 2. This avoids merge logic bugs. The token cost is trivial — a 7-day itinerary is ~2-3K tokens.
- **Structured JSON output**: Gemini's `responseSchema` parameter forces it to return valid JSON matching our Pydantic models. No regex parsing, no "please format as JSON" in the prompt.

## File Structure

```
agents/travel_planner/
├── app.py              # Streamlit UI: form, map, itinerary display, chat, export
├── agent.py            # Gemini calls: generate + refine itineraries
├── models.py           # Pydantic data models (the contract between all components)
├── api_clients.py      # Foursquare API: fetch real places by destination + interests
├── map_builder.py      # Folium map: color-coded pins, route lines, popups
├── export.py           # Convert itinerary to Markdown for download
├── config.py           # API keys, constants, system prompt, interest-to-category mapping
├── requirements.txt    # 7 Python dependencies
├── .env.example        # Template for API keys
├── README.md           # Product description + setup
└── TECHNICAL_REQUIREMENTS.md  # This file
```

### How the files connect:

```
config.py ─────── loaded by everything (API keys, constants, prompts)
     │
models.py ─────── used by everything (shared data shapes)
     │
api_clients.py ── called by agent.py (fetches Foursquare data)
     │
agent.py ──────── called by app.py (generates/refines itineraries via Gemini)
     │
map_builder.py ── called by app.py (builds Folium map from itinerary)
     │
export.py ─────── called by app.py (converts itinerary to Markdown)
     │
app.py ────────── entry point (Streamlit: wires everything together)
```

## Data Models

The Pydantic models define the contract between Gemini, the UI, and export:

```
TripInput (what the user submits)
├── destination: "Tokyo, Japan"
├── start_date / end_date
├── budget_tier: "Budget" | "Moderate" | "Luxury"
├── interests: ["Food", "History", ...]
└── notes: "vegetarian, traveling with kids"

Itinerary (what Gemini returns, what the UI renders)
├── destination, total_days, currency
├── estimated_total_cost_usd
├── local_tips: ["Tipping is not customary...", ...]
├── packing_suggestions: ["Comfortable walking shoes", ...]
└── days: [DayPlan]
        ├── day_number, date, theme
        ├── weather_note: "Warm and humid, ~28C"
        └── activities: [Activity]
                ├── time_slot: "morning" | "afternoon" | "evening"
                ├── time_range: "09:00 - 11:30"
                ├── name: "Visit Senso-ji Temple"
                ├── location: "2 Chome-3-1 Asakusa, Taito City"
                ├── latitude / longitude (for map pins)
                ├── description: "2-3 sentences"
                ├── estimated_cost_usd: 0.0
                ├── category: "History"
                └── meal: MealRecommendation | null
                        ├── restaurant_name: "Sometaro"
                        ├── cuisine: "Japanese Okonomiyaki"
                        └── price_range: "$"
```

Activities include `latitude`/`longitude` so the map can plot pins without a separate geocoding API call — Gemini provides coordinates as part of its structured output.

## Key Technical Decisions

| Decision | Why |
|----------|-----|
| **Gemini 2.0 Flash** over Pro | Faster, cheaper, generous free tier (15 RPM, 1500 RPD). Quality is sufficient for structured itinerary generation. |
| **`google-genai` SDK** (new) | The `google-generativeai` package is deprecated. New SDK uses `genai.Client` pattern. |
| **Foursquare** over Google Places | Foursquare has a genuine free tier with no credit card. Google Places requires billing setup. |
| **Streamlit** for UI | Fast to build, native chat components, good form handling, Folium integration via `streamlit-folium`. |
| **No database** | Itineraries live in Streamlit session state. Export covers "save my work". Keeps setup zero-infrastructure. |
| **No LangChain** | Direct SDK calls are simpler, more transparent, and easier to debug for a standalone agent. |

## Error Handling

| Scenario | What Happens |
|----------|-------------|
| No Google API key | App shows error on startup with link to get the key |
| No Foursquare key | Agent works fine — uses Gemini's own knowledge instead of real place data |
| Foursquare API fails | Silently falls back to Gemini-only mode |
| Gemini returns bad JSON | Error shown with option to retry |
| Gemini rate limited | Warning message: "Please wait a moment" |
| End date before start date | Form validation blocks submission |
| Trip longer than 14 days | Capped with a warning message |
