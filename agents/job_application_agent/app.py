import streamlit as st
from orchestrator import ApplicationOrchestrator
from models import ApplicationPackage


st.set_page_config(page_title="Job Application Agent", page_icon="📋", layout="wide")

st.markdown("""
<style>
    .block-container { max-width: 1100px; }
    .score-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85em;
    }
    .score-high { background: #d4edda; color: #155724; }
    .score-mid { background: #fff3cd; color: #856404; }
    .score-low { background: #f8d7da; color: #721c24; }
    .match-tag { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 8px; font-size: 0.85em; margin: 2px; display: inline-block; }
    .gap-tag { background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 8px; font-size: 0.85em; margin: 2px; display: inline-block; }
    .transfer-tag { background: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 8px; font-size: 0.85em; margin: 2px; display: inline-block; }
</style>
""", unsafe_allow_html=True)


def score_badge(score: int) -> str:
    if score >= 8:
        cls = "score-high"
    elif score >= 7:
        cls = "score-mid"
    else:
        cls = "score-low"
    return f'<span class="score-badge {cls}">{score}/10</span>'


def generate_resume_export(pkg: ApplicationPackage) -> str:
    lines = [f"# Tailored Resume -- {pkg.parsed_job.title} at {pkg.parsed_job.company_name}\n"]

    lines.append(f"## Professional Summary\n{pkg.tailored_resume.summary}\n")

    lines.append("## Skills\n")
    lines.append(", ".join(pkg.tailored_resume.skills_section) + "\n")

    lines.append("## Experience\n")
    for exp in pkg.tailored_resume.experience_bullets:
        lines.append(f"### {exp.title} | {exp.company}\n")
        for b in exp.bullets:
            lines.append(f"- {b}")
        lines.append("")

    return "\n".join(lines)


def generate_cover_letter_export(pkg: ApplicationPackage) -> str:
    return f"# Cover Letter -- {pkg.parsed_job.title} at {pkg.parsed_job.company_name}\n\n{pkg.cover_letter.full_text}"


# --- Sidebar ---
with st.sidebar:
    st.title("Application Input")

    job_text = st.text_area(
        "Job Description",
        placeholder="Paste the full job description here...",
        height=250,
    )

    resume_text = st.text_area(
        "Your Resume",
        placeholder="Paste your resume text here...",
        height=250,
    )

    can_analyze = bool(job_text and job_text.strip() and resume_text and resume_text.strip())
    analyze = st.button(
        "Analyze & Tailor",
        type="primary",
        disabled=not can_analyze,
        use_container_width=True,
    )


# --- Main Area ---
st.title("Job Application Agent")
st.caption("Parse -> Gap Analysis -> Company Research -> Tailor -> Cover Letter -> ATS Evaluation -> Revise")

if analyze:
    orchestrator = ApplicationOrchestrator()

    progress_container = st.container()
    phase_statuses = {}

    def on_phase(phase_id, phase_label):
        phase_statuses[phase_id] = progress_container.status(phase_label, expanded=True)
        for pid, status in phase_statuses.items():
            if pid != phase_id:
                status.update(state="complete", expanded=False)

    def on_progress(msg):
        current = list(phase_statuses.keys())[-1] if phase_statuses else None
        if current and current in phase_statuses:
            phase_statuses[current].write(f"... {msg}")

    try:
        package = orchestrator.run(
            job_text=job_text.strip(),
            resume_text=resume_text.strip(),
            on_phase=on_phase,
            on_progress=on_progress,
        )

        for status in phase_statuses.values():
            status.update(state="complete", expanded=False)

        st.session_state["application"] = package

    except Exception as e:
        st.error(f"Application analysis failed: {e}")
        st.stop()


# --- Display Results ---
if "application" in st.session_state:
    pkg: ApplicationPackage = st.session_state["application"]

    st.divider()
    st.header("Application Package")

    # Top metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ATS Score", f"{pkg.ats_score.overall_score}/10")
    m2.metric("Keyword Match", f"{pkg.ats_score.keyword_match_score}/10")
    m3.metric("Relevance", f"{pkg.ats_score.relevance_score}/10")
    m4.metric("Alignment", pkg.gap_analysis.experience_alignment.title())

    # Tabs
    tab_gap, tab_resume, tab_cover, tab_company, tab_ats = st.tabs(
        ["Gap Analysis", "Tailored Resume", "Cover Letter", "Company Intel", "ATS Evaluation"]
    )

    with tab_gap:
        st.subheader("Skills Gap Analysis")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**You Have (Matching Skills)**")
            for s in pkg.gap_analysis.matching_skills:
                st.markdown(f'<span class="match-tag">{s}</span>', unsafe_allow_html=True)

        with col2:
            st.markdown("**You Need (Missing Skills)**")
            for s in pkg.gap_analysis.missing_skills:
                st.markdown(f'<span class="gap-tag">{s}</span>', unsafe_allow_html=True)

        st.divider()
        st.subheader("Transferable Skills")
        for t in pkg.gap_analysis.transferable_skills:
            st.markdown(
                f'<span class="transfer-tag">{t.resume_skill}</span> '
                f'maps to **{t.maps_to}** ({t.strength})',
                unsafe_allow_html=True,
            )

        st.divider()
        st.subheader("Priority Areas for Tailoring")
        for p in pkg.gap_analysis.priority_areas:
            st.markdown(f"- {p}")

    with tab_resume:
        st.subheader("Tailored Resume")

        col_orig, col_new = st.columns(2)
        with col_orig:
            st.markdown("**Original Resume**")
            st.text_area("", value=pkg.original_resume_text, height=400, disabled=True, key="orig_resume")

        with col_new:
            st.markdown("**Tailored Version**")

            st.markdown(f"**Summary:** {pkg.tailored_resume.summary}")
            st.markdown("**Skills:** " + " | ".join(pkg.tailored_resume.skills_section))

            for exp in pkg.tailored_resume.experience_bullets:
                with st.expander(f"{exp.title} at {exp.company}"):
                    for b in exp.bullets:
                        st.markdown(f"- {b}")

        st.divider()
        st.markdown("**Keywords Added from JD:**")
        kw_text = " | ".join(f"`{k}`" for k in pkg.tailored_resume.keywords_added)
        st.markdown(kw_text)

    with tab_cover:
        st.subheader("Cover Letter")
        st.write(pkg.cover_letter.full_text)

        st.divider()
        with st.expander("Cover Letter Structure"):
            st.markdown("**Opening:**")
            st.write(pkg.cover_letter.opening)
            for i, para in enumerate(pkg.cover_letter.body_paragraphs, 1):
                st.markdown(f"**Body Paragraph {i}:**")
                st.write(para)
            st.markdown("**Closing:**")
            st.write(pkg.cover_letter.closing)

    with tab_company:
        st.subheader(f"Company Intelligence: {pkg.company_intel.company_name}")

        st.markdown(f"**Industry:** {pkg.company_intel.industry}")
        st.markdown(f"**Mission/Values:** {pkg.company_intel.mission_or_values}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Culture Signals**")
            for c in pkg.company_intel.culture_signals:
                st.markdown(f"- {c}")
        with col2:
            st.markdown("**Recent News**")
            for n in pkg.company_intel.recent_news:
                st.markdown(f"- {n}")

        st.divider()
        st.subheader("Talking Points for Your Application")
        for tp in pkg.company_intel.talking_points:
            st.markdown(f"- {tp}")

    with tab_ats:
        st.subheader("ATS Evaluation")

        cols = st.columns(4)
        cols[0].markdown("**Keyword Match**")
        cols[0].markdown(score_badge(pkg.ats_score.keyword_match_score), unsafe_allow_html=True)
        cols[1].markdown("**Format**")
        cols[1].markdown(score_badge(pkg.ats_score.format_score), unsafe_allow_html=True)
        cols[2].markdown("**Relevance**")
        cols[2].markdown(score_badge(pkg.ats_score.relevance_score), unsafe_allow_html=True)
        cols[3].markdown("**Overall**")
        cols[3].markdown(score_badge(pkg.ats_score.overall_score), unsafe_allow_html=True)

        st.divider()
        st.markdown("**Feedback:**")
        st.write(pkg.ats_score.feedback)

        if pkg.ats_score.missing_keywords:
            st.divider()
            st.markdown("**Missing Keywords:**")
            for kw in pkg.ats_score.missing_keywords:
                st.markdown(f'<span class="gap-tag">{kw}</span>', unsafe_allow_html=True)

    # Export
    st.divider()
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="Download Tailored Resume (.md)",
            data=generate_resume_export(pkg),
            file_name="tailored_resume.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_dl2:
        st.download_button(
            label="Download Cover Letter (.md)",
            data=generate_cover_letter_export(pkg),
            file_name="cover_letter.md",
            mime="text/markdown",
            use_container_width=True,
        )
