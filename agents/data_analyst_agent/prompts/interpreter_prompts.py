def interpret_prompt(profile_text: str, results_text: str) -> tuple[str, str]:
    system = "You are a data storyteller and senior analyst. You interpret analysis results and identify the most interesting, surprising, or actionable findings. You rank findings by how interesting they are to a general audience."

    prompt = f"""Interpret these analysis results and identify the key findings.

## Dataset Profile
{profile_text}

## Analysis Results
{results_text}

For each meaningful finding, also suggest a visualization.

Produce a JSON object with:
- "findings": List of 3-6 findings, ordered by importance (most interesting first). Each with:
  - "title": A concise, engaging title (e.g., "Revenue Spikes 40% in Q4" not "Revenue Analysis")
  - "description": 2-3 sentences explaining what was found and why it matters. Include specific numbers.
  - "importance": "high" (surprising, actionable, or statistically strong), "medium" (interesting pattern), or "low" (minor observation)
  - "supporting_data": Key numbers or stats that support this finding (1-2 sentences)
  - "chart_spec": A visualization spec (or null if no chart needed) with:
    - "chart_type": One of "bar", "scatter", "line", "histogram", "box", "heatmap", "pie"
    - "x_column": Column for x-axis (use EXACT column names, or null)
    - "y_column": Column for y-axis (or null)
    - "color_column": Optional column for color grouping (or null)
    - "title": Chart title
    - "params": Additional params dict (e.g., {{"bins": 30}} for histogram)

Guidelines:
- Lead with the most surprising or actionable finding
- Use specific numbers, not vague claims ("3.2x higher" not "much higher")
- Only suggest charts that will actually be informative
- If an analysis failed or returned nothing interesting, skip it
- A finding about the absence of a pattern ("no correlation between X and Y") can be interesting if the correlation was expected
"""
    return system, prompt
