from gemini_client import GeminiClient
from config import SYNTHESIS_TEMPERATURE
from models import (
    ExtractedFact, ReasoningStep, ResearchReport,
    ReportSection, SourceCitation,
)
from prompts.synthesizer_prompts import synthesis_prompt


def _format_facts_for_synthesis(facts: list[ExtractedFact]) -> str:
    lines = []
    for i, f in enumerate(facts, 1):
        lines.append(f"{i}. [{f.confidence}] {f.claim}\n   Source: {f.source_url}")
    return "\n".join(lines)


def _build_sources_list(facts: list[ExtractedFact]) -> str:
    """Build a deduplicated list of all source URLs."""
    seen = set()
    lines = []
    for f in facts:
        if f.source_url not in seen:
            seen.add(f.source_url)
            lines.append(f"- {f.source_url}")
    return "\n".join(lines)


def synthesize(
    client: GeminiClient,
    question: str,
    all_facts: list[ExtractedFact],
    reasoning_trace: list[ReasoningStep],
) -> ResearchReport:
    facts_text = _format_facts_for_synthesis(all_facts)
    sources_list = _build_sources_list(all_facts)

    system, prompt = synthesis_prompt(question, facts_text, sources_list)
    data = client.generate_json(prompt, system, temperature=SYNTHESIS_TEMPERATURE)

    # Parse sections
    sections = []
    for s in data.get("sections", []):
        try:
            sections.append(ReportSection(**s))
        except Exception:
            continue

    # Parse sources
    sources = []
    for s in data.get("sources", []):
        try:
            sources.append(SourceCitation(**s))
        except Exception:
            continue

    return ResearchReport(
        question=question,
        executive_summary=data.get("executive_summary", ""),
        sections=sections,
        key_findings=data.get("key_findings", []),
        sources=sources,
        confidence_level=data.get("confidence_level", "medium"),
        reasoning_trace=reasoning_trace,
    )
