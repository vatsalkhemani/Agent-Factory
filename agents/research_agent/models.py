from pydantic import BaseModel, field_validator


def _coerce_to_str(v):
    """Coerce dicts/lists to string -- handles Gemini returning structured objects for string fields."""
    if isinstance(v, dict):
        parts = [str(val) for val in v.values() if val]
        return " -- ".join(parts)
    if isinstance(v, list):
        return ", ".join(str(i) for i in v)
    return v


# --- Search Models ---

class SearchQuery(BaseModel):
    query: str
    rationale: str

    @field_validator("query", "rationale", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class SearchPlan(BaseModel):
    queries: list[SearchQuery]
    focus_areas: list[str]


class ScrapedPage(BaseModel):
    url: str
    title: str
    content: str
    success: bool
    error: str = ""


class SearchResult(BaseModel):
    query: str
    url: str
    title: str
    snippet: str
    content: str  # scraped body text (truncated)
    success: bool


# --- Extraction Models ---

class ExtractedFact(BaseModel):
    claim: str
    source_url: str
    confidence: str  # "high", "medium", "low"

    @field_validator("claim", "confidence", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class ExtractionResult(BaseModel):
    facts: list[ExtractedFact]
    key_themes: list[str]


# --- Evaluation Models ---

class CoverageEvaluation(BaseModel):
    coverage_score: int  # 1-10
    well_covered: list[str]
    gaps: list[str]
    should_continue: bool
    next_focus: str  # what to search for next, if continuing

    @field_validator("next_focus", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Reasoning Trace ---

class ReasoningStep(BaseModel):
    iteration: int
    phase: str  # "plan", "search", "extract", "evaluate"
    summary: str
    detail: str

    @field_validator("summary", "detail", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Report Models ---

class SourceCitation(BaseModel):
    url: str
    title: str
    used_for: str

    @field_validator("used_for", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class ReportSection(BaseModel):
    heading: str
    content: str
    supporting_sources: list[str]  # URLs

    @field_validator("heading", "content", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class ResearchReport(BaseModel):
    question: str
    executive_summary: str
    sections: list[ReportSection]
    key_findings: list[str]
    sources: list[SourceCitation]
    confidence_level: str  # "high", "medium", "low"
    reasoning_trace: list[ReasoningStep]

    @field_validator("executive_summary", "confidence_level", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)
