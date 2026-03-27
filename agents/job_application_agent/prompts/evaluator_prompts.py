def ats_evaluation_prompt(tailored_resume: str, cover_letter: str, parsed_job: str) -> tuple[str, str]:
    system = "You are an ATS (Applicant Tracking System) scoring engine and hiring expert. You evaluate resumes and cover letters against job descriptions with specific, measurable criteria. You score rigorously -- an 8+ means genuinely strong."

    prompt = f"""Evaluate this tailored resume and cover letter against the target job description.

## Target Job
{parsed_job}

## Tailored Resume
{tailored_resume}

## Cover Letter
{cover_letter}

Score on these three criteria (1-10 each):

1. **Keyword Match Score**: How well does the resume incorporate key phrases from the JD?
   - 9-10: Nearly all key phrases present, naturally integrated
   - 7-8: Most key phrases present, some gaps
   - 5-6: About half the key phrases present
   - 1-4: Significant keyword gaps

2. **Format Score**: Is the resume well-structured for ATS parsing?
   - 9-10: Clean structure, clear sections, consistent formatting
   - 7-8: Good structure, minor issues
   - 5-6: Some structural problems
   - 1-4: Poorly structured

3. **Relevance Score**: How well does the content align with the role?
   - 9-10: Experience directly maps to requirements, strong narrative
   - 7-8: Good alignment with minor gaps
   - 5-6: Partial alignment
   - 1-4: Weak alignment

Produce a JSON object with these exact fields:
- "keyword_match_score": Integer 1-10
- "format_score": Integer 1-10
- "relevance_score": Integer 1-10
- "overall_score": Integer 1-10 (weighted: 40% keyword, 20% format, 40% relevance)
- "missing_keywords": List of specific JD keywords/phrases NOT found in the resume
- "feedback": 3-4 sentences of specific, actionable feedback. What's working and what needs improvement.
- "needs_revision": Boolean -- true if overall_score < 7
"""
    return system, prompt
