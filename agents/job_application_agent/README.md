# Job Application Agent

An AI agent that takes a job description and your resume, then autonomously: analyzes the gap, researches the company, tailors your resume, writes a personalized cover letter, self-evaluates against ATS criteria, and revises weak sections. You paste two text blocks; it delivers a complete application package.

## The Problem

Every job application should be tailored. But manually rewriting your resume and cover letter for each job is tedious. You need to identify which skills match, research the company, reframe your experience, and make sure you hit the right keywords -- all while keeping it authentic.

## What This Agent Does

You paste a job description and your resume. The agent:

1. **Parses** both documents -- extracts structured data from the JD (required skills, key phrases, experience level) and your resume (skills, experiences, education)
2. **Gap Analysis** -- identifies matching skills, missing skills, and transferable skills. Scores your overall alignment as strong/moderate/weak
3. **Company Research** -- autonomously extracts the company name from the JD, scrapes their website, and searches for recent news/culture signals. Builds a set of talking points
4. **Tailors Resume** -- rewrites your professional summary and experience bullets to align with the JD. Weaves in keywords naturally. Never fabricates -- only reframes
5. **Cover Letter** -- writes a personalized cover letter that connects your experience to the role and references specific company details from the research
6. **ATS Evaluation** -- scores the tailored resume on keyword match (40%), relevance (40%), and format (20%). Identifies missing keywords
7. **Auto-Revision** -- if the ATS score is below 7/10, automatically revises both the resume and cover letter, then re-evaluates

## User Flow

1. Open the app, paste the full job description in the sidebar
2. Paste your resume text
3. Hit "Analyze & Tailor"
4. Watch the 7-phase pipeline: parsing, gap analysis, company research, tailoring, cover letter, evaluation, revision
5. Review results across 5 tabs: Gap Analysis, Tailored Resume (side-by-side with original), Cover Letter, Company Intel, ATS Scores
6. Download tailored resume and cover letter as markdown

## What Makes This an Agent (Not a Wrapper)

- **Autonomous company research**: Extracts company name from JD, finds the website, scrapes it, searches for news -- all without user input
- **Self-evaluation with real criteria**: ATS scoring uses specific metrics (keyword overlap, format quality, relevance) not just "looks good"
- **Conditional revision loop**: Only revises if score < 7. Doesn't waste time on already-good output
- **Gap-driven tailoring**: The tailoring is informed by the specific gap analysis, not a generic rewrite
- **Multiple tools working together**: Parser + researcher + gap analyzer + writer + evaluator -- each contributes a different capability

## Setup

```bash
cd agents/job_application_agent
pip install -r requirements.txt
```

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

Run:
```bash
streamlit run app.py
```

## Tech Stack

- **LLM**: Gemini 2.5 Flash Lite (parsing, analysis, writing, evaluation)
- **Web Search**: DuckDuckGo via `duckduckgo-search` (free, no API key) for company research
- **Web Scraping**: BeautifulSoup for company website content
- **UI**: Streamlit with live progress, side-by-side comparison, score badges
- **Data Models**: Pydantic for structured validation at every boundary
