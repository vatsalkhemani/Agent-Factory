from gemini_client import GeminiClient
from config import CONTENT_TEMPERATURE
from models import (
    BrandPositioning, BrandVoiceGuide, ProductBrief,
    LinkedInPost, TwitterThread, Email, EmailSequence, BlogOutline, AdCopy, CampaignContent,
)
from prompts.content_prompts import (
    linkedin_prompt, twitter_prompt, email_prompt, blog_prompt, ad_copy_prompt,
)


def _unwrap_list(data, *keys):
    """Extract a list from a dict that Gemini may have wrapped in various keys."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            if key in data:
                return data[key] if isinstance(data[key], list) else [data[key]]
        # If it's a dict with numeric-ish or arbitrary keys, try values
        return list(data.values()) if data else []
    return [data]


def _context_args(brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> dict:
    return dict(
        product_brief=brief.model_dump_json(indent=2),
        positioning=positioning.model_dump_json(indent=2),
        voice_guide=voice.model_dump_json(indent=2),
        target_audience=audience,
        campaign_goal=goal,
    )


def generate_linkedin(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> list[LinkedInPost]:
    system, prompt = linkedin_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    items = _unwrap_list(data, "posts", "linkedin_posts")
    return [LinkedInPost(**post) for post in items]


def generate_twitter(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> TwitterThread:
    system, prompt = twitter_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    if isinstance(data, dict) and "tweets" in data:
        tweets = data["tweets"]
    elif isinstance(data, list):
        tweets = data
    else:
        tweets = list(data.values())
    # Coerce tweet items to strings if they're dicts
    tweets = [t if isinstance(t, str) else t.get("text", str(t)) for t in tweets]
    return TwitterThread(tweets=tweets)


def generate_emails(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> EmailSequence:
    system, prompt = email_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    if isinstance(data, dict) and "emails" in data:
        emails = data["emails"]
    elif isinstance(data, list):
        emails = data
    else:
        emails = list(data.values())
    return EmailSequence(emails=[Email(**e) for e in emails])


def generate_blog(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> BlogOutline:
    system, prompt = blog_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    # Handle sections that might have nested key_points as dicts
    if "sections" in data:
        for section in data["sections"]:
            if "key_points" in section:
                section["key_points"] = [
                    p if isinstance(p, str) else str(p) for p in section["key_points"]
                ]
    return BlogOutline(**data)


def generate_ads(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> list[AdCopy]:
    system, prompt = ad_copy_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    items = _unwrap_list(data, "ads", "ad_copies", "variations")
    return [AdCopy(**ad) for ad in items]


def generate_all_content(
    client: GeminiClient,
    brief: ProductBrief,
    positioning: BrandPositioning,
    voice: BrandVoiceGuide,
    audience: str,
    goal: str,
    on_progress=None,
) -> CampaignContent:
    args = (client, brief, positioning, voice, audience, goal)

    if on_progress:
        on_progress("Creating LinkedIn posts...")
    linkedin = generate_linkedin(*args)

    if on_progress:
        on_progress("Creating Twitter thread...")
    twitter = generate_twitter(*args)

    if on_progress:
        on_progress("Creating email sequence...")
    emails = generate_emails(*args)

    if on_progress:
        on_progress("Creating blog outline...")
    blog = generate_blog(*args)

    if on_progress:
        on_progress("Creating ad copy...")
    ads = generate_ads(*args)

    return CampaignContent(
        linkedin_posts=linkedin,
        twitter_thread=twitter,
        email_sequence=emails,
        blog_outline=blog,
        ad_copies=ads,
    )
