# Research Agent -- Technical Requirements Document

## Architecture Overview

The Research Agent uses an orchestrator-driven iterative loop pattern. Unlike the Marketing Agent's linear pipeline, this agent loops dynamically -- the number of iterations depends on the agent's own evaluation of coverage quality.

```
User Question
    |
    v
[ResearchOrchestrator]
    |
    +---> Iteration 1
    |       Planner -> Search -> Extractor -> Evaluator
    |       (evaluator: coverage 5/10, gaps found)
    |
    +---> Iteration 2
    |       Replanner -> Search -> Extractor -> Evaluator
    |       (evaluator: coverage 7/10, minor gaps)
    |
    +---> Iteration 3
    |       Replanner -> Search -> Extractor -> Evaluator
    |       (evaluator: coverage 9/10, sufficient)
    |
    +---> Synthesizer -> ResearchReport
```

## File Structure

```
research_agent/
  app.py              (212 lines)  - Streamlit UI, progress display, export
  orchestrator.py     (171 lines)  - Core research loop with convergence logic
  models.py           (131 lines)  - 12 Pydantic models
  config.py           (18 lines)   - All constants and presets
  gemini_client.py    (125 lines)  - LLM wrapper with retry + JSON parsing
  search.py           (80 lines)   - DuckDuckGo search + BeautifulSoup scraping
  agents/
    planner_agent.py  (32 lines)   - Initial plan + replan
    extractor_agent.py(53 lines)   - Fact extraction from search results
    evaluator_agent.py(32 lines)   - Coverage scoring + gap identification
    synthesizer_agent.py(64 lines) - Final report generation
  prompts/
    planner_prompts.py   (44 lines)
    extractor_prompts.py (29 lines)
    evaluator_prompts.py (25 lines)
    synthesizer_prompts.py(34 lines)
```

Total: ~1,050 lines across 16 files.

## Core Loop Logic (orchestrator.py)

The orchestrator maintains state across iterations:

- `all_facts: list[ExtractedFact]` -- accumulated knowledge base (capped at 30 to prevent token overflow)
- `reasoning_trace: list[ReasoningStep]` -- full decision log for UI display
- `gaps: list[str]` -- current knowledge gaps from evaluator
- `next_focus: str` -- evaluator's suggested next search direction

**Convergence rules:**
- Minimum 2 iterations always run (MIN_ITERATIONS)
- After minimum: stop if coverage_score >= 8 (COVERAGE_THRESHOLD)
- After minimum: stop if evaluator sets should_continue = False
- Hard ceiling: MAX_ITERATIONS (configurable via depth preset: 2/3/4)

**Fact overflow prevention:**
- When `all_facts` exceeds MAX_FACTS (30), older facts are trimmed
- Keeps most recent facts since they're more targeted (from gap-filling searches)

## Data Flow

```
Question -> PlannerAgent -> SearchPlan (3 queries + rationale)
                                |
                    For each query:
                        DuckDuckGo search -> 3 results per query
                        BeautifulSoup scrape -> page content (2000 char cap)
                                |
                        ExtractorAgent -> 4-8 new ExtractedFacts per round
                                |
                        EvaluatorAgent -> CoverageEvaluation
                            (score, gaps, should_continue, next_focus)
                                |
                        If continuing: gaps + next_focus -> PlannerAgent.replan()
                                |
                        If done: all_facts -> SynthesizerAgent -> ResearchReport
```

## Key Design Decisions

### 1. DuckDuckGo over Tavily
- Free, no API key, zero setup friction
- `duckduckgo-search` package handles the API
- Scrape results with BeautifulSoup for richer content; fall back to DDG snippets if scraping fails
- 1-second delay between searches to avoid rate limiting

### 2. Coverage-based convergence (not fixed iterations)
- The evaluator LLM scores coverage 1-10 and explicitly decides whether to continue
- This makes the agent genuinely autonomous -- it stops when it has enough, not after N loops
- MIN_ITERATIONS ensures at least 2 rounds (prevents premature stopping)

### 3. Fact deduplication via context
- The extractor receives ALL existing facts and is instructed to return only NEW ones
- This prevents the same fact from appearing multiple times across iterations
- Cheaper than embedding-based deduplication and works well enough

### 4. Separated reasoning trace
- Every phase logs a ReasoningStep with iteration, phase, summary, and detail
- This is passed through to the final report and displayed in the UI
- Makes the agent's thinking transparent -- users can see WHY it searched what it searched

### 5. No LangChain/LangGraph
- Plain Python orchestration with callbacks for UI updates
- All logic is visible and debuggable
- Same pattern as the Marketing Agent

## Error Handling

| Failure | Recovery |
|---------|----------|
| DuckDuckGo search fails | Return empty results, log the error, continue with other queries |
| Page scrape fails | Fall back to DDG snippet (always have some content) |
| LLM returns bad JSON | 3-strategy JSON parsing + 3 retries with stricter prompts |
| LLM rate limited | Exponential backoff: 30s, 60s, 90s (max 4 attempts) |
| Zero facts extracted in a round | Evaluator sees low coverage, triggers replan |
| All searches fail in an iteration | Break loop, synthesize with whatever facts we have |

## Pydantic Models

12 models enforce structure at every boundary:

- **Search**: SearchQuery, SearchPlan, ScrapedPage, SearchResult
- **Extraction**: ExtractedFact (claim + source + confidence), ExtractionResult
- **Evaluation**: CoverageEvaluation (score + gaps + should_continue + next_focus)
- **Trace**: ReasoningStep (iteration + phase + summary + detail)
- **Report**: SourceCitation, ReportSection, ResearchReport

All string fields have `_coerce_to_str` validators to handle Gemini returning dicts/lists for string fields.

## UI Architecture

**Sidebar**: Question input + depth slider (Quick/Standard/Deep) + Start button

**During research**: One `st.status()` per iteration, showing live reasoning steps. Previous iterations collapse when next starts.

**After completion**:
- Metrics row: Sources count, Key Findings count, Research Loops count, Confidence level
- Executive summary as info box
- Three tabs: Report (sections + findings), Sources (numbered with descriptions), Reasoning Trace (expandable per-step)
- Download button for markdown export

**Session state**: `st.session_state["report"]` persists the ResearchReport across Streamlit reruns.

## Configuration

All constants in config.py:
- `GEMINI_MODEL`: gemini-3.1-flash-lite-preview
- `MAX_ITERATIONS`: 4 (hard ceiling)
- `MIN_ITERATIONS`: 2 (minimum before convergence check)
- `COVERAGE_THRESHOLD`: 8 (score to stop)
- `SEARCH_RESULTS_PER_QUERY`: 3
- `QUERIES_PER_ITERATION`: 3
- `MAX_CONTENT_CHARS`: 2000 (per scraped page)
- `MAX_FACTS`: 30 (prevent token overflow)
- `SEARCH_DELAY`: 1.0s (between DDG searches)
- `DEPTH_PRESETS`: Quick=2, Standard=3, Deep=4

## Dependencies

- streamlit, google-genai, duckduckgo-search, beautifulsoup4, requests, pydantic, python-dotenv
- No additional API keys beyond GEMINI_API_KEY
