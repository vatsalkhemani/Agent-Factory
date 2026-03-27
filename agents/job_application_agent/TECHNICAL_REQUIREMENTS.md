# Job Application Agent -- Technical Requirements Document

## Architecture Overview

The Job Application Agent uses a linear pipeline with a conditional revision loop at the end. It follows the same orchestrator pattern as the Marketing Agent but with 7 phases instead of 5.

```
JD Text + Resume Text
    |
    v
[ApplicationOrchestrator]
    |
    +---> Phase 1: Parse (JD + Resume -> structured data)
    +---> Phase 2: Gap Analysis (matching/missing/transferable skills)
    +---> Phase 3: Company Research (scrape + search -> intel)
    +---> Phase 4: Tailor Resume (rewrite bullets + summary)
    +---> Phase 5: Cover Letter (personalized with company research)
    +---> Phase 6: ATS Evaluation (score on 3 criteria)
    +---> Phase 7: Revision (conditional, if score < 7)
    |
    v
ApplicationPackage
```

## File Structure

```
job_application_agent/
  app.py                 (271 lines) - Streamlit UI with side-by-side resume comparison
  orchestrator.py        (144 lines) - 7-phase pipeline driver
  models.py              (163 lines) - 15 Pydantic models
  config.py              (10 lines)  - Constants
  gemini_client.py       (122 lines) - LLM wrapper with retry + JSON parsing
  search.py              (80 lines)  - DDG search + BeautifulSoup for company research
  agents/
    parser_agent.py      (26 lines)  - Parse JD and resume
    gap_agent.py         (23 lines)  - Skill gap analysis
    researcher_agent.py  (17 lines)  - Company research coordination
    tailor_agent.py      (57 lines)  - Resume tailoring + revision
    cover_letter_agent.py(37 lines)  - Cover letter writing + revision
    evaluator_agent.py   (28 lines)  - ATS scoring
  prompts/
    parser_prompts.py    (47 lines)  - JD + resume parsing prompts
    gap_prompts.py       (24 lines)  - Gap analysis prompt
    researcher_prompts.py(19 lines)  - Company research prompt
    tailor_prompts.py    (66 lines)  - Tailoring + revision prompts
    cover_letter_prompts.py(62 lines)- Cover letter + revision prompts
    evaluator_prompts.py (44 lines)  - ATS evaluation prompt
```

Total: ~1,240 lines across 20 files.

## Data Flow

```
JD Text ---------> parse_job() ---------> ParsedJob
                                              |
Resume Text -----> parse_resume() ------> ParsedResume
                                              |
ParsedJob + ParsedResume -----> analyze_gaps() -> GapAnalysis
                                              |
ParsedJob.company_name -----> research_company() -> CompanyIntel
  (scrape website + DDG search)                    |
                                              |
All context -----> tailor_resume() ---------> TailoredResume
                                              |
All context -----> write_cover_letter() ----> CoverLetter
                                              |
Resume + CL + Job -----> evaluate_ats() ----> ATSScore
                                              |
                         if score < 7: revise both, re-evaluate
                                              |
                         -----> ApplicationPackage
```

## Key Design Decisions

### 1. Text input (no PDF parsing)
- Paste-based input keeps the agent simple and dependency-light
- No need for PyPDF2, pdfplumber, or OCR libraries
- Users can easily paste from any resume format
- Focus is on the agent's intelligence, not file parsing

### 2. ATS scoring with weighted criteria
- Keyword Match (40%): Overlap between JD key_phrases and tailored resume text
- Relevance (40%): How well the content aligns with the role
- Format (20%): Clean structure for ATS parsing
- Overall = weighted combination
- `needs_revision` = True when overall < 7

### 3. Company URL extraction from JD
- The parser LLM is instructed to guess the company website URL from the JD text
- Common pattern: company name -> https://companyname.com
- If it can't determine the URL, falls back to DDG search only
- Scrapes both the homepage and /about page for richer intel

### 4. Company research dual strategy
- Strategy 1: Scrape company website + /about page (if URL available)
- Strategy 2: DDG search for "{company} mission values culture" and "{company} recent news"
- Both strategies run; results are combined before LLM synthesis
- If both fail, CompanyIntel is still generated with minimal data

### 5. Conditional revision (not always)
- Revision only triggers if `overall_score < 7`
- Max 1 revision pass (same as Marketing Agent pattern)
- Both resume and cover letter are revised based on the same ATS feedback
- Re-evaluation after revision to track improvement

### 6. Authentic tailoring (never fabricate)
- The tailor prompt explicitly forbids fabricating experience or metrics
- "Reframe, don't fabricate" is the core principle
- If the candidate managed 3 people, it stays 3 people
- Keywords are woven in naturally, not keyword-stuffed

## Pydantic Models

15 models across 4 categories:

**Parsing**: ParsedJob (with key_phrases), ParsedResume, Experience
**Analysis**: SkillMapping, GapAnalysis, CompanyIntel
**Output**: ExperienceBullets, TailoredResume, CoverLetter
**Evaluation**: ATSScore, ApplicationPackage

All string fields have `_coerce_to_str` validators for Gemini response robustness.

## UI Architecture

**Sidebar**: Two large text areas (JD + Resume) + "Analyze & Tailor" button

**During processing**: `st.status()` per phase with progress messages

**After completion**:
- Metrics row: ATS Score, Keyword Match, Relevance, Alignment
- 5 tabs:
  - **Gap Analysis**: Two columns with color-coded skill tags (green=match, red=gap, yellow=transferable)
  - **Tailored Resume**: Side-by-side (original left, tailored right with expandable experience sections)
  - **Cover Letter**: Full text + expandable structure breakdown
  - **Company Intel**: Industry, mission, culture signals, recent news, talking points
  - **ATS Evaluation**: Score badges, feedback text, missing keywords list
- Download buttons: Tailored resume + cover letter as separate markdown files

## Error Handling

| Failure | Recovery |
|---------|----------|
| Company website unreachable | Fall back to DDG search only |
| DDG search fails | CompanyIntel generated with minimal data |
| JD too short or unusual format | Parser extracts what it can, empty fields handled gracefully |
| Resume unusual format | Parser extracts what it can |
| LLM bad JSON | 3-strategy parsing + 3 retries |
| LLM rate limited | Exponential backoff up to 90s |

## Configuration

- `GEMINI_MODEL`: gemini-2.5-flash-lite
- `ANALYSIS_TEMPERATURE`: 0.3 (parsing, evaluation)
- `CREATIVE_TEMPERATURE`: 0.7 (tailoring, cover letter)
- `REVISION_THRESHOLD`: 7 (ATS score below this triggers revision)
- `MAX_REVISIONS`: 1
- `SCRAPE_TIMEOUT`: 8s
- `SEARCH_DELAY`: 1.0s between DDG searches

## Dependencies

- streamlit, google-genai, duckduckgo-search, beautifulsoup4, requests, pydantic, python-dotenv
- No additional API keys beyond GEMINI_API_KEY
