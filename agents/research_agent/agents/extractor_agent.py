import json

from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE, MODEL_EXTRACTION
from models import ExtractedFact, ExtractionResult, SearchResult
from prompts.extractor_prompts import extraction_prompt


def _format_search_results(results: list[SearchResult]) -> str:
    sections = []
    for r in results:
        status = "OK" if r.success else "FAILED"
        sections.append(
            f"--- Source: {r.url} ({status}) ---\n"
            f"Title: {r.title}\n"
            f"Snippet: {r.snippet}\n"
            f"Content: {r.content[:1500]}\n"
        )
    return "\n".join(sections)


def _format_existing_facts(facts: list[ExtractedFact]) -> str:
    if not facts:
        return ""
    lines = []
    for i, f in enumerate(facts, 1):
        lines.append(f"{i}. [{f.confidence}] {f.claim} (source: {f.source_url})")
    return "\n".join(lines)


def extract_facts(
    client: GeminiClient,
    question: str,
    search_results: list[SearchResult],
    existing_facts: list[ExtractedFact],
) -> ExtractionResult:
    results_text = _format_search_results(search_results)
    facts_text = _format_existing_facts(existing_facts)

    system, prompt = extraction_prompt(question, results_text, facts_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE, model=MODEL_EXTRACTION)

    facts = []
    for f in data.get("facts", []):
        try:
            facts.append(ExtractedFact(**f))
        except Exception:
            # Skip malformed facts rather than crashing
            continue

    key_themes = data.get("key_themes", [])

    return ExtractionResult(facts=facts, key_themes=key_themes)
