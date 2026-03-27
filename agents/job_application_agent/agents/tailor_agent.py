from gemini_client import GeminiClient
from config import CREATIVE_TEMPERATURE
from models import (
    ParsedJob, ParsedResume, GapAnalysis, CompanyIntel,
    TailoredResume, ExperienceBullets,
)
from prompts.tailor_prompts import tailor_resume_prompt, revise_resume_prompt


def tailor_resume(
    client: GeminiClient,
    parsed_resume: ParsedResume,
    parsed_job: ParsedJob,
    gap_analysis: GapAnalysis,
    company_intel: CompanyIntel,
) -> TailoredResume:
    resume_text = parsed_resume.model_dump_json(indent=2)
    job_text = parsed_job.model_dump_json(indent=2)
    gap_text = gap_analysis.model_dump_json(indent=2)
    company_text = company_intel.model_dump_json(indent=2)

    system, prompt = tailor_resume_prompt(resume_text, job_text, gap_text, company_text)
    data = client.generate_json(prompt, system, temperature=CREATIVE_TEMPERATURE)

    # Parse experience bullets
    exp_bullets = []
    for eb in data.get("experience_bullets", []):
        try:
            exp_bullets.append(ExperienceBullets(**eb))
        except Exception:
            continue
    data["experience_bullets"] = exp_bullets

    return TailoredResume(**data)


def revise_resume(
    client: GeminiClient,
    tailored_resume: TailoredResume,
    ats_feedback: str,
    parsed_job: ParsedJob,
) -> TailoredResume:
    resume_text = tailored_resume.model_dump_json(indent=2)
    job_text = parsed_job.model_dump_json(indent=2)

    system, prompt = revise_resume_prompt(resume_text, ats_feedback, job_text)
    data = client.generate_json(prompt, system, temperature=CREATIVE_TEMPERATURE)

    exp_bullets = []
    for eb in data.get("experience_bullets", []):
        try:
            exp_bullets.append(ExperienceBullets(**eb))
        except Exception:
            continue
    data["experience_bullets"] = exp_bullets

    return TailoredResume(**data)
