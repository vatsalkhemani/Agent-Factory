def synthesis_prompt(profile_text: str, findings_text: str) -> tuple[str, str]:
    system = "You are a data storytelling expert. You write clear, engaging narratives that turn data findings into a story. You write for a smart but non-technical audience. You use specific numbers and draw actionable conclusions."

    prompt = f"""Write a narrative data analysis report based on these findings.

## Dataset Overview
{profile_text}

## Key Findings
{findings_text}

Produce a JSON object with:
- "dataset_summary": 2-3 sentences describing the dataset (what it contains, how big it is, what time period it covers if applicable)
- "narrative": A 3-5 paragraph narrative report in markdown format. Structure it as:
  - Opening: What is this data about and what did we discover?
  - Body: Walk through the most important findings with specific numbers. Connect findings to each other where possible.
  - Closing: What does this all mean? What questions remain? What should the reader do next?
- "methodology_notes": List of 2-3 brief notes about the analysis approach (e.g., "Sampled 50,000 rows from 200,000 total", "Used IQR method for outlier detection", "Monthly aggregation for time trends")

Guidelines:
- Write like a data journalist, not a robot. "Revenue jumped 40% in Q4, driven almost entirely by the West region" not "The analysis revealed a statistically significant increase."
- Use specific numbers from the findings.
- Don't overstate conclusions -- be honest about limitations.
- Keep it under 500 words.
"""
    return system, prompt
