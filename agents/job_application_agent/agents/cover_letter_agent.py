from gemini_client import GeminiClient
from config import CREATIVE_TEMPERATURE
from models import ParsedJob, ParsedResume, GapAnalysis, CompanyIntel, CoverLetter
from prompts.cover_letter_prompts import cover_letter_prompt, revise_cover_letter_prompt


def write_cover_letter(
    client: GeminiClient,
    parsed_job: ParsedJob,
    parsed_resume: ParsedResume,
    gap_analysis: GapAnalysis,
    company_intel: CompanyIntel,
) -> CoverLetter:
    job_text = parsed_job.model_dump_json(indent=2)
    resume_text = parsed_resume.model_dump_json(indent=2)
    gap_text = gap_analysis.model_dump_json(indent=2)
    company_text = company_intel.model_dump_json(indent=2)

    system, prompt = cover_letter_prompt(job_text, resume_text, gap_text, company_text)
    data = client.generate_json(prompt, system, temperature=CREATIVE_TEMPERATURE)

    return CoverLetter(**data)


def revise_cover_letter(
    client: GeminiClient,
    cover_letter: CoverLetter,
    ats_feedback: str,
    parsed_job: ParsedJob,
) -> CoverLetter:
    cl_text = cover_letter.model_dump_json(indent=2)
    job_text = parsed_job.model_dump_json(indent=2)

    system, prompt = revise_cover_letter_prompt(cl_text, ats_feedback, job_text)
    data = client.generate_json(prompt, system, temperature=CREATIVE_TEMPERATURE)

    return CoverLetter(**data)
