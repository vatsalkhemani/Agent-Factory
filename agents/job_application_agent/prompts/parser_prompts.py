def parse_job_prompt(job_text: str) -> tuple[str, str]:
    system = "You are an expert HR analyst and ATS specialist. You extract structured data from job descriptions with precision, identifying both explicit requirements and implicit signals."

    prompt = f"""Parse this job description into structured data.

## Job Description
{job_text}

Produce a JSON object with these exact fields:
- "title": The job title
- "company_name": The company name
- "company_url": Best guess at the company's website URL (e.g., "https://stripe.com"). If you can't determine it, use ""
- "location": Location (remote, city, etc.)
- "required_skills": List of explicitly required skills/technologies
- "preferred_skills": List of preferred/nice-to-have skills
- "responsibilities": List of 4-6 key responsibilities
- "experience_level": "entry", "mid", "senior", "staff", or "lead"
- "key_phrases": List of 8-12 exact phrases from the JD that an ATS would scan for. Include job-specific terminology, tools, methodologies, and qualifications verbatim as written.

For key_phrases: extract the exact wording used in the JD. These will be used for keyword matching, so precision matters. Include multi-word terms (e.g., "machine learning", "cross-functional collaboration", "CI/CD pipelines").
"""
    return system, prompt


def parse_resume_prompt(resume_text: str) -> tuple[str, str]:
    system = "You are an expert resume parser. You extract structured data from resumes regardless of formatting. You capture the essence of each role and skill precisely."

    prompt = f"""Parse this resume into structured data.

## Resume
{resume_text}

Produce a JSON object with these exact fields:
- "name": The person's name
- "current_title": Their most recent or current job title
- "skills": List of all skills mentioned (technical and non-technical)
- "experiences": List of work experiences, each with:
  - "title": Job title
  - "company": Company name
  - "duration": Time period (e.g., "Jan 2022 - Present")
  - "highlights": List of 2-4 key accomplishments/responsibilities as bullet points
- "education": List of education entries (e.g., "BS Computer Science, MIT, 2020")
- "summary": A 1-2 sentence summary of this person's professional profile based on the resume

Extract ALL experiences, even if they seem minor. Include skills that are implied by the work described, not just explicitly listed.
"""
    return system, prompt
