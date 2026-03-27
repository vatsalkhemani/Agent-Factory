def extraction_prompt(question: str, search_results: str, existing_facts: str) -> tuple[str, str]:
    system = "You are a meticulous research analyst. You extract specific, verifiable facts from search results. You distinguish between claims, data, and opinions. You never fabricate information -- only extract what's actually present in the sources."

    prompt = f"""We're researching: "{question}"

Here are the search results from this round:

{search_results}

Facts we already have from previous rounds:
{existing_facts if existing_facts else "(This is the first round -- no prior facts)"}

Extract NEW facts from these search results that help answer the research question. Only extract facts that are NOT already captured above.

Produce a JSON object with these exact fields:
- "facts": List of objects, each with:
  - "claim": A specific, verifiable fact or finding (1-2 sentences). Be precise -- include numbers, dates, names when available.
  - "source_url": The URL where this fact was found
  - "confidence": "high" (directly stated with evidence), "medium" (implied or partially supported), or "low" (single source, could be biased)
- "key_themes": List of 2-4 themes or patterns emerging from this batch of results

Rules:
- Only extract facts actually present in the search results. Never infer or fabricate.
- Prefer specific claims over vague generalizations.
- If a fact contradicts something we already know, include it and note the contradiction in the claim.
- Skip promotional or obviously biased content.
- Aim for 4-8 high-quality facts per round.
"""
    return system, prompt
