# Agent Factory

A collection of standalone AI agents, each solving a different real-world use case. Each agent uses its own tech stack and is independently runnable.

## Agents

| Agent | Category | Tech | Status |
|-------|----------|------|--------|
| [Travel Planner Agent](agents/travel_planner/) | Consumer | Gemini 2.5 Flash + Streamlit + Folium + Foursquare | Done |
| [Marketing Campaign Agent](agents/marketing_agent/) | Business | Gemini 2.5 Flash Lite + Streamlit + BeautifulSoup | Done |
| [Research Agent](agents/research_agent/) | Research | Gemini 2.5 Flash Lite + Streamlit + DuckDuckGo | Done |
| [Job Application Agent](agents/job_application_agent/) | Career | Gemini 2.5 Flash Lite + Streamlit + DuckDuckGo | Done |
| [Data Analyst Agent](agents/data_analyst_agent/) | Analytics | Gemini 2.5 Flash Lite + Streamlit + Pandas + Plotly | Done |

## Quick Start (any agent)

```bash
cd agents/<agent_name>
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
# Check the agent's README for run instructions
```

## Structure

Each agent is fully standalone in its own directory under `agents/`. No shared dependencies — each agent picks its own tech stack, UI framework, and LLM provider.

```
Agent-Factory/
├── agents/
│   ├── travel_planner/         # Gemini + Streamlit + Folium + Foursquare
│   ├── marketing_agent/        # Gemini + Streamlit + BeautifulSoup
│   ├── research_agent/         # Gemini + Streamlit + DuckDuckGo + BeautifulSoup
│   ├── job_application_agent/  # Gemini + Streamlit + DuckDuckGo + BeautifulSoup
│   └── data_analyst_agent/     # Gemini + Streamlit + Pandas + Plotly
├── CLAUDE.md
├── .gitignore
└── .env.example
```
