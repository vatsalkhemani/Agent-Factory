import json

from gemini_client import GeminiClient
from config import CREATIVE_TEMPERATURE, MODEL_SYNTHESIS
from models import DataProfile, Finding
from prompts.synthesizer_prompts import synthesis_prompt


def _format_profile_brief(profile: DataProfile) -> str:
    lines = [f"Rows: {profile.row_count} | Columns: {profile.column_count}"]
    if profile.sampled:
        lines.append("(Sampled from larger dataset)")
    for col in profile.columns:
        line = f"- {col.name} ({col.dtype})"
        if col.dtype == "numeric":
            line += f": mean={col.mean}, range=[{col.min_val}, {col.max_val}]"
        lines.append(line)
    return "\n".join(lines)


def _format_findings(findings: list[Finding]) -> str:
    sections = []
    for i, f in enumerate(findings, 1):
        sections.append(
            f"### Finding {i}: {f.title} [{f.importance.upper()}]\n"
            f"{f.description}\n"
            f"Data: {f.supporting_data}"
        )
    return "\n\n".join(sections)


def synthesize_report(
    client: GeminiClient,
    profile: DataProfile,
    findings: list[Finding],
) -> dict:
    """Returns dict with dataset_summary, narrative, methodology_notes."""
    profile_text = _format_profile_brief(profile)
    findings_text = _format_findings(findings)

    system, prompt = synthesis_prompt(profile_text, findings_text)
    data = client.generate_json(prompt, system, temperature=CREATIVE_TEMPERATURE, model=MODEL_SYNTHESIS)

    return {
        "dataset_summary": data.get("dataset_summary", ""),
        "narrative": data.get("narrative", ""),
        "methodology_notes": data.get("methodology_notes", []),
    }
