from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import ParsedJob, TailoredResume, CoverLetter, ATSScore
from prompts.evaluator_prompts import ats_evaluation_prompt


def evaluate_ats(
    client: GeminiClient,
    tailored_resume: TailoredResume,
    cover_letter: CoverLetter,
    parsed_job: ParsedJob,
) -> ATSScore:
    resume_text = tailored_resume.model_dump_json(indent=2)
    cl_text = cover_letter.full_text
    job_text = parsed_job.model_dump_json(indent=2)

    system, prompt = ats_evaluation_prompt(resume_text, cl_text, job_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    return ATSScore(
        keyword_match_score=int(data.get("keyword_match_score", 5)),
        format_score=int(data.get("format_score", 5)),
        relevance_score=int(data.get("relevance_score", 5)),
        overall_score=int(data.get("overall_score", 5)),
        missing_keywords=data.get("missing_keywords", []),
        feedback=data.get("feedback", ""),
        needs_revision=data.get("needs_revision", False),
    )
