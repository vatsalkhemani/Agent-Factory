from pydantic import BaseModel, field_validator
from typing import Optional


def _coerce_to_str(v):
    if isinstance(v, dict):
        parts = [str(val) for val in v.values() if val]
        return " -- ".join(parts)
    if isinstance(v, list):
        return ", ".join(str(i) for i in v)
    return v


# --- Profiling Models ---

class ColumnProfile(BaseModel):
    name: str
    dtype: str  # "numeric", "categorical", "datetime", "text"
    non_null_count: int
    null_count: int
    unique_count: int
    sample_values: list[str]
    # Numeric only
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    # Categorical only
    top_values: Optional[list[str]] = None
    top_counts: Optional[list[int]] = None


class DataProfile(BaseModel):
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    data_quality_notes: list[str]
    sampled: bool = False


# --- Hypothesis Models ---

class AnalysisRequest(BaseModel):
    tool: str  # one of the toolkit method names
    params: dict
    rationale: str

    @field_validator("rationale", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class Hypothesis(BaseModel):
    statement: str
    analyses: list[AnalysisRequest]

    @field_validator("statement", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class AnalysisPlan(BaseModel):
    hypotheses: list[Hypothesis]


# --- Results Models ---

class AnalysisResult(BaseModel):
    hypothesis: str
    tool: str
    params: dict
    result_summary: str
    raw_data: dict
    success: bool
    error: str = ""

    @field_validator("result_summary", "error", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class ChartSpec(BaseModel):
    chart_type: str  # "bar", "scatter", "line", "histogram", "box", "heatmap", "pie"
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    title: str
    params: dict = {}

    @field_validator("title", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class Finding(BaseModel):
    title: str
    description: str
    importance: str  # "high", "medium", "low"
    supporting_data: str
    chart_spec: Optional[ChartSpec] = None

    @field_validator("title", "description", "importance", "supporting_data", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Deep Dive Models ---

class DeepDiveRequest(BaseModel):
    finding_index: int
    additional_analyses: list[AnalysisRequest]


# --- Report Models ---

class AnalysisReport(BaseModel):
    dataset_summary: str
    key_findings: list[Finding]
    narrative: str
    methodology_notes: list[str]
    data_profile: DataProfile

    @field_validator("dataset_summary", "narrative", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)
