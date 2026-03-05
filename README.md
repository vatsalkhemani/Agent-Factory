# Agent Factory

A collection of standalone AI agents, each solving a different real-world use case. Every agent is independently runnable with minimal setup.

## Agents

| Agent | Category | Description | Status |
|-------|----------|-------------|--------|
| Tic Tac Toe Agent | Gaming | Play against an AI with personality and difficulty levels | Planned |
| Travel Planner Agent | Consumer | Generates day-by-day travel itineraries with real data | Planned |
| Text to Podcast Agent | Media | Converts text into multi-speaker podcast audio | Planned |
| Investment Analyst Agent | Finance | Stock/crypto analysis dashboard with AI insights | Planned |
| Marketing Content Agent | Business | Multi-platform marketing content generator | Planned |

## Quick Start (any agent)

```bash
cd agents/<agent_name>
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
streamlit run app.py
```

## Tech Stack

- **Python 3.10+** - Core language
- **Streamlit** - UX / chat interface
- **OpenAI SDK** - LLM access
- **Pydantic** - Structured data validation

## Structure

Each agent is fully standalone in its own directory under `agents/`. No shared dependencies between agents - clone any single agent folder and it works on its own.

```
agents/<agent-name>/
  README.md
  TECHNICAL_REQUIREMENTS.md
  requirements.txt
  .env.example
  app.py          # Streamlit entry point
  agent.py        # LLM orchestration
```
