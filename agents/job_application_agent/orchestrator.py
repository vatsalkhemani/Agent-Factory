from gemini_client import GeminiClient
from config import REVISION_THRESHOLD, MAX_REVISIONS
from models import ApplicationPackage
from agents.parser_agent import parse_job, parse_resume
from agents.gap_agent import analyze_gaps
from agents.researcher_agent import research_company
from agents.tailor_agent import tailor_resume, revise_resume
from agents.cover_letter_agent import write_cover_letter, revise_cover_letter
from agents.evaluator_agent import evaluate_ats


class ApplicationOrchestrator:
    def __init__(self):
        self.client = GeminiClient()

    def run(
        self,
        job_text: str,
        resume_text: str,
        on_phase=None,
        on_progress=None,
    ) -> ApplicationPackage:

        # --- Phase 1: Parse ---
        if on_phase:
            on_phase("parse", "Phase 1: Parsing Documents")

        if on_progress:
            on_progress("Parsing job description...")
        parsed_job = parse_job(self.client, job_text)

        if on_progress:
            on_progress("Parsing resume...")
        parsed_resume = parse_resume(self.client, resume_text)

        if on_progress:
            on_progress(f"Detected: {parsed_job.title} at {parsed_job.company_name}")

        # --- Phase 2: Gap Analysis ---
        if on_phase:
            on_phase("gap", "Phase 2: Gap Analysis")

        if on_progress:
            on_progress("Analyzing skill gaps and alignment...")
        gap_analysis = analyze_gaps(self.client, parsed_job, parsed_resume)

        if on_progress:
            on_progress(f"Alignment: {gap_analysis.experience_alignment} | {len(gap_analysis.matching_skills)} matching, {len(gap_analysis.missing_skills)} missing")

        # --- Phase 3: Company Research ---
        if on_phase:
            on_phase("research", "Phase 3: Company Research")

        if on_progress:
            on_progress(f"Researching {parsed_job.company_name}...")
        company_intel = research_company(
            self.client, parsed_job.company_name, parsed_job.company_url
        )

        if on_progress:
            on_progress(f"Found: {company_intel.industry} | {len(company_intel.talking_points)} talking points")

        # --- Phase 4: Tailor Resume ---
        if on_phase:
            on_phase("tailor", "Phase 4: Tailoring Resume")

        if on_progress:
            on_progress("Rewriting resume for target role...")
        tailored_resume = tailor_resume(
            self.client, parsed_resume, parsed_job, gap_analysis, company_intel
        )

        if on_progress:
            on_progress(f"Added {len(tailored_resume.keywords_added)} keywords from JD")

        # --- Phase 5: Cover Letter ---
        if on_phase:
            on_phase("cover_letter", "Phase 5: Writing Cover Letter")

        if on_progress:
            on_progress("Writing personalized cover letter...")
        cover_letter = write_cover_letter(
            self.client, parsed_job, parsed_resume, gap_analysis, company_intel
        )

        # --- Phase 6: ATS Evaluation ---
        if on_phase:
            on_phase("evaluate", "Phase 6: ATS Evaluation")

        if on_progress:
            on_progress("Scoring against ATS criteria...")
        ats_score = evaluate_ats(
            self.client, tailored_resume, cover_letter, parsed_job
        )

        if on_progress:
            on_progress(f"ATS Score: {ats_score.overall_score}/10 | Keywords: {ats_score.keyword_match_score}/10 | Relevance: {ats_score.relevance_score}/10")

        # --- Phase 7: Revision (conditional) ---
        if ats_score.needs_revision and ats_score.overall_score < REVISION_THRESHOLD:
            if on_phase:
                on_phase("revise", "Phase 7: Auto-Revision")

            if on_progress:
                on_progress(f"Score {ats_score.overall_score}/10 below threshold. Revising...")

            # Revise resume
            if on_progress:
                on_progress("Revising resume based on ATS feedback...")
            tailored_resume = revise_resume(
                self.client, tailored_resume, ats_score.feedback, parsed_job
            )

            # Revise cover letter
            if on_progress:
                on_progress("Revising cover letter...")
            cover_letter = revise_cover_letter(
                self.client, cover_letter, ats_score.feedback, parsed_job
            )

            # Re-evaluate
            if on_progress:
                on_progress("Re-evaluating after revision...")
            ats_score = evaluate_ats(
                self.client, tailored_resume, cover_letter, parsed_job
            )

            if on_progress:
                on_progress(f"Revised ATS Score: {ats_score.overall_score}/10")

        # --- Package ---
        if on_phase:
            on_phase("complete", "Complete")

        return ApplicationPackage(
            parsed_job=parsed_job,
            parsed_resume=parsed_resume,
            gap_analysis=gap_analysis,
            company_intel=company_intel,
            tailored_resume=tailored_resume,
            cover_letter=cover_letter,
            original_resume_text=resume_text,
            ats_score=ats_score,
        )
