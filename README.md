# Agent Factory

A collection of standalone AI agents, each solving a different real-world use case. Each agent uses its own tech stack and is independently runnable.

## Agents

| Agent | Category | Description | Status |
|-------|----------|-------------|--------|
| Travel Planner Agent | Consumer | Generates day-by-day travel itineraries with real data | Up Next |
| Text to Podcast Agent | Media | Converts text into multi-speaker podcast audio | Planned |
| Investment Analyst Agent | Finance | Stock/crypto analysis dashboard with AI insights | Planned |
| Marketing Content Agent | Business | Multi-platform marketing content generator | Planned |

## Quick Start (any agent)

```bash
cd agents/<agent_name>
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
# Run command varies per agent - check agent's README
```

## Structure

Each agent is fully standalone in its own directory under `agents/`. No shared dependencies - each agent picks its own tech stack, UI framework, and LLM provider.
