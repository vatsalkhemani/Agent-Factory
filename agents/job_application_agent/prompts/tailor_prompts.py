def tailor_resume_prompt(parsed_resume: str, parsed_job: str, gap_analysis: str, company_intel: str) -> tuple[str, str]:
    system = "You are an expert resume writer and career coach. You tailor resumes to specific job descriptions by reframing existing experience -- never fabricating. You know how ATS systems work and optimize for keyword matching while keeping content authentic."

    prompt = f"""Tailor this candidate's resume for the target job. Reframe their existing experience to better align with what the job requires. DO NOT fabricate experience or skills the candidate doesn't have.

## Candidate's Current Resume
{parsed_resume}

## Target Job
{parsed_job}

## Gap Analysis
{gap_analysis}

## Company Intelligence
{company_intel}

Produce a JSON object with these exact fields:
- "summary": A rewritten 2-3 sentence professional summary tailored to this specific role. Weave in key phrases from the JD naturally. Highlight the candidate's most relevant experience for this role.
- "skills_section": List of skills, reordered to put the most relevant ones first. Include all existing skills but prioritize those matching the JD. If the candidate has a skill under a different name than the JD uses, use the JD's terminology (e.g., if resume says "ML" and JD says "machine learning", use "machine learning").
- "experience_bullets": List of rewritten experience entries, each with:
  - "company": Company name
  - "title": Job title
  - "bullets": List of 3-4 rewritten bullet points. Each bullet should:
    - Start with a strong action verb
    - Include quantifiable results where the original had them
    - Naturally incorporate relevant JD keywords
    - Emphasize aspects of the role most relevant to the target job
    - NOT fabricate achievements or metrics not in the original
- "keywords_added": List of JD keywords that were woven into the tailored resume (for ATS tracking)

Rules:
- Reframe, don't fabricate. If the candidate managed 3 people, don't say 30.
- Use the JD's exact terminology where it fits naturally.
- Prioritize the most recent and relevant experience.
- Every bullet should be specific and results-oriented.
"""
    return system, prompt


def revise_resume_prompt(tailored_resume: str, ats_feedback: str, parsed_job: str) -> tuple[str, str]:
    system = "You are an ATS optimization specialist. You revise tailored resumes based on specific ATS scoring feedback, ensuring keyword coverage and format compliance."

    prompt = f"""Revise this tailored resume based on the ATS evaluation feedback.

## Current Tailored Resume
{tailored_resume}

## ATS Feedback
{ats_feedback}

## Target Job
{parsed_job}

Fix the specific issues identified in the ATS feedback. Focus on:
1. Adding missing keywords naturally (don't keyword-stuff)
2. Improving bullet point relevance to the target role
3. Strengthening the professional summary

Return the revised resume in the SAME JSON format:
- "summary": Revised professional summary
- "skills_section": Revised skills list
- "experience_bullets": Revised experience entries (same format as before)
- "keywords_added": Updated list of JD keywords present in the resume
"""
    return system, prompt
