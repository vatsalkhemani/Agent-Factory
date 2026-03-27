import time

from gemini_client import GeminiClient
from search import web_search
from config import (
    MAX_ITERATIONS, MIN_ITERATIONS, COVERAGE_THRESHOLD,
    QUERIES_PER_ITERATION, SEARCH_DELAY, MAX_FACTS,
)
from models import (
    ExtractedFact, ReasoningStep, ResearchReport, SearchResult,
)
from agents.planner_agent import create_initial_plan, replan
from agents.extractor_agent import extract_facts
from agents.evaluator_agent import evaluate_coverage
from agents.synthesizer_agent import synthesize


class ResearchOrchestrator:
    def __init__(self):
        self.client = GeminiClient()

    def run(
        self,
        question: str,
        max_iterations: int = MAX_ITERATIONS,
        on_phase=None,
        on_progress=None,
        on_reasoning_step=None,
    ) -> ResearchReport:
        all_facts: list[ExtractedFact] = []
        all_results: list[SearchResult] = []
        reasoning_trace: list[ReasoningStep] = []
        iteration = 0
        gaps = []
        next_focus = ""

        while iteration < max_iterations:
            iteration += 1

            # --- PLAN / REPLAN ---
            if on_phase:
                on_phase(f"iteration_{iteration}", f"Research Loop {iteration}")

            if iteration == 1:
                if on_progress:
                    on_progress(f"Planning initial research strategy...")
                plan = create_initial_plan(self.client, question)
                reasoning_trace.append(ReasoningStep(
                    iteration=iteration,
                    phase="plan",
                    summary=f"Initial plan: {len(plan.queries)} search queries",
                    detail=f"Focus areas: {', '.join(plan.focus_areas)}\nQueries: {', '.join(q.query for q in plan.queries)}",
                ))
            else:
                if on_progress:
                    on_progress(f"Replanning based on {len(gaps)} gaps found...")
                facts_text = "\n".join(f"- {f.claim}" for f in all_facts)
                plan = replan(self.client, question, facts_text, gaps, next_focus)
                reasoning_trace.append(ReasoningStep(
                    iteration=iteration,
                    phase="replan",
                    summary=f"Replanned: targeting {len(gaps)} gaps with {len(plan.queries)} new queries",
                    detail=f"Gaps: {', '.join(gaps)}\nNew queries: {', '.join(q.query for q in plan.queries)}",
                ))

            if on_reasoning_step:
                on_reasoning_step(reasoning_trace[-1])

            # --- SEARCH ---
            if on_progress:
                on_progress(f"Searching ({len(plan.queries)} queries)...")

            iteration_results = []
            for i, sq in enumerate(plan.queries[:QUERIES_PER_ITERATION]):
                if on_progress:
                    on_progress(f"Searching: \"{sq.query}\"")
                results = web_search(sq.query)
                iteration_results.extend(results)
                all_results.extend(results)

                # Delay between searches to avoid rate limiting
                if i < len(plan.queries) - 1:
                    time.sleep(SEARCH_DELAY)

            successful = [r for r in iteration_results if r.success]
            reasoning_trace.append(ReasoningStep(
                iteration=iteration,
                phase="search",
                summary=f"Found {len(successful)}/{len(iteration_results)} successful results",
                detail=f"Sources: {', '.join(set(r.url for r in successful[:5]))}",
            ))
            if on_reasoning_step:
                on_reasoning_step(reasoning_trace[-1])

            # --- EXTRACT ---
            if on_progress:
                on_progress("Extracting facts from search results...")

            if iteration_results:
                extraction = extract_facts(
                    self.client, question, iteration_results, all_facts
                )
                new_facts = extraction.facts
                all_facts.extend(new_facts)

                # Cap facts to prevent token overflow
                if len(all_facts) > MAX_FACTS:
                    # Keep the most recent facts (they tend to be more targeted)
                    all_facts = all_facts[-MAX_FACTS:]

                reasoning_trace.append(ReasoningStep(
                    iteration=iteration,
                    phase="extract",
                    summary=f"Extracted {len(new_facts)} new facts (total: {len(all_facts)})",
                    detail=f"Themes: {', '.join(extraction.key_themes)}",
                ))
            else:
                reasoning_trace.append(ReasoningStep(
                    iteration=iteration,
                    phase="extract",
                    summary="No results to extract from",
                    detail="All searches returned empty results this iteration.",
                ))

            if on_reasoning_step:
                on_reasoning_step(reasoning_trace[-1])

            # --- EVALUATE ---
            if on_progress:
                on_progress("Evaluating research coverage...")

            evaluation = evaluate_coverage(
                self.client, question, all_facts, iteration
            )

            reasoning_trace.append(ReasoningStep(
                iteration=iteration,
                phase="evaluate",
                summary=f"Coverage: {evaluation.coverage_score}/10 | Continue: {evaluation.should_continue}",
                detail=f"Well covered: {', '.join(evaluation.well_covered)}\nGaps: {', '.join(evaluation.gaps) if evaluation.gaps else 'None identified'}",
            ))
            if on_reasoning_step:
                on_reasoning_step(reasoning_trace[-1])

            # --- CONVERGENCE CHECK ---
            # Always do at least MIN_ITERATIONS
            if iteration >= MIN_ITERATIONS:
                if evaluation.coverage_score >= COVERAGE_THRESHOLD:
                    if on_progress:
                        on_progress(f"Coverage score {evaluation.coverage_score}/10 meets threshold. Moving to synthesis.")
                    break
                if not evaluation.should_continue:
                    if on_progress:
                        on_progress("Agent determined further searching unlikely to help. Moving to synthesis.")
                    break

            gaps = evaluation.gaps
            next_focus = evaluation.next_focus

        # --- SYNTHESIZE ---
        if on_phase:
            on_phase("synthesis", "Synthesis")
        if on_progress:
            on_progress(f"Synthesizing report from {len(all_facts)} facts across {iteration} research loops...")

        report = synthesize(self.client, question, all_facts, reasoning_trace)

        if on_progress:
            on_progress("Research complete!")

        return report
