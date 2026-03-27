def evaluation_prompt(question: str, all_facts: str, iteration: int) -> tuple[str, str]:
    system = "You are a research quality assessor. You evaluate whether collected facts are sufficient to answer a question comprehensively. You identify specific gaps, not vague ones. You are honest about what's missing."

    prompt = f"""We're researching: "{question}"

We are on iteration {iteration} of our research loop. Here are ALL facts collected so far:

{all_facts}

Evaluate whether we have enough information to write a comprehensive, well-supported answer to the research question.

Produce a JSON object with these exact fields:
- "coverage_score": Integer 1-10. How well do the collected facts cover the question?
  - 1-3: Major aspects completely unaddressed
  - 4-6: Key information present but significant gaps remain
  - 7-8: Good coverage with minor gaps
  - 9-10: Comprehensive, well-rounded coverage
- "well_covered": List of aspects/sub-questions that are well addressed (2-4 items)
- "gaps": List of specific information gaps that remain (be precise about what's missing, not vague)
- "should_continue": Boolean -- true if there are meaningful gaps that more searching could fill. False if coverage is sufficient OR if additional searching is unlikely to help.
- "next_focus": If should_continue is true, describe what the next search should focus on (1-2 sentences). If false, write "Coverage is sufficient."

Be rigorous. A coverage score of 8+ means we could write a well-cited report. Below 6 means major holes remain.
"""
    return system, prompt
