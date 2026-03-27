from gemini_client import GeminiClient
from config import ANALYSIS_TEMPERATURE
from models import ParsedJob, ParsedResume, Experience
from prompts.parser_prompts import parse_job_prompt, parse_resume_prompt


def parse_job(client: GeminiClient, job_text: str) -> ParsedJob:
    system, prompt = parse_job_prompt(job_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)
    return ParsedJob(**data)


def parse_resume(client: GeminiClient, resume_text: str) -> ParsedResume:
    system, prompt = parse_resume_prompt(resume_text)
    data = client.generate_json(prompt, system, temperature=ANALYSIS_TEMPERATURE)

    # Handle experiences list -- each item needs to be an Experience
    experiences = []
    for exp in data.get("experiences", []):
        try:
            experiences.append(Experience(**exp))
        except Exception:
            continue
    data["experiences"] = experiences

    return ParsedResume(**data)
