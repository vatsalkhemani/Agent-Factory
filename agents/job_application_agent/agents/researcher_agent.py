from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE, MODEL_ANALYSIS
from models import CompanyIntel
from search import search_company
from prompts.researcher_prompts import company_research_prompt


def research_company(client: GeminiClient, company_name: str, company_url: str = "") -> CompanyIntel:
    # Gather raw research data
    research = search_company(company_name, company_url)
    research_content = research["content"]

    # Synthesize into structured intel
    system, prompt = company_research_prompt(company_name, research_content)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE, model=MODEL_ANALYSIS)

    return CompanyIntel(**data)
