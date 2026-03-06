# Travel Planner Agent

An AI-powered travel planning agent that generates detailed day-by-day itineraries with interactive maps, grounded in real place data.

## The Product

### Problem
Planning a trip is time-consuming. You have to research destinations, find restaurants, figure out logistics, estimate costs, and organize it all into a coherent day-by-day plan. Most people end up with a messy Google Doc or scattered browser tabs.

### Solution
A conversational travel planner that does the heavy lifting. You tell it where you're going, when, your budget, and what you like — it gives you a complete, structured itinerary with real places, a visual map, and cost estimates. Then you refine it through chat until it's perfect.

### User Flow (End to End)

**Step 1: Describe your trip**
You fill out a simple sidebar form:
- Where are you going? (e.g., "Tokyo, Japan")
- When? (start and end dates)
- Budget level? (Budget / Moderate / Luxury)
- What do you enjoy? (Food, History, Nature, Art, Nightlife, Shopping, Adventure, Relaxation)
- Any special requests? (e.g., "traveling with kids", "vegetarian", "want street food only")

**Step 2: Get your itinerary**
The agent generates a structured day-by-day plan. Each day has:
- A theme (e.g., "Historic Temples & Traditional Food")
- Morning, afternoon, and evening activities with specific times
- Restaurant recommendations for each meal
- Cost estimates in USD
- Weather expectations based on season
- Real place names from Foursquare (not hallucinated)

You also get:
- Local tips (tipping customs, transit advice, safety notes)
- Packing suggestions based on expected weather and activities
- Total estimated trip cost

**Step 3: See it on a map**
An interactive map shows all your activities as pins, color-coded by day. Dashed lines connect each day's activities so you can see if the routing makes sense geographically. Click any pin for details.

**Step 4: Refine via chat**
Not happy with something? Chat with the agent:
- "Make day 2 more relaxed"
- "Swap the museum on day 3 for something outdoors"
- "Add more street food spots"
- "I want to spend less on day 4"

The agent updates the entire itinerary while keeping the rest intact.

**Step 5: Export**
Download your final plan as a Markdown file — clean, formatted, ready to share or print.

## Tech Stack

- **LLM**: Google Gemini 2.0 Flash (via `google-genai` SDK)
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

Both have free tiers with no credit card required. The Foursquare key is optional — the agent works without it but itineraries will rely solely on Gemini's knowledge instead of verified place data.
