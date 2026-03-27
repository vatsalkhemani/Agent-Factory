from pydantic import BaseModel, field_validator


def _coerce_to_str(v):
    """Coerce dicts/lists to string -- handles Gemini returning structured objects for string fields."""
    if isinstance(v, dict):
        parts = [str(val) for val in v.values() if val]
        return " -- ".join(parts)
    if isinstance(v, list):
        return ", ".join(str(i) for i in v)
    return v


# --- Parsing Models ---

class Experience(BaseModel):
    title: str
    company: str
    duration: str
    highlights: list[str]

    @field_validator("title", "company", "duration", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class ParsedJob(BaseModel):
    title: str
    company_name: str
    company_url: str  # best guess from JD, or ""
    location: str
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    experience_level: str
    key_phrases: list[str]  # ATS-relevant phrases verbatim from JD

    @field_validator("title", "company_name", "company_url", "location", "experience_level", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class ParsedResume(BaseModel):
    name: str
    current_title: str
    skills: list[str]
    experiences: list[Experience]
    education: list[str]
    summary: str

    @field_validator("name", "current_title", "summary", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Analysis Models ---

class SkillMapping(BaseModel):
    resume_skill: str
    maps_to: str  # JD requirement it relates to
    strength: str  # "direct", "adjacent", "stretch"

    @field_validator("resume_skill", "maps_to", "strength", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class GapAnalysis(BaseModel):
    matching_skills: list[str]
    missing_skills: list[str]
    transferable_skills: list[SkillMapping]
    experience_alignment: str  # "strong", "moderate", "weak"
    priority_areas: list[str]  # what to emphasize in tailoring

    @field_validator("experience_alignment", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class CompanyIntel(BaseModel):
    company_name: str
    industry: str
    mission_or_values: str
    recent_news: list[str]
    culture_signals: list[str]
    talking_points: list[str]  # things to weave into cover letter

    @field_validator("company_name", "industry", "mission_or_values", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Output Models ---

class ExperienceBullets(BaseModel):
    company: str
    title: str
    bullets: list[str]

    @field_validator("company", "title", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class TailoredResume(BaseModel):
    summary: str
    skills_section: list[str]
    experience_bullets: list[ExperienceBullets]
    keywords_added: list[str]

    @field_validator("summary", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class CoverLetter(BaseModel):
    opening: str
    body_paragraphs: list[str]
    closing: str
    full_text: str

    @field_validator("opening", "closing", "full_text", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Evaluation Models ---

class ATSScore(BaseModel):
    keyword_match_score: int  # 1-10
    format_score: int  # 1-10
    relevance_score: int  # 1-10
    overall_score: int  # 1-10
    missing_keywords: list[str]
    feedback: str
    needs_revision: bool

    @field_validator("feedback", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


# --- Final Package ---

class ApplicationPackage(BaseModel):
    parsed_job: ParsedJob
    parsed_resume: ParsedResume
    gap_analysis: GapAnalysis
    company_intel: CompanyIntel
    tailored_resume: TailoredResume
    cover_letter: CoverLetter
    original_resume_text: str
    ats_score: ATSScore
