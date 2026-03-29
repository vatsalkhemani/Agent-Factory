# Agent Factory

Five standalone AI agents. Each one is built independently with its own tech stack — different LLMs, different tools, different agentic patterns. No shared code.

## Agents

### [Travel Planner](agents/travel_planner/) — Gemini 2.5 Flash + Folium + Foursquare

You give it: destination, dates, budget, interests.

The agent:
- Pulls real restaurants/attractions from Foursquare API
- Generates a structured day-by-day itinerary (morning/afternoon/evening)
- Plots everything on an interactive map with color-coded pins per day
- You refine via chat: "make day 2 more relaxed" — it updates the whole plan
- Export as markdown

### [Marketing Campaign](agents/marketing_agent/) — Gemini 3.1 Flash Lite + BeautifulSoup

You give it: a product URL, competitor URLs, target audience, campaign goal.

The agent:
- Scrapes your product page and competitor pages
- Builds a product brief and competitive analysis from the scraped data
- Develops brand positioning and a voice guide before writing anything
- Creates LinkedIn posts, Twitter thread, email sequence, blog outline, and ad copy — all in one consistent voice
- Scores every piece against brand/channel fit, auto-revises anything below threshold

### [Research Agent](agents/research_agent/) — Gemini 3.1 Flash Lite + DuckDuckGo + BeautifulSoup

You give it: a question.

The agent:
- Plans 3 search queries targeting different angles of the question
- Searches DuckDuckGo, scrapes results, extracts facts with confidence scores
- Scores its own coverage (1-10) and identifies specific gaps
- Replans with new queries that target those gaps — second round is always different from the first
- Loops 2-4 times until coverage is sufficient or further searching won't help
- Writes a structured report with citations

### [Job Application Agent](agents/job_application_agent/) — Gemini 3.1 Flash Lite + DuckDuckGo + BeautifulSoup

You give it: a job description + your resume (as text).

The agent:
- Parses both documents into structured data (skills, requirements, experience)
- Runs gap analysis: matching skills, missing skills, transferable skills
- Extracts the company name from the JD, finds their website, scrapes it, searches for news — builds talking points
- Rewrites your resume to align with the JD (reframes, never fabricates)
- Writes a cover letter that references specific company details from the research
- Scores against ATS criteria (keyword match 40%, relevance 40%, format 20%)
- If score < 7/10: auto-revises resume + cover letter, re-scores

### [Data Analyst Agent](agents/data_analyst_agent/) — Gemini 3.1 Flash Lite + Pandas + Plotly

You give it: a CSV file.

The agent:
- Profiles the data: column types, distributions, missing values, quality issues (no LLM, pure computation)
- Forms 4-6 hypotheses about what patterns might exist based on the profile
- Tests each hypothesis using a predefined toolkit (correlation, group comparison, outlier detection, time trends) — LLM picks which tools and parameters, but no generated code runs
- Ranks findings by importance, deep-dives the top 2
- Generates Plotly charts for key findings
- Writes a narrative report connecting everything into a data story
- No external APIs needed — just Gemini + your data

## Quick Start

```bash
cd agents/<agent_name>
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
streamlit run app.py
```

## Structure

Each agent is a silo — own deps, own .env, own README, own tech decisions.

```
Agent-Factory/
├── agents/
│   ├── travel_planner/
│   ├── marketing_agent/
│   ├── research_agent/
│   ├── job_application_agent/
│   └── data_analyst_agent/
├── CLAUDE.md
├── .gitignore
└── .env.example
```
