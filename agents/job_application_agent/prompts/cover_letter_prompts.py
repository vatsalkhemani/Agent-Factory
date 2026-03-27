def cover_letter_prompt(parsed_job: str, parsed_resume: str, gap_analysis: str, company_intel: str) -> tuple[str, str]:
    system = "You are an expert cover letter writer. You write compelling, authentic cover letters that connect a candidate's experience to a specific role. You avoid generic language and corporate cliches. Every sentence should add value."

    prompt = f"""Write a cover letter for this candidate applying to this specific role.

## Target Job
{parsed_job}

## Candidate Resume
{parsed_resume}

## Gap Analysis
{gap_analysis}

## Company Intelligence
{company_intel}

Produce a JSON object with these exact fields:
- "opening": A compelling opening paragraph (3-4 sentences). Don't start with "I am writing to apply for..." -- start with something that shows you understand the company or role. Reference a specific company initiative, value, or product from the company intelligence.
- "body_paragraphs": List of 2-3 body paragraphs (each 3-5 sentences). Each paragraph should:
  - Connect a specific piece of the candidate's experience to a specific job requirement
  - Use concrete examples and results from the resume
  - Show how the candidate's background uniquely positions them for this role
  - Address a gap constructively if relevant (frame as "eager to grow in X" not "I lack X")
- "closing": A strong closing paragraph (2-3 sentences). Include a specific call to action. Reference something forward-looking about the role or company.
- "full_text": The complete cover letter as a single formatted text block. Include:
  - "Dear Hiring Manager," (or the hiring manager's name if available in the JD)
  - The opening, body paragraphs, and closing as continuous text
  - "Sincerely," and the candidate's name

Guidelines:
- Keep it under 400 words total
- Be specific, not generic. "I increased API response time by 40%" > "I have strong technical skills"
- Show genuine interest in THIS company, not just any job
- Don't repeat the resume -- add context and narrative
"""
    return system, prompt


def revise_cover_letter_prompt(cover_letter: str, ats_feedback: str, parsed_job: str) -> tuple[str, str]:
    system = "You are an expert cover letter editor. You revise cover letters to improve keyword coverage and relevance while maintaining authentic voice."

    prompt = f"""Revise this cover letter based on the evaluation feedback.

## Current Cover Letter
{cover_letter}

## Feedback
{ats_feedback}

## Target Job
{parsed_job}

Improve the cover letter based on the feedback. Maintain the authentic voice but ensure better alignment with the target role.

Return in the SAME JSON format:
- "opening": Revised opening paragraph
- "body_paragraphs": Revised body paragraphs
- "closing": Revised closing paragraph
- "full_text": Complete revised cover letter text
"""
    return system, prompt
