# Agent Factory

## Project Overview
Portfolio repository of standalone AI agents. Each agent is siloed, independently runnable, and demonstrates AI product-building skills.

## Design Principles
- Each agent is fully independent - no shared code between agents
- Simple setup: `pip install -r requirements.txt` + `.env` + `streamlit run app.py`
- API connectors + LLM APIs as building blocks (no heavy frameworks like LangChain)
- OpenAI SDK for LLM access, Pydantic for structured outputs
- Streamlit for all UX screens

## Agent Template Structure
Every agent in `agents/<agent-name>/` must contain:
```
agents/<agent-name>/
  README.md                    # Setup, usage
  TECHNICAL_REQUIREMENTS.md    # Architecture, APIs, data flow
  requirements.txt             # Python dependencies
  .env.example                 # Required API keys for this agent
  app.py                       # Streamlit entry point
  agent.py                     # LLM orchestration logic
```

## Agents
| Agent | Directory | Status |
|-------|-----------|--------|
| Tic Tac Toe Agent | `agents/tic_tac_toe/` | Planned |
| Travel Planner Agent | `agents/travel_planner/` | Planned |
| Text to Podcast Agent | `agents/text_to_podcast/` | Planned |
| Investment Analyst Agent | `agents/investment_analyst/` | Planned |
| Marketing Content Agent | `agents/marketing_agent/` | Planned |

## Conventions
- Python 3.10+
- Use `python-dotenv` for config, load `.env` from agent's own directory
- Use Pydantic v2 models for all structured LLM responses
- Use `openai` SDK directly (works with OpenAI and compatible endpoints)
- Streamlit chat components (`st.chat_input`, `st.chat_message`) for conversational UX
- Each agent tracks its own dependencies in its own `requirements.txt`
