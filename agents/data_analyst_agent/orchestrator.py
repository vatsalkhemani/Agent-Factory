import json

import pandas as pd

from gemini_client import GeminiClient
from toolkit import AnalysisToolkit
from config import MAX_DEEP_DIVES
from models import (
    AnalysisReport, AnalysisResult, Finding,
)
from agents.profiler_agent import profile_data
from agents.hypothesis_agent import generate_hypotheses, generate_deep_dives
from agents.interpreter_agent import interpret_results
from agents.synthesizer_agent import synthesize_report


class AnalysisOrchestrator:
    def __init__(self):
        self.client = GeminiClient()

    def run(
        self,
        df: pd.DataFrame,
        user_context: str = "",
        on_phase=None,
        on_progress=None,
    ) -> AnalysisReport:
        toolkit = AnalysisToolkit(df)

        # --- Phase 1: PROFILE ---
        if on_phase:
            on_phase("profile", "Phase 1: Data Profiling")
        if on_progress:
            on_progress(f"Profiling {len(df)} rows x {len(df.columns)} columns...")

        profile = profile_data(toolkit)

        if on_progress:
            on_progress(f"Profile complete: {len(profile.columns)} columns analyzed, {len(profile.data_quality_notes)} quality notes")
            if profile.sampled:
                on_progress(f"Dataset sampled to {toolkit.df.shape[0]} rows for analysis")

        # --- Phase 2: HYPOTHESIZE ---
        if on_phase:
            on_phase("hypothesize", "Phase 2: Generating Hypotheses")
        if on_progress:
            on_progress("Analyzing data profile and forming hypotheses...")

        plan = generate_hypotheses(self.client, profile, user_context)

        if on_progress:
            on_progress(f"Generated {len(plan.hypotheses)} hypotheses")
            for h in plan.hypotheses:
                on_progress(f"  Hypothesis: {h.statement}")

        # --- Phase 3: ANALYZE ---
        if on_phase:
            on_phase("analyze", "Phase 3: Testing Hypotheses")

        all_results: list[AnalysisResult] = []
        for h in plan.hypotheses:
            if on_progress:
                on_progress(f"Testing: {h.statement}")

            for analysis in h.analyses:
                # Validate request
                valid, error = toolkit.validate_request(analysis.tool, analysis.params)
                if not valid:
                    all_results.append(AnalysisResult(
                        hypothesis=h.statement,
                        tool=analysis.tool,
                        params=analysis.params,
                        result_summary="",
                        raw_data={},
                        success=False,
                        error=error,
                    ))
                    continue

                # Execute
                result = toolkit.execute(analysis.tool, analysis.params)

                if result.get("success"):
                    raw_data = result["data"]
                    # Create a brief summary
                    summary = json.dumps(raw_data, default=str)[:300]
                    all_results.append(AnalysisResult(
                        hypothesis=h.statement,
                        tool=analysis.tool,
                        params=analysis.params,
                        result_summary=summary,
                        raw_data=raw_data,
                        success=True,
                    ))
                else:
                    all_results.append(AnalysisResult(
                        hypothesis=h.statement,
                        tool=analysis.tool,
                        params=analysis.params,
                        result_summary="",
                        raw_data={},
                        success=False,
                        error=result.get("error", "Unknown error"),
                    ))

        successful = [r for r in all_results if r.success]
        if on_progress:
            on_progress(f"Completed {len(successful)}/{len(all_results)} analyses successfully")

        # --- Phase 4: INTERPRET ---
        if on_phase:
            on_phase("interpret", "Phase 4: Interpreting Results")
        if on_progress:
            on_progress("Analyzing results and identifying key findings...")

        findings = interpret_results(self.client, profile, all_results)

        if on_progress:
            on_progress(f"Identified {len(findings)} findings")
            for f in findings:
                on_progress(f"  [{f.importance.upper()}] {f.title}")

        # --- Phase 5: DEEP DIVE ---
        if on_phase:
            on_phase("deep_dive", "Phase 5: Deep Dive Analysis")
        if on_progress:
            on_progress("Selecting top findings for deeper analysis...")

        if len(findings) >= 2:
            # Format findings for the deep dive prompt
            findings_text = "\n".join(
                f"{i}. [{f.importance}] {f.title}: {f.description}"
                for i, f in enumerate(findings)
            )

            deep_dives = generate_deep_dives(self.client, findings_text, profile)

            for dd in deep_dives[:MAX_DEEP_DIVES]:
                idx = dd["finding_index"]
                finding_name = findings[idx].title if idx < len(findings) else "Unknown"

                if on_progress:
                    on_progress(f"Deep diving into: {finding_name}")

                for analysis in dd["additional_analyses"]:
                    valid, error = toolkit.validate_request(analysis.tool, analysis.params)
                    if not valid:
                        continue

                    result = toolkit.execute(analysis.tool, analysis.params)
                    if result.get("success"):
                        all_results.append(AnalysisResult(
                            hypothesis=f"Deep dive: {finding_name}",
                            tool=analysis.tool,
                            params=analysis.params,
                            result_summary=json.dumps(result["data"], default=str)[:300],
                            raw_data=result["data"],
                            success=True,
                        ))

            # Re-interpret with additional results
            if on_progress:
                on_progress("Re-interpreting with deep dive results...")
            findings = interpret_results(self.client, profile, all_results)
        else:
            if on_progress:
                on_progress("Not enough findings for deep dive, proceeding to synthesis")

        # --- Phase 6: SYNTHESIZE ---
        if on_phase:
            on_phase("synthesize", "Phase 6: Writing Report")
        if on_progress:
            on_progress("Synthesizing narrative report...")

        synthesis = synthesize_report(self.client, profile, findings)

        if on_progress:
            on_progress("Report complete!")

        return AnalysisReport(
            dataset_summary=synthesis["dataset_summary"],
            key_findings=findings,
            narrative=synthesis["narrative"],
            methodology_notes=synthesis["methodology_notes"],
            data_profile=profile,
        )
