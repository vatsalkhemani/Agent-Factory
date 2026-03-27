# Data Analyst Agent -- Technical Requirements Document

## Architecture Overview

The Data Analyst Agent uses an orchestrator with a critical safety boundary: the LLM never executes code. Instead, a predefined `AnalysisToolkit` class provides 10 analysis operations. The LLM selects which tool to call and with what parameters; the orchestrator validates and executes.

```
CSV Upload
    |
    v
[AnalysisOrchestrator]
    |
    +---> Phase 1: Profile (deterministic -- AnalysisToolkit.profile())
    +---> Phase 2: Hypothesize (LLM generates hypotheses + tool selections)
    +---> Phase 3: Analyze (toolkit executes validated tool calls)
    +---> Phase 4: Interpret (LLM ranks results, identifies findings)
    +---> Phase 5: Deep Dive (LLM picks top 2, requests more analyses)
    +---> Phase 6: Synthesize (LLM writes narrative report)
    |
    v
AnalysisReport (findings + charts + narrative)
```

## The Safety Boundary

**No LLM-generated code is ever executed.** The architecture:

1. `AnalysisToolkit` has 10 methods: `describe`, `correlation`, `distribution`, `group_comparison`, `time_trend`, `outlier_detection`, `cross_tabulation`, `top_n`, `value_counts`, `percentile_analysis`
2. The LLM returns JSON: `{"tool": "correlation", "params": {"columns": ["revenue", "cost"]}}`
3. The orchestrator calls `toolkit.validate_request(tool, params)` to verify columns exist and types are compatible
4. If valid, `toolkit.execute(tool, params)` runs the actual pandas computation
5. Results are returned as dicts -- structured data, not code

This ensures reliability, security, and predictable behavior.

## File Structure

```
data_analyst_agent/
  app.py               (293 lines) - Streamlit UI with charts
  orchestrator.py      (186 lines) - 6-phase pipeline driver
  models.py            (132 lines) - 12 Pydantic models
  config.py            (13 lines)  - Constants
  gemini_client.py     (122 lines) - LLM wrapper with retry + JSON parsing
  toolkit.py           (302 lines) - 10 predefined analysis operations
  chart_builder.py     (140 lines) - 7 Plotly chart builders
  agents/
    profiler_agent.py  (9 lines)   - Wraps toolkit.profile()
    hypothesis_agent.py(83 lines)  - Generates hypotheses + deep dives
    interpreter_agent.py(65 lines) - Interprets results, ranks findings
    synthesizer_agent.py(48 lines) - Writes narrative report
  prompts/
    hypothesis_prompts.py(72 lines)
    interpreter_prompts.py(35 lines)
    synthesizer_prompts.py(26 lines)
    profiler_prompts.py(4 lines)   - Placeholder for future use
```

Total: ~1,530 lines across 17 files.

## Analysis Toolkit (toolkit.py)

The toolkit is the compute engine. Each method:
- Takes typed parameters (column names, aggregation type, etc.)
- Validates input
- Executes pandas operations
- Returns a dict with results

### Available Tools

| Tool | Purpose | Key Params |
|------|---------|------------|
| `describe` | Full descriptive stats | column |
| `correlation` | Pearson correlation matrix | columns (optional) |
| `distribution` | Histogram/frequency data | column, bins |
| `group_comparison` | Group by + aggregate | group_column, value_column, agg |
| `time_trend` | Time series resampling | date_column, value_column, freq |
| `outlier_detection` | IQR or z-score outliers | column, method |
| `cross_tabulation` | Two-way frequency table | column_1, column_2 |
| `top_n` | Top/bottom records | column, n, ascending |
| `value_counts` | Value frequencies | column, top_n |
| `percentile_analysis` | Percentile breakdown | column |

### Validation

`validate_request(tool, params)` checks:
- Tool name is in `VALID_TOOLS`
- All referenced columns exist in the DataFrame
- Returns `(bool, error_message)`

Failed validations are logged as `AnalysisResult(success=False)` and skipped gracefully.

## Chart Builder (chart_builder.py)

Maps `ChartSpec` models to Plotly Express calls. 7 chart types:

| Type | Builder | Key Logic |
|------|---------|-----------|
| bar | `_build_bar` | Auto-aggregates if >20 categories |
| scatter | `_build_scatter` | Supports color grouping |
| line | `_build_line` | Auto-sorts by x-axis |
| histogram | `_build_histogram` | Configurable bins |
| box | `_build_box` | Optional grouping by x |
| heatmap | `_build_heatmap` | Correlation matrix for numeric columns |
| pie | `_build_pie` | Top 10 categories |

All charts are capped at `MAX_CHART_POINTS` (1000) to prevent slow rendering.
Chart failures return `None` and are silently skipped.

## CSV Loading Strategy

```python
# 1. Try UTF-8, then Latin-1
# 2. Auto-detect delimiter (sep=None, engine='python')
# 3. Skip bad lines (on_bad_lines='skip')
# 4. Smart type coercion:
#    - Try pd.to_numeric (>50% success = numeric)
#    - Try pd.to_datetime (>50% success = datetime)
#    - Otherwise: keep as string/categorical
```

## Data Profile

The profiler is deterministic (no LLM):
- Column types: numeric, categorical, datetime, text
- Categorical threshold: <20 unique values AND <5% of total rows
- Numeric stats: mean, median, std, min, max
- Categorical stats: top 8 values with counts
- Quality notes: columns with >10% null, very high variance (CV > 2)
- Sampling: >50K rows triggers random sampling with seed 42

## Orchestrator Flow

1. **Profile**: `toolkit.profile()` -- pure pandas, no LLM
2. **Hypothesize**: Profile text -> LLM -> `AnalysisPlan` (4-6 hypotheses with tool requests)
3. **Analyze**: For each hypothesis, validate and execute tool calls. Collect `AnalysisResult` list
4. **Interpret**: All results -> LLM -> ranked `Finding` list with `ChartSpec` suggestions
5. **Deep Dive**: Top findings -> LLM -> 2 deep dive requests -> execute -> re-interpret
6. **Synthesize**: Findings -> LLM -> narrative report + methodology notes

## Key Design Decisions

### 1. Predefined toolkit (no code execution)
- Safe, reliable, predictable
- Covers ~90% of common exploratory analysis patterns
- The LLM is the brain (decides what to analyze), toolkit is the hands (executes safely)

### 2. Hypothesis-driven analysis
- The LLM forms hypotheses BEFORE running analyses
- This prevents scattershot "compute everything" approaches
- Hypotheses are informed by the actual data profile (column types, distributions, etc.)

### 3. Two-pass interpretation
- First pass: interpret initial hypothesis results
- Deep dive: run additional targeted analyses on top findings
- Second pass: re-interpret with all results
- This simulates how a real analyst works: broad scan, then zoom in

### 4. Chart specs as data (not code)
- The LLM suggests charts as structured `ChartSpec` objects
- The chart builder maps specs to Plotly Express calls
- Invalid specs produce `None` and are skipped
- This keeps visualization reliable and controlled

## Error Handling

| Failure | Recovery |
|---------|----------|
| CSV encoding error | Try UTF-8, then Latin-1 |
| Bad CSV rows | Skip with `on_bad_lines='skip'` |
| Column doesn't exist | `validate_request` catches, analysis skipped |
| Wrong type for analysis | Toolkit methods handle gracefully |
| Toolkit execution error | Wrapped in try/except, returns `success=False` |
| Chart build fails | Returns `None`, silently skipped |
| All analyses fail | Report generated with just data profile |
| Empty DataFrame | Caught before orchestrator, user error shown |

## Configuration

- `MAX_ROWS`: 50,000 (sampling threshold)
- `MAX_HYPOTHESES`: 6
- `MAX_DEEP_DIVES`: 2
- `MAX_CHART_POINTS`: 1,000
- `OUTLIER_Z_THRESHOLD`: 3.0
- `OUTLIER_IQR_MULTIPLIER`: 1.5

## Dependencies

- streamlit, google-genai, pandas, numpy, plotly, pydantic, python-dotenv
- No external APIs beyond Gemini. No web search, no scraping.
