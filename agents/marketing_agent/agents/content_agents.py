from gemini_client import GeminiClient
from config import CONTENT_TEMPERATURE
from models import (
    BrandPositioning, BrandVoiceGuide, ProductBrief,
    LinkedInPost, TwitterThread, EmailSequence, BlogOutline, AdCopy, CampaignContent,
)
from prompts.content_prompts import (
    linkedin_prompt, twitter_prompt, email_prompt, blog_prompt, ad_copy_prompt,
)


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
    if isinstance(data, dict) and "posts" in data:
        data = data["posts"]
    if isinstance(data, dict):
        data = list(data.values())
    return [LinkedInPost(**post) for post in data]


def generate_twitter(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> TwitterThread:
    system, prompt = twitter_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    return TwitterThread(**data)


def generate_emails(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> EmailSequence:
    system, prompt = email_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    return EmailSequence(**data)


def generate_blog(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> BlogOutline:
    system, prompt = blog_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    return BlogOutline(**data)


def generate_ads(client: GeminiClient, brief: ProductBrief, positioning: BrandPositioning, voice: BrandVoiceGuide, audience: str, goal: str) -> list[AdCopy]:
    system, prompt = ad_copy_prompt(**_context_args(brief, positioning, voice, audience, goal))
    data = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
    if isinstance(data, dict) and "ads" in data:
        data = data["ads"]
    if isinstance(data, dict):
        data = list(data.values())
    return [AdCopy(**ad) for ad in data]


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
