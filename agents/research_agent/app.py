import streamlit as st
from orchestrator import ResearchOrchestrator
from config import DEPTH_PRESETS
from models import ResearchReport


st.set_page_config(page_title="Research Agent", page_icon="🔬", layout="wide")

st.markdown("""
<style>
    .block-container { max-width: 1100px; }
    .confidence-high { color: #155724; font-weight: 600; }
    .confidence-medium { color: #856404; font-weight: 600; }
    .confidence-low { color: #721c24; font-weight: 600; }
    .fact-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .fact-high { background: #d4edda; color: #155724; }
    .fact-medium { background: #fff3cd; color: #856404; }
    .fact-low { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)


def confidence_badge(level: str) -> str:
    cls = f"fact-{level}"
    return f'<span class="fact-badge {cls}">{level.upper()}</span>'


def generate_export(report: ResearchReport) -> str:
    lines = [f"# Research Report: {report.question}\n"]

    lines.append(f"**Confidence Level:** {report.confidence_level.upper()}\n")
    lines.append("## Executive Summary\n")
    lines.append(f"{report.executive_summary}\n")

    lines.append("## Key Findings\n")
    for f in report.key_findings:
        lines.append(f"- {f}")
    lines.append("")

    for section in report.sections:
        lines.append(f"## {section.heading}\n")
        lines.append(f"{section.content}\n")
        if section.supporting_sources:
            lines.append("**Sources:**")
            for s in section.supporting_sources:
                lines.append(f"- {s}")
            lines.append("")

    lines.append("## Sources\n")
    for i, s in enumerate(report.sources, 1):
        lines.append(f"{i}. [{s.title}]({s.url}) -- {s.used_for}")
    lines.append("")

    lines.append("## Research Process\n")
    for step in report.reasoning_trace:
        lines.append(f"**Iteration {step.iteration} - {step.phase.upper()}:** {step.summary}")
    lines.append("")

    return "\n".join(lines)


# --- Sidebar ---
with st.sidebar:
    st.title("Research Input")

    question = st.text_area(
        "Research Question",
        placeholder="What question do you want to research? Be specific for better results.",
        height=120,
    )

    depth = st.select_slider(
        "Research Depth",
        options=list(DEPTH_PRESETS.keys()),
        value="Standard",
        help="Quick: 2 loops | Standard: 3 loops | Deep: 4 loops",
    )

    can_research = bool(question and question.strip())
    research = st.button(
        "Start Research",
        type="primary",
        disabled=not can_research,
        use_container_width=True,
    )


# --- Main Area ---
st.title("Research Agent")
st.caption("Plan -> Search -> Extract -> Evaluate -> Replan -> Synthesize")

if research:
    max_iter = DEPTH_PRESETS[depth]
    orchestrator = ResearchOrchestrator()

    progress_container = st.container()
    phase_statuses = {}

    def on_phase(phase_id, phase_label):
        phase_statuses[phase_id] = progress_container.status(phase_label, expanded=True)
        # Collapse previous phases
        for pid, status in phase_statuses.items():
            if pid != phase_id:
                status.update(state="complete", expanded=False)

    def on_progress(msg):
        current = list(phase_statuses.keys())[-1] if phase_statuses else None
        if current and current in phase_statuses:
            phase_statuses[current].write(f"... {msg}")

    def on_reasoning_step(step):
        current = list(phase_statuses.keys())[-1] if phase_statuses else None
        if current and current in phase_statuses:
            phase_statuses[current].write(
                f"**{step.phase.upper()}:** {step.summary}"
            )

    try:
        report = orchestrator.run(
            question=question.strip(),
            max_iterations=max_iter,
            on_phase=on_phase,
            on_progress=on_progress,
            on_reasoning_step=on_reasoning_step,
        )

        # Mark all phases complete
        for status in phase_statuses.values():
            status.update(state="complete", expanded=False)

        st.session_state["report"] = report

    except Exception as e:
        st.error(f"Research failed: {e}")
        st.stop()


# --- Display Results ---
if "report" in st.session_state:
    report: ResearchReport = st.session_state["report"]

    st.divider()
    st.header("Research Report")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sources", len(report.sources))
    m2.metric("Key Findings", len(report.key_findings))
    m3.metric("Research Loops", max((s.iteration for s in report.reasoning_trace), default=0))
    m4.metric("Confidence", report.confidence_level.upper())

    # Executive summary
    st.info(report.executive_summary)

    # Tabs
    tab_report, tab_sources, tab_trace = st.tabs(["Report", "Sources", "Reasoning Trace"])

    with tab_report:
        # Key findings
        st.subheader("Key Findings")
        for f in report.key_findings:
            st.markdown(f"- {f}")

        st.divider()

        # Sections
        for section in report.sections:
            st.subheader(section.heading)
            st.write(section.content)
            if section.supporting_sources:
                with st.expander("Sources for this section"):
                    for s in section.supporting_sources:
                        st.markdown(f"- {s}")

    with tab_sources:
        st.subheader("All Sources")
        for i, source in enumerate(report.sources, 1):
            st.markdown(
                f"**{i}.** [{source.title}]({source.url})\n\n"
                f"  Used for: {source.used_for}"
            )
            st.divider()

    with tab_trace:
        st.subheader("Agent Reasoning Trace")
        st.caption("This shows how the agent decided what to search and when to stop.")

        current_iteration = 0
        for step in report.reasoning_trace:
            if step.iteration != current_iteration:
                current_iteration = step.iteration
                st.markdown(f"### Iteration {current_iteration}")

            with st.expander(f"{step.phase.upper()}: {step.summary}"):
                st.write(step.detail)

    # Export
    st.divider()
    export_md = generate_export(report)
    st.download_button(
        label="Download Report (.md)",
        data=export_md,
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
