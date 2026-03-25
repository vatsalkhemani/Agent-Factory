from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import ProductBrief, CompetitiveAnalysis, BrandPositioning, BrandVoiceGuide
from prompts.strategy_prompts import positioning_prompt, voice_guide_prompt


def build_positioning(
    client: GeminiClient,
    product_brief: ProductBrief,
    competitive_analysis: CompetitiveAnalysis,
    target_audience: str,
    campaign_goal: str,
) -> BrandPositioning:
    brief_text = product_brief.model_dump_json(indent=2)
    analysis_text = competitive_analysis.model_dump_json(indent=2)

    system, prompt = positioning_prompt(brief_text, analysis_text, target_audience, campaign_goal)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)
    return BrandPositioning(**data)


def build_voice_guide(
    client: GeminiClient,
    product_brief: ProductBrief,
    positioning: BrandPositioning,
    target_audience: str,
) -> BrandVoiceGuide:
    brief_text = product_brief.model_dump_json(indent=2)
    positioning_text = positioning.model_dump_json(indent=2)

    system, prompt = voice_guide_prompt(brief_text, positioning_text, target_audience)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)
    return BrandVoiceGuide(**data)
