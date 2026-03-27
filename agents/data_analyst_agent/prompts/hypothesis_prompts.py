def hypothesis_prompt(profile_text: str, user_context: str = "") -> tuple[str, str]:
    system = "You are a senior data analyst with expertise in exploratory data analysis. Given a dataset profile, you generate insightful hypotheses about what patterns might exist in the data. You think like a detective -- looking for relationships, anomalies, and stories hidden in the numbers."

    context_line = f"\nThe user provided this context: \"{user_context}\"\n" if user_context else ""

    prompt = f"""Based on this dataset profile, generate hypotheses about what might be interesting in the data.
{context_line}
## Dataset Profile
{profile_text}

## Available Analysis Tools
You can request any of these analysis operations:
- "describe": Full stats for a column. Params: {{"column": "col_name"}}
- "correlation": Correlation matrix. Params: {{"columns": ["col1", "col2", ...]}} (optional, uses all numeric if omitted)
- "distribution": Histogram/value counts. Params: {{"column": "col_name", "bins": 20}}
- "group_comparison": Group by + aggregate. Params: {{"group_column": "cat_col", "value_column": "num_col", "agg": "mean"}}
- "time_trend": Time series trend. Params: {{"date_column": "date_col", "value_column": "num_col", "freq": "ME"}}
- "outlier_detection": Find outliers. Params: {{"column": "col_name", "method": "iqr"}}
- "cross_tabulation": Cross-tab two categorical columns. Params: {{"column_1": "col1", "column_2": "col2"}}
- "top_n": Top/bottom records. Params: {{"column": "col_name", "n": 10, "ascending": false}}
- "value_counts": Frequency of values. Params: {{"column": "col_name", "top_n": 15}}
- "percentile_analysis": Percentile breakdown. Params: {{"column": "col_name"}}

Produce a JSON object with:
- "hypotheses": List of 4-6 hypotheses, each with:
  - "statement": A clear hypothesis (e.g., "Revenue shows strong seasonal patterns" or "Region X outperforms others significantly")
  - "analyses": List of 1-2 analysis requests to test this hypothesis, each with:
    - "tool": One of the tool names above
    - "params": The parameters dict for that tool (use EXACT column names from the profile)
    - "rationale": Why this analysis will help test the hypothesis

CRITICAL: Use the EXACT column names from the profile. Do not invent column names.

Think creatively:
- Are there correlations between numeric columns?
- Do categorical groups differ significantly on numeric measures?
- Are there temporal patterns if date columns exist?
- Are there outliers that tell a story?
- Does the distribution of key columns reveal anything unexpected?
"""
    return system, prompt


def deep_dive_prompt(findings_text: str, profile_text: str) -> tuple[str, str]:
    system = "You are a senior data analyst performing deep-dive analysis. Given initial findings, you design follow-up analyses to strengthen the most interesting discoveries."

    prompt = f"""Based on these initial findings, select the top 2 most interesting ones and design deeper analyses.

## Initial Findings
{findings_text}

## Dataset Profile
{profile_text}

## Available Analysis Tools
Same tools as before: describe, correlation, distribution, group_comparison, time_trend, outlier_detection, cross_tabulation, top_n, value_counts, percentile_analysis.

Produce a JSON object with:
- "deep_dives": List of 2 deep dives, each with:
  - "finding_index": Which finding to explore deeper (0-indexed)
  - "additional_analyses": List of 1-2 new analyses, each with:
    - "tool": Tool name
    - "params": Parameters dict (use EXACT column names)
    - "rationale": What additional insight this will provide

Design analyses that ADD to what we already know -- don't repeat the same analysis. Think about:
- Segmenting a broad finding by another dimension
- Testing whether a pattern holds across subgroups
- Drilling into outlier cases
- Checking if a correlation is spurious by controlling for a third variable
"""
    return system, prompt
