from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE, MODEL_EVALUATION
from models import CoverageEvaluation, ExtractedFact
from prompts.evaluator_prompts import evaluation_prompt


def _format_all_facts(facts: list[ExtractedFact]) -> str:
    if not facts:
        return "(No facts collected yet)"
    lines = []
    for i, f in enumerate(facts, 1):
        lines.append(f"{i}. [{f.confidence}] {f.claim}\n   Source: {f.source_url}")
    return "\n".join(lines)


def evaluate_coverage(
    client: GeminiClient,
    question: str,
    all_facts: list[ExtractedFact],
    iteration: int,
) -> CoverageEvaluation:
    facts_text = _format_all_facts(all_facts)
    system, prompt = evaluation_prompt(question, facts_text, iteration)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE, model=MODEL_EVALUATION)

    return CoverageEvaluation(
        coverage_score=int(data.get("coverage_score", 5)),
        well_covered=data.get("well_covered", []),
        gaps=data.get("gaps", []),
        should_continue=data.get("should_continue", True),
        next_focus=data.get("next_focus", ""),
    )
