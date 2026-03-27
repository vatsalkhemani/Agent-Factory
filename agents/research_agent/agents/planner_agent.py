from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import SearchPlan, SearchQuery
from prompts.planner_prompts import initial_plan_prompt, replan_prompt


def create_initial_plan(client: GeminiClient, question: str) -> SearchPlan:
    system, prompt = initial_plan_prompt(question)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    queries = [SearchQuery(**q) for q in data.get("queries", [])]
    focus_areas = data.get("focus_areas", [])

    # Ensure we have at least 1 query
    if not queries:
        queries = [SearchQuery(query=question, rationale="Direct search for the main question")]

    return SearchPlan(queries=queries, focus_areas=focus_areas)


def replan(client: GeminiClient, question: str, facts_text: str, gaps: list[str], next_focus: str) -> SearchPlan:
    system, prompt = replan_prompt(question, facts_text, gaps, next_focus)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    queries = [SearchQuery(**q) for q in data.get("queries", [])]
    focus_areas = data.get("focus_areas", [])

    # Ensure we have at least 1 query
    if not queries:
        queries = [SearchQuery(query=f"{question} {next_focus}", rationale="Fallback search targeting identified gap")]

    return SearchPlan(queries=queries, focus_areas=focus_areas)
