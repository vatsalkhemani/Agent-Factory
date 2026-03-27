def initial_plan_prompt(question: str) -> tuple[str, str]:
    system = "You are an expert research strategist. You break complex questions into targeted search queries that will yield comprehensive, factual answers. Think like an investigative journalist."

    prompt = f"""A user wants to research this question:

"{question}"

Break this question down into 3 specific web search queries that will help answer it comprehensively. Each query should target a different aspect of the question.

Produce a JSON object with these exact fields:
- "queries": List of objects, each with:
  - "query": The exact search string to use (be specific, use keywords that will find authoritative sources)
  - "rationale": Why this search will help answer the question (1 sentence)
- "focus_areas": List of 3-5 key aspects/angles of the question that need to be covered

Think about what sub-questions need answering. Don't just rephrase the original question 3 times -- each query should target different information.
"""
    return system, prompt


def replan_prompt(question: str, facts_so_far: str, gaps: list[str], next_focus: str) -> tuple[str, str]:
    system = "You are an expert research strategist. You identify what's still missing from a research effort and design targeted searches to fill those gaps. You never repeat searches that have already been done."

    prompt = f"""We're researching this question:

"{question}"

Here's what we've learned so far:
{facts_so_far}

The evaluator identified these GAPS in our knowledge:
{chr(10).join(f'- {g}' for g in gaps)}

Suggested next focus: {next_focus}

Design 2-3 NEW search queries that specifically target these gaps. Do NOT repeat information we already have. Each query should aim to fill a specific gap.

Produce a JSON object with these exact fields:
- "queries": List of objects, each with:
  - "query": The exact search string to use (be specific and targeted at the gaps)
  - "rationale": Which gap this search aims to fill (1 sentence)
- "focus_areas": List of 2-3 specific things we still need to learn
"""
    return system, prompt
