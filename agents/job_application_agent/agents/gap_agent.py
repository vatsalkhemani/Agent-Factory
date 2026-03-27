from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import ParsedJob, ParsedResume, GapAnalysis, SkillMapping
from prompts.gap_prompts import gap_analysis_prompt


def analyze_gaps(client: GeminiClient, parsed_job: ParsedJob, parsed_resume: ParsedResume) -> GapAnalysis:
    job_text = parsed_job.model_dump_json(indent=2)
    resume_text = parsed_resume.model_dump_json(indent=2)

    system, prompt = gap_analysis_prompt(job_text, resume_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    # Parse transferable skills
    transferable = []
    for t in data.get("transferable_skills", []):
        try:
            transferable.append(SkillMapping(**t))
        except Exception:
            continue
    data["transferable_skills"] = transferable

    return GapAnalysis(**data)
