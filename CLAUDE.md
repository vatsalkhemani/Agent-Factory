# Agent Factory

## Project Overview
Repository of standalone AI agents. Each agent is independently built, using its own tech stack and approach. The goal is to explore different ways to build agents - different LLMs, frameworks, UI tools, and patterns.

## Design Principles
- Each agent is fully independent - no shared code
- Tech stack is chosen per agent (not uniform)
- Each agent is planned from scratch before building
- Simple setup per agent: install deps, add API keys, run

## Per-Agent Requirements
Every agent in `agents/<agent-name>/` must have:
- `README.md` - Product story: what it does, problem/solution, end-to-end user flow, setup
- `TECHNICAL_REQUIREMENTS.md` - Technical story: how it works end-to-end, architecture, file connections, key decisions and WHY
- A UX screen (framework varies per agent)
- `.env.example` - Required API keys
- `requirements.txt` or equivalent dependency file

**IMPORTANT**: Docs must always be in sync with code. After building or changing an agent, update both README and TRD to reflect the actual implementation.

## Agents
| Agent | Directory | Status |
|-------|-----------|--------|
| Travel Planner Agent | `agents/travel_planner/` | Done (Gemini 2.5 Flash + Streamlit + Folium + Foursquare) |
| Marketing Campaign Agent | `agents/marketing_agent/` | Done (Gemini 2.5 Flash Lite + Streamlit + BeautifulSoup) |
| Research Agent | `agents/research_agent/` | Done (Gemini 2.5 Flash Lite + Streamlit + DuckDuckGo + BeautifulSoup) |
| Job Application Agent | `agents/job_application_agent/` | Done (Gemini 2.5 Flash Lite + Streamlit + DuckDuckGo + BeautifulSoup) |
| Data Analyst Agent | `agents/data_analyst_agent/` | Done (Gemini 2.5 Flash Lite + Streamlit + Pandas + Plotly) |
