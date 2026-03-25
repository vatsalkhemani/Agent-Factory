# Agent Factory

A collection of standalone AI agents, each solving a different real-world use case. Each agent uses its own tech stack and is independently runnable.

## Agents

| Agent | Category | Tech | Status |
|-------|----------|------|--------|
| [Travel Planner Agent](agents/travel_planner/) | Consumer | Gemini 2.5 Flash + Streamlit + Folium + Foursquare | Done |
| Text to Podcast Agent | Media | TBD | Planned |
| Investment Analyst Agent | Finance | TBD | Planned |
| Marketing Content Agent | Business | TBD | Planned |

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
│   ├── travel_planner/    # Gemini + Streamlit + Folium + Foursquare
│   ├── text_to_podcast/   # Coming soon
│   ├── investment_analyst/ # Coming soon
│   └── marketing_agent/   # Coming soon
├── CLAUDE.md
├── .gitignore
└── .env.example
```
