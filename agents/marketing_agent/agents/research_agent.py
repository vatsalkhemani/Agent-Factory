import json

from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import ProductBrief, CompetitiveAnalysis, ScrapedPage
from prompts.research_prompts import product_brief_prompt, competitive_analysis_prompt


def build_product_brief(client: GeminiClient, scraped: ScrapedPage, user_description: str, target_audience: str) -> ProductBrief:
    scraped_text = f"""URL: {scraped.url}
Title: {scraped.title}
Meta Description: {scraped.meta_description}
Headings: {json.dumps(scraped.headings)}
Content Paragraphs: {json.dumps(scraped.paragraphs[:20])}"""

    if not scraped.success:
        scraped_text = f"(Scraping failed: {scraped.error})\nUsing user description only."

    system, prompt = product_brief_prompt(scraped_text, user_description, target_audience)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)
    return ProductBrief(**data)


def build_competitive_analysis(client: GeminiClient, competitors: list[ScrapedPage], product_brief: ProductBrief) -> CompetitiveAnalysis:
    competitors_text = ""
    for comp in competitors:
        if comp.success:
            competitors_text += f"""
--- Competitor: {comp.url} ---
Title: {comp.title}
Meta Description: {comp.meta_description}
Headings: {json.dumps(comp.headings)}
Content: {json.dumps(comp.paragraphs[:15])}
"""
        else:
            competitors_text += f"\n--- Competitor: {comp.url} ---\n(Scraping failed: {comp.error})\n"

    brief_text = product_brief.model_dump_json(indent=2)
    system, prompt = competitive_analysis_prompt(competitors_text, brief_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)
    return CompetitiveAnalysis(**data)
