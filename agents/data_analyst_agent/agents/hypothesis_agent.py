import json

from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE, MAX_HYPOTHESES, MODEL_HYPOTHESIS, MODEL_DEEP_DIVE
from models import DataProfile, AnalysisPlan, Hypothesis, AnalysisRequest
from prompts.hypothesis_prompts import hypothesis_prompt, deep_dive_prompt


def _format_profile(profile: DataProfile) -> str:
    lines = [f"Rows: {profile.row_count} | Columns: {profile.column_count}"]
    if profile.sampled:
        lines.append("(Sampled from a larger dataset)")

    for col in profile.columns:
        line = f"- {col.name} ({col.dtype}): {col.non_null_count} non-null, {col.unique_count} unique"
        if col.dtype == "numeric":
            line += f" | mean={col.mean}, median={col.median}, std={col.std}, range=[{col.min_val}, {col.max_val}]"
        elif col.dtype == "categorical" and col.top_values:
            top = ", ".join(f"{v}({c})" for v, c in zip(col.top_values[:5], col.top_counts[:5]))
            line += f" | top: {top}"
        elif col.dtype == "datetime":
            line += f" | samples: {', '.join(col.sample_values)}"
        lines.append(line)

    if profile.data_quality_notes:
        lines.append("\nData Quality Notes:")
        for note in profile.data_quality_notes:
            lines.append(f"  - {note}")

    return "\n".join(lines)


def generate_hypotheses(
    client: GeminiClient,
    profile: DataProfile,
    user_context: str = "",
) -> AnalysisPlan:
    profile_text = _format_profile(profile)
    system, prompt = hypothesis_prompt(profile_text, user_context)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE, model=MODEL_HYPOTHESIS)

    hypotheses = []
    for h in data.get("hypotheses", [])[:MAX_HYPOTHESES]:
        analyses = []
        for a in h.get("analyses", []):
            try:
                analyses.append(AnalysisRequest(**a))
            except Exception:
                continue
        if analyses:
            try:
                hypotheses.append(Hypothesis(statement=h.get("statement", ""), analyses=analyses))
            except Exception:
                continue

    return AnalysisPlan(hypotheses=hypotheses)


def generate_deep_dives(
    client: GeminiClient,
    findings_text: str,
    profile: DataProfile,
) -> list[dict]:
    """Returns list of dicts with finding_index and additional_analyses."""
    profile_text = _format_profile(profile)
    system, prompt = deep_dive_prompt(findings_text, profile_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE, model=MODEL_DEEP_DIVE)

    deep_dives = []
    for dd in data.get("deep_dives", []):
        analyses = []
        for a in dd.get("additional_analyses", []):
            try:
                analyses.append(AnalysisRequest(**a))
            except Exception:
                continue
        if analyses:
            deep_dives.append({
                "finding_index": dd.get("finding_index", 0),
                "additional_analyses": analyses,
            })

    return deep_dives
