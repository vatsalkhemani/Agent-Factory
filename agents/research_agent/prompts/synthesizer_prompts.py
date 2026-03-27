def synthesis_prompt(question: str, all_facts: str, sources_list: str) -> tuple[str, str]:
    system = "You are a senior research analyst who writes clear, well-structured research reports. You synthesize facts into coherent narratives, cite your sources, and distinguish between well-supported conclusions and areas of uncertainty. You write for an intelligent general audience."

    prompt = f"""Write a comprehensive research report answering this question:

"{question}"

Use ONLY these collected facts as your source material:

{all_facts}

Available sources:
{sources_list}

Produce a JSON object with these exact fields:
- "executive_summary": A clear 3-5 sentence summary of the key findings. Lead with the answer to the question.
- "sections": List of 3-5 report sections, each with:
  - "heading": Section title
  - "content": 2-4 paragraphs of analysis and findings for this section. Write in full prose, not bullet points. Reference specific facts and data points.
  - "supporting_sources": List of source URLs that support this section's claims
- "key_findings": List of 4-6 bullet-point key findings (the most important takeaways)
- "sources": List of all sources used, each with:
  - "url": The source URL
  - "title": The source title or domain name
  - "used_for": What information this source provided (1 sentence)
- "confidence_level": "high" (multiple corroborating sources, strong evidence), "medium" (some sources, reasonable evidence), or "low" (limited sources, mostly inferred)

Guidelines:
- Synthesize and analyze -- don't just list facts. Draw connections and identify patterns.
- If sources contradict each other, acknowledge the disagreement.
- Be specific: use numbers, dates, and names from the facts.
- The report should feel like it was written by a thorough researcher, not generated from a single search.
"""
    return system, prompt
