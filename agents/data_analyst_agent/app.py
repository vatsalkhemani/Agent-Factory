import io

import pandas as pd
import streamlit as st

from orchestrator import AnalysisOrchestrator
from chart_builder import build_chart
from models import AnalysisReport


st.set_page_config(page_title="Data Analyst Agent", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .block-container { max-width: 1200px; }
    .finding-high { border-left: 4px solid #28a745; padding-left: 12px; margin-bottom: 16px; }
    .finding-medium { border-left: 4px solid #ffc107; padding-left: 12px; margin-bottom: 16px; }
    .finding-low { border-left: 4px solid #6c757d; padding-left: 12px; margin-bottom: 16px; }
    .importance-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .imp-high { background: #d4edda; color: #155724; }
    .imp-medium { background: #fff3cd; color: #856404; }
    .imp-low { background: #e2e3e5; color: #383d41; }
</style>
""", unsafe_allow_html=True)


def importance_badge(level: str) -> str:
    return f'<span class="importance-badge imp-{level}">{level.upper()}</span>'


def load_csv(uploaded_file) -> pd.DataFrame:
    """Load CSV with smart type inference and encoding fallback."""
    content = uploaded_file.getvalue()

    # Try UTF-8 first, then latin-1
    for encoding in ["utf-8", "latin-1"]:
        try:
            df = pd.read_csv(
                io.BytesIO(content),
                encoding=encoding,
                sep=None,
                engine="python",
                on_bad_lines="skip",
            )
            break
        except Exception:
            continue
    else:
        raise ValueError("Could not parse CSV with UTF-8 or Latin-1 encoding")

    # Smart type coercion
    for col in df.columns:
        # Try numeric
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.notna().sum() > 0.5 * len(df):
            df[col] = numeric
            continue

        # Try datetime
        try:
            dt = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            if dt.notna().sum() > 0.5 * len(df):
                df[col] = dt
                continue
        except Exception:
            pass

    return df


def generate_export(report: AnalysisReport) -> str:
    lines = ["# Data Analysis Report\n"]

    lines.append(f"## Dataset Summary\n{report.dataset_summary}\n")

    lines.append("## Key Findings\n")
    for i, f in enumerate(report.key_findings, 1):
        lines.append(f"### {i}. {f.title} [{f.importance.upper()}]")
        lines.append(f"\n{f.description}\n")
        lines.append(f"*Supporting data: {f.supporting_data}*\n")

    lines.append("## Full Analysis\n")
    lines.append(report.narrative + "\n")

    lines.append("## Methodology\n")
    for note in report.methodology_notes:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## Data Profile\n")
    lines.append(f"- Rows: {report.data_profile.row_count}")
    lines.append(f"- Columns: {report.data_profile.column_count}")
    if report.data_profile.sampled:
        lines.append("- *Note: Dataset was sampled for analysis*")
    lines.append("")

    for col in report.data_profile.columns:
        line = f"- **{col.name}** ({col.dtype}): {col.non_null_count} non-null, {col.unique_count} unique"
        if col.dtype == "numeric":
            line += f" | mean={col.mean}, std={col.std}"
        lines.append(line)

    return "\n".join(lines)


# --- Sidebar ---
with st.sidebar:
    st.title("Data Input")

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        help="Upload a CSV file (max 50MB). The agent will autonomously analyze it.",
    )

    user_context = st.text_input(
        "Context (optional)",
        placeholder="e.g., 'This is sales data from 2023'",
        help="Optional hint about what the data represents. The agent works without this.",
    )

    if uploaded_file:
        st.caption(f"File: {uploaded_file.name} ({uploaded_file.size / 1024:.0f} KB)")

    can_analyze = uploaded_file is not None
    analyze = st.button(
        "Analyze Data",
        type="primary",
        disabled=not can_analyze,
        use_container_width=True,
    )


# --- Main Area ---
st.title("Data Analyst Agent")
st.caption("Profile -> Hypothesize -> Analyze -> Deep Dive -> Visualize -> Synthesize")

if analyze and uploaded_file:
    try:
        df = load_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not load CSV: {e}")
        st.stop()

    if len(df) == 0:
        st.error("The uploaded CSV is empty.")
        st.stop()

    # Show preview
    with st.expander("Data Preview", expanded=False):
        st.dataframe(df.head(10))

    orchestrator = AnalysisOrchestrator()

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
        report = orchestrator.run(
            df=df,
            user_context=user_context,
            on_phase=on_phase,
            on_progress=on_progress,
        )

        for status in phase_statuses.values():
            status.update(state="complete", expanded=False)

        st.session_state["analysis_report"] = report
        st.session_state["analysis_df"] = df

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()


# --- Display Results ---
if "analysis_report" in st.session_state:
    report: AnalysisReport = st.session_state["analysis_report"]
    df = st.session_state.get("analysis_df")

    st.divider()
    st.header("Analysis Report")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{report.data_profile.row_count:,}")
    m2.metric("Columns", report.data_profile.column_count)
    m3.metric("Key Findings", len(report.key_findings))
    high_count = sum(1 for f in report.key_findings if f.importance == "high")
    m4.metric("High Importance", high_count)

    # Summary
    st.info(report.dataset_summary)

    # Tabs
    tab_findings, tab_charts, tab_report, tab_profile = st.tabs(
        ["Key Findings", "Charts", "Full Report", "Data Profile"]
    )

    with tab_findings:
        for i, finding in enumerate(report.key_findings):
            st.markdown(
                f'<div class="finding-{finding.importance}">'
                f'{importance_badge(finding.importance)} '
                f'<strong>{finding.title}</strong></div>',
                unsafe_allow_html=True,
            )
            st.write(finding.description)
            st.caption(f"Data: {finding.supporting_data}")
            st.divider()

    with tab_charts:
        if df is not None:
            chart_count = 0
            for finding in report.key_findings:
                if finding.chart_spec:
                    fig = build_chart(df, finding.chart_spec)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(finding.title)
                        st.divider()
                        chart_count += 1

            if chart_count == 0:
                st.info("No charts were generated for this analysis.")
        else:
            st.warning("DataFrame not available for charting.")

    with tab_report:
        st.markdown(report.narrative)

        if report.methodology_notes:
            st.divider()
            st.subheader("Methodology")
            for note in report.methodology_notes:
                st.markdown(f"- {note}")

    with tab_profile:
        st.subheader("Column Profiles")

        for col in report.data_profile.columns:
            with st.expander(f"{col.name} ({col.dtype})"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Non-null:** {col.non_null_count}")
                    st.markdown(f"**Null:** {col.null_count}")
                    st.markdown(f"**Unique:** {col.unique_count}")
                with c2:
                    if col.dtype == "numeric":
                        st.markdown(f"**Mean:** {col.mean}")
                        st.markdown(f"**Median:** {col.median}")
                        st.markdown(f"**Std:** {col.std}")
                        st.markdown(f"**Range:** [{col.min_val}, {col.max_val}]")
                    elif col.dtype == "categorical" and col.top_values:
                        st.markdown("**Top Values:**")
                        for v, c in zip(col.top_values[:5], col.top_counts[:5]):
                            st.markdown(f"  - {v}: {c}")
                st.markdown(f"**Samples:** {', '.join(col.sample_values)}")

        if report.data_profile.data_quality_notes:
            st.divider()
            st.subheader("Data Quality Notes")
            for note in report.data_profile.data_quality_notes:
                st.warning(note)

    # Export
    st.divider()
    export_md = generate_export(report)
    st.download_button(
        label="Download Report (.md)",
        data=export_md,
        file_name="data_analysis_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
