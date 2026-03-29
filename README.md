# Agent Factory

A collection of useful AI agents, each built independently with its own tech stack. Different LLMs, different tools, different agentic patterns. No shared code.

## Agents

| Agent | Category | Tech |
|-------|----------|------|
| [Travel Planner](agents/travel_planner/) | Consumer | Gemini 2.5 Flash, Streamlit, Folium, Foursquare |
| [Marketing Campaign](agents/marketing_agent/) | Business | Gemini 3.1 Flash Lite, Streamlit, BeautifulSoup |
| [Research Agent](agents/research_agent/) | Research | Gemini 3.1 Flash Lite, Streamlit, DuckDuckGo, BeautifulSoup |
| [Job Application](agents/job_application_agent/) | Career | Gemini 3.1 Flash Lite, Streamlit, DuckDuckGo, BeautifulSoup |
| [Data Analyst](agents/data_analyst_agent/) | Analytics | Gemini 3.1 Flash Lite, Streamlit, Pandas, Plotly |

---

### Travel Planner

**Input:** Destination, dates, budget, interests

The agent:
- Pulls real restaurants and attractions from Foursquare API
- Generates a structured day-by-day itinerary (morning/afternoon/evening)
- Plots everything on an interactive map with color-coded pins per day
- You refine via chat: "make day 2 more relaxed", it updates the whole plan

**Output:** Complete itinerary with real places, cost estimates, weather tips, packing suggestions, interactive map, exportable as markdown

---

### Marketing Campaign

**Input:** Product URL, competitor URLs, target audience, campaign goal

The agent:
- Scrapes your product page and competitor pages
- Builds a product brief and competitive analysis from the scraped data
- Develops brand positioning and a voice guide before writing anything
- Creates LinkedIn posts, Twitter thread, email sequence, blog outline, and ad copy, all in one consistent voice
- Scores every piece against brand/channel fit, auto-revises anything below threshold

**Output:** Full campaign package with product intelligence, competitive analysis, brand positioning, voice guide, content for 5 channels, quality scores, downloadable as a bundle

---

### Research Agent

**Input:** A question

The agent:
- Plans 3 search queries targeting different angles of the question
- Searches DuckDuckGo, scrapes results, extracts facts with confidence scores
- Scores its own coverage (1-10) and identifies specific gaps
- Replans with new queries that target those gaps, second round is always different from the first
- Loops 2-4 times until coverage is sufficient or further searching won't help

**Output:** Structured report with executive summary, sectioned findings, source citations, and a visible reasoning trace showing every search/extract/evaluate decision

---

### Job Application

**Input:** Job description + your resume (as text)

The agent:
- Parses both documents into structured data (skills, requirements, experience)
- Runs gap analysis: matching skills, missing skills, transferable skills
- Extracts company name from the JD, finds their website, scrapes it, searches for news, builds talking points
- Rewrites your resume to align with the JD (reframes, never fabricates)
- Writes a cover letter that references specific company details from the research
- Scores against ATS criteria (keyword match 40%, relevance 40%, format 20%)
- If score < 7/10: auto-revises resume + cover letter, re-scores

**Output:** Tailored resume, personalized cover letter, gap analysis breakdown, company intel with talking points, ATS score with per-criteria feedback, downloadable as markdown

---

### Data Analyst

**Input:** A CSV file

The agent:
- Profiles the data: column types, distributions, missing values, quality issues (no LLM, pure computation)
- Forms 4-6 hypotheses about what patterns might exist based on the profile
- Tests each hypothesis using a predefined toolkit (correlation, group comparison, outlier detection, time trends). LLM picks which tools and parameters, but no generated code runs
- Ranks findings by importance, deep-dives the top 2
- Generates Plotly charts for key findings

**Output:** Analysis report with dataset summary, ranked findings with importance badges, interactive Plotly charts, narrative connecting findings into a data story, methodology notes, downloadable as markdown

---

## Quick Start

```bash
cd agents/<agent_name>
pip install -r requirements.txt
cp .env.example .env     # Add your API keys
streamlit run app.py
```

## Structure

Each agent is a silo with its own deps, .env, README, and tech decisions.

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
