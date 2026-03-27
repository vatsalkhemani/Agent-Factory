import json

from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import DataProfile, AnalysisResult, Finding, ChartSpec
from prompts.interpreter_prompts import interpret_prompt


def _format_profile_brief(profile: DataProfile) -> str:
    lines = [f"Dataset: {profile.row_count} rows x {profile.column_count} columns"]
    for col in profile.columns:
        lines.append(f"- {col.name} ({col.dtype})")
    return "\n".join(lines)


def _format_results(results: list[AnalysisResult]) -> str:
    sections = []
    for r in results:
        if r.success:
            sections.append(
                f"### Hypothesis: {r.hypothesis}\n"
                f"Tool: {r.tool} | Params: {json.dumps(r.params)}\n"
                f"Result: {r.result_summary}\n"
                f"Data: {json.dumps(r.raw_data, default=str)[:800]}"
            )
        else:
            sections.append(
                f"### Hypothesis: {r.hypothesis}\n"
                f"Tool: {r.tool} | FAILED: {r.error}"
            )
    return "\n\n".join(sections)


def interpret_results(
    client: GeminiClient,
    profile: DataProfile,
    results: list[AnalysisResult],
) -> list[Finding]:
    profile_text = _format_profile_brief(profile)
    results_text = _format_results(results)

    system, prompt = interpret_prompt(profile_text, results_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    findings = []
    for f in data.get("findings", []):
        chart_spec = None
        if f.get("chart_spec"):
            try:
                chart_spec = ChartSpec(**f["chart_spec"])
            except Exception:
                pass

        try:
            findings.append(Finding(
                title=f.get("title", ""),
                description=f.get("description", ""),
                importance=f.get("importance", "medium"),
                supporting_data=f.get("supporting_data", ""),
                chart_spec=chart_spec,
            ))
        except Exception:
            continue

    return findings
