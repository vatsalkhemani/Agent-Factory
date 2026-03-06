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
- `README.md` - Setup and usage instructions
- `TECHNICAL_REQUIREMENTS.md` - Architecture, APIs, data flow
- A UX screen (framework varies per agent)
- `.env.example` - Required API keys
- `requirements.txt` or equivalent dependency file

## Agents
| Agent | Directory | Status |
|-------|-----------|--------|
| Travel Planner Agent | `agents/travel_planner/` | Up Next |
| Text to Podcast Agent | `agents/text_to_podcast/` | Planned |
| Investment Analyst Agent | `agents/investment_analyst/` | Planned |
| Marketing Content Agent | `agents/marketing_agent/` | Planned |
