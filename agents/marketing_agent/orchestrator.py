from gemini_client import GeminiClient
from scraper import scrape_url
from models import CampaignPackage, ScrapedPage
from agents.research_agent import build_product_brief, build_competitive_analysis
from agents.strategy_agent import build_positioning, build_voice_guide
from agents.content_agents import generate_all_content
from agents.evaluator_agent import evaluate_campaign, revise_weak_pieces


class CampaignOrchestrator:
    def __init__(self):
        self.client = GeminiClient()

    def run(
        self,
        product_url: str,
        product_description: str,
        target_audience: str,
        competitor_urls: list[str],
        campaign_goal: str,
        on_phase=None,
        on_progress=None,
    ) -> CampaignPackage:
        # --- Phase 1: Research ---
        if on_phase:
            on_phase("research")

        if on_progress:
            on_progress("Scraping product website...")
        product_page = scrape_url(product_url)

        if on_progress:
            on_progress("Scraping competitor websites...")
        competitor_pages: list[ScrapedPage] = []
        for url in competitor_urls:
            if url.strip():
                competitor_pages.append(scrape_url(url.strip()))

        if on_progress:
            on_progress("Analyzing product...")
        product_brief = build_product_brief(
            self.client, product_page, product_description, target_audience
        )

        if on_progress:
            on_progress("Analyzing competitors...")
        competitive_analysis = build_competitive_analysis(
            self.client, competitor_pages, product_brief
        )

        # --- Phase 2: Strategy ---
        if on_phase:
            on_phase("strategy")

        if on_progress:
            on_progress("Developing brand positioning...")
        positioning = build_positioning(
            self.client, product_brief, competitive_analysis, target_audience, campaign_goal
        )

        if on_progress:
            on_progress("Creating brand voice guide...")
        voice_guide = build_voice_guide(
            self.client, product_brief, positioning, target_audience
        )

        # --- Phase 3: Content Creation ---
        if on_phase:
            on_phase("content")

        content = generate_all_content(
            self.client, product_brief, positioning, voice_guide,
            target_audience, campaign_goal, on_progress=on_progress,
        )

        # --- Phase 4: Evaluation ---
        if on_phase:
            on_phase("evaluation")

        if on_progress:
            on_progress("Evaluating content quality...")
        evaluation = evaluate_campaign(self.client, content, positioning, voice_guide)

        if on_progress:
            on_progress("Checking for pieces needing revision...")
        content, evaluation = revise_weak_pieces(
            self.client, content, evaluation, positioning, voice_guide,
            on_progress=on_progress,
        )

        # --- Phase 5: Package ---
        if on_phase:
            on_phase("delivery")

        return CampaignPackage(
            product_brief=product_brief,
            competitive_analysis=competitive_analysis,
            positioning=positioning,
            voice_guide=voice_guide,
            content=content,
            evaluation=evaluation,
        )
