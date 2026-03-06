# Travel Planner Agent

An AI-powered travel planning agent that generates detailed day-by-day itineraries with interactive maps, grounded in real place data.

## What It Does

1. **Describe your trip** via a form: destination, dates, budget level, interests, and any special notes
2. **Get a structured itinerary** - day-by-day with morning/afternoon/evening activities, restaurant recommendations, estimated costs, weather-aware suggestions, and local tips
3. **See it on a map** - interactive map showing each day's locations and routes between them
4. **Refine via chat** - ask the agent to adjust ("make day 2 more relaxed", "swap the museum for something outdoors", "add more street food spots")
5. **Export your plan** - download the final itinerary as Markdown

## What Makes It Good

- **Real places** - uses Foursquare API so itineraries reference actual restaurants and attractions, not hallucinated ones
- **Interactive map** - visualize your daily routes and see if the plan makes geographic sense
- **Structured output** - organized day/activity/meal blocks, not a wall of text
- **Iterative refinement** - chat to tweak the plan without starting over
- **Minimal setup** - only 2 API keys needed

## Tech Stack

- **LLM**: Google Gemini 2.0 Flash (via `google-generativeai` SDK)
- **UI**: Streamlit
- **Maps**: Folium + streamlit-folium
- **Places Data**: Foursquare Places API
- **Data Models**: Pydantic v2

## Setup

```bash
cd agents/travel_planner
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
streamlit run app.py
```

## API Keys Needed

| Key | Where to Get | Free Tier |
|-----|-------------|-----------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) | 15 RPM, 1500 RPD |
| `FOURSQUARE_API_KEY` | [Foursquare Developers](https://foursquare.com/developers) | 1000 calls/day |

Both APIs have free tiers with no credit card required.
