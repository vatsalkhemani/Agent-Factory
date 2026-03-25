import json

from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE, CONTENT_TEMPERATURE, REVISION_THRESHOLD, MAX_REVISIONS
from models import (
    BrandPositioning, BrandVoiceGuide, CampaignContent,
    EvaluationResult, ContentScore,
)
from prompts.evaluator_prompts import evaluation_prompt, revision_prompt


def _format_content_for_eval(content: CampaignContent) -> str:
    sections = []

    for i, post in enumerate(content.linkedin_posts, 1):
        sections.append(f"### linkedin_post_{i}\nHook: {post.hook}\nBody: {post.body}\nCTA: {post.cta}")

    sections.append(f"### twitter_thread\n" + "\n".join(f"Tweet {i+1}: {t}" for i, t in enumerate(content.twitter_thread.tweets)))

    for i, email in enumerate(content.email_sequence.emails, 1):
        sections.append(f"### email_{i}\nSubject: {email.subject}\nPreview: {email.preview_text}\nBody: {email.body}\nCTA: {email.cta}")

    sections.append(f"### blog_outline\nTitle: {content.blog_outline.title}\nIntro: {content.blog_outline.intro}\n" +
                     "\n".join(f"Section: {s.heading} - {s.summary}" for s in content.blog_outline.sections) +
                     f"\nConclusion: {content.blog_outline.conclusion}")

    for i, ad in enumerate(content.ad_copies, 1):
        sections.append(f"### ad_copy_{i}\nHeadline: {ad.headline}\nBody: {ad.body}\nCTA: {ad.cta}")

    return "\n\n".join(sections)


def evaluate_campaign(
    client: GeminiClient,
    content: CampaignContent,
    positioning: BrandPositioning,
    voice: BrandVoiceGuide,
) -> EvaluationResult:
    content_text = _format_content_for_eval(content)
    voice_text = voice.model_dump_json(indent=2)
    positioning_text = positioning.model_dump_json(indent=2)

    system, prompt = evaluation_prompt(voice_text, positioning_text, content_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    scores = [ContentScore(**s) for s in data["scores"]]
    return EvaluationResult(scores=scores, overall_feedback=data.get("overall_feedback", ""))


def _get_piece_content(content: CampaignContent, piece_name: str) -> str:
    if piece_name.startswith("linkedin_post_"):
        idx = int(piece_name.split("_")[-1]) - 1
        if idx < len(content.linkedin_posts):
            return content.linkedin_posts[idx].model_dump_json(indent=2)
    elif piece_name == "twitter_thread":
        return content.twitter_thread.model_dump_json(indent=2)
    elif piece_name.startswith("email_"):
        idx = int(piece_name.split("_")[-1]) - 1
        if idx < len(content.email_sequence.emails):
            return content.email_sequence.emails[idx].model_dump_json(indent=2)
    elif piece_name == "blog_outline":
        return content.blog_outline.model_dump_json(indent=2)
    elif piece_name.startswith("ad_copy_"):
        idx = int(piece_name.split("_")[-1]) - 1
        if idx < len(content.ad_copies):
            return content.ad_copies[idx].model_dump_json(indent=2)
    return ""


def _apply_revision(content: CampaignContent, piece_name: str, revised_json: dict) -> None:
    try:
        if piece_name.startswith("linkedin_post_"):
            idx = int(piece_name.split("_")[-1]) - 1
            if idx < len(content.linkedin_posts):
                for key, val in revised_json.items():
                    if hasattr(content.linkedin_posts[idx], key):
                        setattr(content.linkedin_posts[idx], key, val)
        elif piece_name == "twitter_thread":
            if "tweets" in revised_json:
                content.twitter_thread.tweets = revised_json["tweets"]
        elif piece_name.startswith("email_"):
            idx = int(piece_name.split("_")[-1]) - 1
            if idx < len(content.email_sequence.emails):
                for key, val in revised_json.items():
                    if hasattr(content.email_sequence.emails[idx], key):
                        setattr(content.email_sequence.emails[idx], key, val)
        elif piece_name == "blog_outline":
            for key, val in revised_json.items():
                if hasattr(content.blog_outline, key):
                    setattr(content.blog_outline, key, val)
        elif piece_name.startswith("ad_copy_"):
            idx = int(piece_name.split("_")[-1]) - 1
            if idx < len(content.ad_copies):
                for key, val in revised_json.items():
                    if hasattr(content.ad_copies[idx], key):
                        setattr(content.ad_copies[idx], key, val)
    except (IndexError, ValueError):
        pass


def revise_weak_pieces(
    client: GeminiClient,
    content: CampaignContent,
    evaluation: EvaluationResult,
    positioning: BrandPositioning,
    voice: BrandVoiceGuide,
    on_progress=None,
) -> tuple[CampaignContent, EvaluationResult]:
    weak = [s for s in evaluation.scores if s.needs_revision]
    if not weak:
        return content, evaluation

    voice_text = voice.model_dump_json(indent=2)
    positioning_text = positioning.model_dump_json(indent=2)

    for score in weak:
        if on_progress:
            on_progress(f"Revising {score.piece_name}...")

        original = _get_piece_content(content, score.piece_name)
        if not original:
            continue

        system, prompt = revision_prompt(
            score.piece_name, original, score.feedback, voice_text, positioning_text,
        )
        revised = client.generate_json(prompt, system, temperature=CONTENT_TEMPERATURE)
        _apply_revision(content, score.piece_name, revised)

    # Re-evaluate after revisions
    if on_progress:
        on_progress("Re-evaluating revised content...")
    new_eval = evaluate_campaign(client, content, positioning, voice)

    return content, new_eval
