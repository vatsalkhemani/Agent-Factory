GEMINI_MODEL = "gemini-3.1-flash-lite-preview"  # default / fallback
MODEL_PLANNING = "gemini-3.1-flash-lite-preview"  # planning & extraction (15 RPM)
MODEL_EXTRACTION = "gemini-3.1-flash-lite-preview"  # fact extraction (15 RPM)
MODEL_EVALUATION = "gemini-3.1-flash-lite-preview"  # lightweight scoring (15 RPM)
MODEL_SYNTHESIS = "gemini-3.1-flash-lite-preview"  # creative report writing (15 RPM)
ANALYSIS_TEMPERATURE = 0.3
SYNTHESIS_TEMPERATURE = 0.7
MAX_ITERATIONS = 4
MIN_ITERATIONS = 2
COVERAGE_THRESHOLD = 8
SEARCH_RESULTS_PER_QUERY = 3
QUERIES_PER_ITERATION = 3
MAX_CONTENT_CHARS = 2000
SCRAPE_TIMEOUT = 8
SEARCH_DELAY = 2.0  # seconds between DDG searches to avoid rate limiting
LLM_TIMEOUT = 30
MAX_FACTS = 30  # cap accumulated facts to prevent token overflow
DEPTH_PRESETS = {
    "Quick": 2,
    "Standard": 3,
    "Deep": 4,
}
