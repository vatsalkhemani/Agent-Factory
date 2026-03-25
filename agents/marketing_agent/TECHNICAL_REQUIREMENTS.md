# Marketing Campaign Agent — Technical Requirements Document

## Architecture Overview

This agent follows an **Orchestrator-Worker pattern with an Evaluator-Optimizer loop**. A central orchestrator drives the agent through sequential phases, each phase delegating to specialized workers. An evaluator reviews all generated content and triggers revision where needed.

```
User Input
    │
    ▼
┌─────────────────────────────┐
│     CAMPAIGN ORCHESTRATOR   │  ← Drives the entire pipeline
│                             │
│  Phase 1: RESEARCH          │
│  ├── Product Scraper        │  ← Scrapes product URL, extracts content
│  ├── Competitor Scraper     │  ← Scrapes competitor URLs
│  └── Research Analyst       │  ← LLM: builds intelligence brief + competitive analysis
│                             │
│  Phase 2: STRATEGY          │
│  ├── Positioning Agent      │  ← LLM: develops brand positioning from research
│  └── Voice Agent            │  ← LLM: creates brand voice guide
│                             │
│  Phase 3: CONTENT CREATION  │
│  ├── LinkedIn Worker        │  ← LLM: 3 LinkedIn posts
│  ├── Twitter Worker         │  ← LLM: 1 tweet thread (5-7 tweets)
│  ├── Email Worker           │  ← LLM: 3-email nurture sequence
│  ├── Blog Worker            │  ← LLM: full blog post outline
│  └── Ad Copy Worker         │  ← LLM: 3 ad copy variations
│                             │
│  Phase 4: EVALUATION        │
│  └── Evaluator Agent        │  ← LLM: scores each piece, flags weak ones
│       └── Revision loop     │  ← LLM: rewrites pieces scoring below threshold
│                             │
│  Phase 5: DELIVERY          │
│  └── Package & display      │  ← Assembles campaign dashboard + export
└─────────────────────────────┘
```

## File Structure

```
agents/marketing_agent/
├── app.py                    # Streamlit UI — main entry point
├── orchestrator.py           # Campaign orchestrator — drives all phases
├── scraper.py                # Web scraping — product & competitor research
├── agents/
│   ├── __init__.py
│   ├── research_agent.py     # Analyzes scraped data → intelligence brief + competitive analysis
│   ├── strategy_agent.py     # Builds brand positioning + voice guide
│   ├── content_agents.py     # All 5 content channel workers
│   └── evaluator_agent.py    # Scores content, triggers revisions
├── prompts/
│   ├── __init__.py
│   ├── research_prompts.py   # Prompts for research analysis
│   ├── strategy_prompts.py   # Prompts for positioning + voice
│   ├── content_prompts.py    # Prompts for each content channel
│   └── evaluator_prompts.py  # Prompts for evaluation + revision
├── models.py                 # Pydantic data models for all structured data
├── gemini_client.py          # Gemini API wrapper — single point of LLM access
├── config.py                 # Configuration constants
├── requirements.txt
├── .env.example
├── README.md
└── TECHNICAL_REQUIREMENTS.md
```

## How It Works End-to-End

### 1. User Input → Orchestrator

The user fills a Streamlit form:
- Product URL (required)
- Product description (required, 1-2 sentences)
- Target audience (required)
- Competitor URLs (1-3, at least 1 required)
- Campaign goal (dropdown: launch, awareness, lead gen, engagement)

On submit, `app.py` passes input to `orchestrator.py` which manages the entire pipeline.

### 2. Phase 1: Research

**Scraping (scraper.py):**
- `scrape_url(url)` fetches the page with `requests`, parses with `BeautifulSoup`
- Extracts: page title, meta description, headings (h1-h3), paragraph text, link text
- Strips nav/footer/script noise — focuses on main content
- Returns structured `ScrapedPage` object
- Timeout: 10 seconds per URL, graceful failure with error message
- User-Agent header set to avoid basic blocks

**Research Analysis (research_agent.py):**
- Takes scraped product data + user description → calls Gemini → produces `ProductBrief`
  - What the product does
  - Key features and value propositions
  - Target audience signals
  - Current messaging tone
- Takes scraped competitor data → calls Gemini → produces `CompetitiveAnalysis`
  - Per-competitor: positioning, strengths, messaging approach
  - Cross-competitor: gaps and opportunities
  - Where THIS product can differentiate

**Why scrape instead of trusting user input?** The agent gets ground truth from real websites. This is what makes it agentic — it gathers its own evidence rather than relying solely on what the user claims.

### 3. Phase 2: Strategy

**Positioning (strategy_agent.py):**
- Input: ProductBrief + CompetitiveAnalysis + target audience + campaign goal
- Output: `BrandPositioning`
  - Core positioning statement
  - Key messages (3-5)
  - Differentiators
  - Proof points

**Voice Guide (strategy_agent.py):**
- Input: ProductBrief + BrandPositioning + target audience
- Output: `BrandVoiceGuide`
  - Tone attributes (e.g., "confident but not arrogant")
  - Language do's and don'ts
  - Example phrases that match the voice
  - Words/phrases to avoid

**Why strategy before content?** This is the core insight. Without positioning and voice, content is random. With it, every piece tells the same story in the same voice. The voice guide becomes a constraint passed to every content worker.

### 4. Phase 3: Content Creation

All 5 workers live in `content_agents.py`. Each receives the same context package:
- ProductBrief
- BrandPositioning
- BrandVoiceGuide
- Campaign goal
- Target audience

Each worker has a channel-specific prompt that produces platform-optimized content:

| Worker | Output | Platform Constraints |
|--------|--------|---------------------|
| `generate_linkedin_posts()` | 3 posts (thought leadership, product value, social proof) | Professional tone, 1300 char sweet spot, hook-first |
| `generate_twitter_thread()` | 5-7 connected tweets | 280 char/tweet, conversational, thread narrative arc |
| `generate_email_sequence()` | 3 emails (hook → value → CTA) | Subject lines, preview text, body, clear CTAs |
| `generate_blog_outline()` | Full outline with section summaries | SEO-aware structure, intro/body/conclusion, key points per section |
| `generate_ad_copy()` | 3 variations (headline + body + CTA) | Short-form, benefit-driven, action-oriented |

**Content workers run sequentially** — Gemini Flash is fast enough and we avoid rate limiting complexity.

### 5. Phase 4: Evaluation

**Evaluator (evaluator_agent.py):**
- Reviews EVERY content piece against 3 criteria:
  1. **Voice consistency** (1-10) — does it match the brand voice guide?
  2. **Campaign coherence** (1-10) — does it tell the same story as other pieces?
  3. **Channel optimization** (1-10) — is it right for the platform?
- Produces overall score + specific feedback per piece

**Revision loop:**
- Pieces scoring below **7/10 on any criterion** get sent back for revision
- Revision prompt includes: original piece + evaluator feedback + voice guide
- **Max 1 revision pass** — avoids infinite loops, good enough for quality lift
- Revised pieces get re-scored (scores shown to user, no further revision)

**Why self-evaluate?** This is the evaluator-optimizer pattern from Anthropic's best practices. The agent doesn't just generate — it critiques its own work and improves. This is what separates an agent from a prompt wrapper.

### 6. Phase 5: Delivery

**Dashboard (app.py):**
- Campaign overview with quality scores per piece
- Expandable sections for each channel's content
- Research brief and competitive analysis viewable
- Brand positioning and voice guide viewable

**Export:**
- "Download Campaign" button → generates a single Markdown file
- Organized with headers: Research → Strategy → Content (by channel) → Scores
- Ready to copy/paste into any tool

## Data Models (models.py)

All structured data uses Pydantic models for validation:

```python
# Research
ScrapedPage(url, title, meta_description, headings, paragraphs, links)
ProductBrief(summary, features, value_propositions, audience_signals, messaging_tone)
CompetitorProfile(url, positioning, strengths, messaging_approach)
CompetitiveAnalysis(competitors: list[CompetitorProfile], gaps, opportunities)

# Strategy
BrandPositioning(statement, key_messages, differentiators, proof_points)
BrandVoiceGuide(tone_attributes, dos, donts, example_phrases, words_to_avoid)

# Content
LinkedInPost(hook, body, cta, angle)
TwitterThread(tweets: list[str])
Email(subject, preview_text, body, cta)
EmailSequence(emails: list[Email])
BlogOutline(title, sections: list[BlogSection])
AdCopy(headline, body, cta)

# Evaluation
ContentScore(voice_score, coherence_score, channel_score, feedback, needs_revision)
CampaignPackage(brief, analysis, positioning, voice_guide, content, scores)
```

## Gemini Integration (gemini_client.py)

Single wrapper around the Gemini API:
- `GeminiClient` class initialized with API key from `.env`
- Uses `gemini-2.5-flash` model for all calls
- `generate(prompt, system_instruction)` → returns text response
- `generate_json(prompt, system_instruction)` → returns parsed JSON (using Gemini's JSON mode)
- Temperature: 0.7 for content generation, 0.3 for analysis/evaluation
- Handles retries (1 retry on failure) and timeout (30s)

**Why a single client?** One file, one class, one place to change model config. Every agent imports and uses this.

## Streamlit UI (app.py)

### Layout
- **Sidebar**: Input form (product URL, description, audience, competitor URLs, campaign goal)
- **Main area**: Phase-by-phase progress display

### Real-time Progress
- `st.status()` containers for each phase — shows spinner while running, checkmark when done
- Phase results displayed as they complete (user doesn't wait for everything)
- Expandable sections for detailed output (research, strategy docs)

### Session State
- All campaign data stored in `st.session_state`
- Survives Streamlit reruns
- Enables download button after completion

### Flow
1. User fills form → clicks "Launch Campaign"
2. Phase 1 status opens: "Researching product..." → shows brief when done
3. Phase 2 status opens: "Building strategy..." → shows positioning when done
4. Phase 3 status opens: "Creating content..." → shows each channel as it completes
5. Phase 4 status opens: "Evaluating quality..." → shows scores, revisions if any
6. Campaign dashboard appears with all content + download button

## Configuration (config.py)

```python
GEMINI_MODEL = "gemini-2.5-flash"
CONTENT_TEMPERATURE = 0.7
ANALYSIS_TEMPERATURE = 0.3
SCRAPE_TIMEOUT = 10
LLM_TIMEOUT = 30
REVISION_THRESHOLD = 7  # score below this triggers revision
MAX_REVISIONS = 1
CAMPAIGN_GOALS = ["Product Launch", "Brand Awareness", "Lead Generation", "Engagement"]
```

## Key Design Decisions

### Why plain Python orchestration (no LangChain/LangGraph)?
- No framework bloat — every line of logic is visible and debuggable
- The pipeline is clear enough that a framework adds complexity without value
- We learn more about agent patterns by building them ourselves
- Fewer dependencies, simpler setup

### Why sequential content generation (not parallel)?
- Gemini Flash is fast enough (~2-3s per call) that parallel adds marginal benefit
- Avoids rate limiting complexity
- Simpler error handling
- Total content phase: ~15-20 seconds, acceptable for the UX

### Why max 1 revision pass?
- Diminishing returns after first revision
- Avoids infinite loops and unpredictable latency
- First revision typically catches 80% of issues
- User sees both scores (original + revised) for transparency

### Why Pydantic models?
- Structured data validation at every boundary
- Clear contracts between agents
- Makes JSON mode parsing reliable
- Self-documenting data shapes

### Why scraping over user-provided info?
- This is what makes the agent agentic — it gathers its own evidence
- Real website content reveals actual positioning, not aspirational descriptions
- Competitors' real messaging is more valuable than guesses
- Falls back gracefully to user description if scraping fails

## Error Handling

- **Scraping fails**: Fall back to user-provided product description, warn user
- **Competitor scrape fails**: Skip that competitor, continue with others, warn user
- **Gemini call fails**: 1 retry, then show error for that phase, allow user to retry
- **JSON parsing fails**: Retry with stricter prompt, fall back to text extraction
- **All competitors fail**: Skip competitive analysis, proceed with product-only positioning

## Estimated LLM Calls

| Phase | Calls | Purpose |
|-------|-------|---------|
| Research | 2 | Product brief + competitive analysis |
| Strategy | 2 | Positioning + voice guide |
| Content | 5 | One per channel |
| Evaluation | 1 | All pieces evaluated in single call |
| Revisions | 0-5 | Only for pieces below threshold |
| **Total** | **10-15** | ~30-45 seconds end-to-end |
