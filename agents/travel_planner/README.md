# Travel Planner Agent

An AI-powered travel planning agent that generates detailed day-by-day itineraries with interactive maps, grounded in real place data.

![Travel Planner Screenshot](assets/screenshot.png)

## What This Agent Can Do

- **Generate full trip itineraries** - Give it a destination, dates, budget, and interests. It returns a structured day-by-day plan with morning/afternoon/evening activities, restaurant recommendations, and cost estimates.

- **Ground plans in real data** - Uses the Foursquare Places API to pull actual restaurants, landmarks, and attractions at your destination. Your itinerary references real places, not hallucinated ones.

- **Visualize on an interactive map** - Every activity is plotted on a Folium map with color-coded pins per day (Day 1 = blue, Day 2 = green, etc.). Dashed route lines connect each day's stops so you can see if the plan makes geographic sense. Click any pin for activity details.

- **Refine through conversation** - Don't like something? Chat with the agent: "make day 2 more relaxed", "swap the museum for something outdoors", "add more street food". It updates the full itinerary while keeping the rest intact.

- **Export your plan** - Download the final itinerary as a clean Markdown file with all days, activities, meals, costs, local tips, and packing suggestions. Ready to share or print.

## The Product

### Problem
Planning a trip is time-consuming. You research destinations, hunt for restaurants, figure out logistics, estimate costs, and try to organize it all into a day-by-day plan. Most people end up with a messy Google Doc or scattered browser tabs.

### Solution
A conversational travel planner that does the heavy lifting. Describe your trip once, get a complete structured itinerary with real places and a visual map, then refine it through chat until it's perfect.

### User Flow

**Step 1: Describe your trip** in the sidebar form:
- Destination (e.g., "Sri Lanka")
- Travel dates
- Budget level (Budget / Moderate / Luxury)
- Interests (Food, History, Nature, Art, Nightlife, Shopping, Adventure, Relaxation)
- Special notes (e.g., "Boys trip. Need casino and surf minimum, and relaxation")

**Step 2: Get your itinerary** - The agent generates a structured plan. Each day includes:
- A theme (e.g., "Surf Adventure & Beach Day")
- Morning, afternoon, and evening activities with specific times and locations
- Restaurant recommendations for each meal
- Cost estimates in USD
- Weather expectations based on season and destination
- Local tips and packing suggestions

**Step 3: See it on the map** - An interactive map shows all activities as clickable pins, color-coded by day, with route lines connecting each day's stops.

**Step 4: Refine via chat** - Adjust the plan conversationally. The agent remembers context and updates the full itinerary with your changes.

**Step 5: Export** - Download as Markdown with one click from the sidebar.

## Tech Stack

| Technology | What It Does |
|-----------|-------------|
| **Google Gemini 2.5 Flash** | The LLM brain. Generates structured itineraries from trip details. Uses structured JSON output mode with a Pydantic schema so responses are always valid and parseable. Handles both initial generation and chat-based refinement. |
| **Foursquare Places API** | Provides real place data. Given a destination and interest categories (food, landmarks, nature, etc.), it returns actual restaurant names, attraction names, addresses, and coordinates. This grounds the itinerary in reality instead of relying on LLM knowledge alone. |
| **Streamlit** | The UI framework. Handles the sidebar form, day-by-day itinerary rendering with expanders, chat interface for refinement, session state management, and file downloads. |
| **Folium + streamlit-folium** | Interactive map rendering. Plots activities as markers with popups, draws route lines between daily stops, auto-zooms to fit all pins. Integrates into Streamlit via the streamlit-folium bridge. |
| **Pydantic v2** | Data validation. Defines the shape of the itinerary (days, activities, meals, coordinates) as typed Python models. These models serve triple duty: Gemini's response schema, internal data passing, and export formatting. |

## Setup

```bash
cd agents/travel_planner
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
streamlit run app.py
```

## API Keys Needed

| Key | Where to Get | What It Enables | Free Tier |
|-----|-------------|-----------------|-----------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) | Gemini LLM for itinerary generation and chat refinement | 15 requests/min, 1500 requests/day |
| `FOURSQUARE_API_KEY` | [Foursquare Developers](https://foursquare.com/developers) | Real place names, addresses, and coordinates for your destination | 1000 calls/day |

Both have free tiers with no credit card required.

The Foursquare key is **optional** — the agent works without it but itineraries will rely solely on Gemini's knowledge instead of verified place data.
