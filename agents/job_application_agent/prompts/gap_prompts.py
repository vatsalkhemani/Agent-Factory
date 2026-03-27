def gap_analysis_prompt(parsed_job: str, parsed_resume: str) -> tuple[str, str]:
    system = "You are a career coach and hiring expert. You analyze the gap between what a job requires and what a candidate offers. You're honest about gaps but constructive about transferable skills."

    prompt = f"""Analyze the gap between this job description and this candidate's resume.

## Parsed Job Description
{parsed_job}

## Parsed Resume
{parsed_resume}

Produce a JSON object with these exact fields:
- "matching_skills": List of skills the candidate HAS that the job REQUIRES (direct matches)
- "missing_skills": List of skills the job REQUIRES that the candidate LACKS (clear gaps)
- "transferable_skills": List of skills that aren't direct matches but are relevant. Each with:
  - "resume_skill": The skill the candidate has
  - "maps_to": The JD requirement it partially addresses
  - "strength": "direct" (very close), "adjacent" (related field), or "stretch" (loosely connected)
- "experience_alignment": "strong" (most requirements met), "moderate" (some gaps but solid foundation), or "weak" (significant gaps)
- "priority_areas": List of 3-5 areas to emphasize when tailoring the resume. These should be the candidate's strongest matches to the job's most important requirements.

Be specific. Don't just say "Python" -- say "Python (candidate has 3 years, job requires 5+)" if there's a partial match.
"""
    return system, prompt
