from pydantic import BaseModel, field_validator


def _coerce_to_str(v):
    """Coerce dicts/lists to string — handles Gemini returning structured objects for string fields."""
    if isinstance(v, dict):
        parts = [str(val) for val in v.values() if val]
        return " — ".join(parts)
    if isinstance(v, list):
        return ", ".join(str(i) for i in v)
    return v


# --- Research Models ---

class ScrapedPage(BaseModel):
    url: str
    title: str
    meta_description: str
    headings: list[str]
    paragraphs: list[str]
    success: bool
    error: str = ""


class ProductBrief(BaseModel):
    summary: str
    features: list[str]
    value_propositions: list[str]
    audience_signals: list[str]
    messaging_tone: str


class CompetitorProfile(BaseModel):
    url: str
    name: str
    positioning: str
    strengths: list[str]
    messaging_approach: str


class CompetitiveAnalysis(BaseModel):
    competitors: list[CompetitorProfile]
    gaps: list[str]
    opportunities: list[str]


# --- Strategy Models ---

class BrandPositioning(BaseModel):
    statement: str
    key_messages: list[str]
    differentiators: list[str]
    proof_points: list[str]


class BrandVoiceGuide(BaseModel):
    tone_attributes: list[str]
    dos: list[str]
    donts: list[str]
    example_phrases: list[str]
    words_to_avoid: list[str]


# --- Content Models ---

class LinkedInPost(BaseModel):
    hook: str
    body: str
    cta: str
    angle: str

    @field_validator("hook", "body", "cta", "angle", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class TwitterThread(BaseModel):
    tweets: list[str]


class Email(BaseModel):
    subject: str
    preview_text: str
    body: str
    cta: str

    @field_validator("subject", "preview_text", "body", "cta", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class EmailSequence(BaseModel):
    emails: list[Email]


class BlogSection(BaseModel):
    heading: str
    key_points: list[str]
    summary: str

    @field_validator("heading", "summary", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class BlogOutline(BaseModel):
    title: str
    intro: str
    sections: list[BlogSection]
    conclusion: str

    @field_validator("title", "intro", "conclusion", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class AdCopy(BaseModel):
    headline: str
    body: str
    cta: str

    @field_validator("headline", "body", "cta", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return _coerce_to_str(v)


class CampaignContent(BaseModel):
    linkedin_posts: list[LinkedInPost]
    twitter_thread: TwitterThread
    email_sequence: EmailSequence
    blog_outline: BlogOutline
    ad_copies: list[AdCopy]


# --- Evaluation Models ---

class ContentScore(BaseModel):
    piece_name: str
    voice_score: int
    coherence_score: int
    channel_score: int
    feedback: str
    needs_revision: bool


class EvaluationResult(BaseModel):
    scores: list[ContentScore]
    overall_feedback: str


# --- Campaign Package ---

class CampaignPackage(BaseModel):
    product_brief: ProductBrief
    competitive_analysis: CompetitiveAnalysis
    positioning: BrandPositioning
    voice_guide: BrandVoiceGuide
    content: CampaignContent
    evaluation: EvaluationResult
