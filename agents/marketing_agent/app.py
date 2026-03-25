import streamlit as st
from orchestrator import CampaignOrchestrator
from config import CAMPAIGN_GOALS
from models import CampaignPackage


st.set_page_config(page_title="Marketing Campaign Agent", page_icon="📣", layout="wide")

# --- Custom CSS ---
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


def render_scores_table(evaluation):
    cols = st.columns([2, 1, 1, 1])
    cols[0].markdown("**Piece**")
    cols[1].markdown("**Voice**")
    cols[2].markdown("**Coherence**")
    cols[3].markdown("**Channel**")

    for s in evaluation.scores:
        cols = st.columns([2, 1, 1, 1])
        cols[0].markdown(s.piece_name.replace("_", " ").title())
        cols[1].markdown(score_badge(s.voice_score), unsafe_allow_html=True)
        cols[2].markdown(score_badge(s.coherence_score), unsafe_allow_html=True)
        cols[3].markdown(score_badge(s.channel_score), unsafe_allow_html=True)


def generate_export(pkg: CampaignPackage) -> str:
    lines = ["# Marketing Campaign Package\n"]

    lines.append("## Product Intelligence Brief\n")
    lines.append(f"**Summary:** {pkg.product_brief.summary}\n")
    lines.append("**Features:**")
    for f in pkg.product_brief.features:
        lines.append(f"- {f}")
    lines.append("\n**Value Propositions:**")
    for v in pkg.product_brief.value_propositions:
        lines.append(f"- {v}")
    lines.append(f"\n**Messaging Tone:** {pkg.product_brief.messaging_tone}\n")

    lines.append("---\n## Competitive Analysis\n")
    for c in pkg.competitive_analysis.competitors:
        lines.append(f"### {c.name} ({c.url})")
        lines.append(f"**Positioning:** {c.positioning}")
        lines.append(f"**Messaging:** {c.messaging_approach}")
        lines.append("**Strengths:** " + ", ".join(c.strengths) + "\n")
    lines.append("**Gaps:** " + ", ".join(pkg.competitive_analysis.gaps))
    lines.append("**Opportunities:** " + ", ".join(pkg.competitive_analysis.opportunities) + "\n")

    lines.append("---\n## Brand Positioning\n")
    lines.append(f"**Statement:** {pkg.positioning.statement}\n")
    lines.append("**Key Messages:**")
    for m in pkg.positioning.key_messages:
        lines.append(f"- {m}")
    lines.append("\n**Differentiators:**")
    for d in pkg.positioning.differentiators:
        lines.append(f"- {d}")
    lines.append("")

    lines.append("---\n## Brand Voice Guide\n")
    lines.append("**Tone:** " + " | ".join(pkg.voice_guide.tone_attributes))
    lines.append("\n**Do's:**")
    for d in pkg.voice_guide.dos:
        lines.append(f"- {d}")
    lines.append("\n**Don'ts:**")
    for d in pkg.voice_guide.donts:
        lines.append(f"- {d}")
    lines.append("\n**Words to Avoid:** " + ", ".join(pkg.voice_guide.words_to_avoid))
    lines.append("")

    lines.append("---\n## LinkedIn Posts\n")
    for i, post in enumerate(pkg.content.linkedin_posts, 1):
        lines.append(f"### Post {i} — {post.angle.replace('_', ' ').title()}\n")
        lines.append(f"**Hook:** {post.hook}\n")
        lines.append(post.body + "\n")
        lines.append(f"**CTA:** {post.cta}\n")

    lines.append("---\n## Twitter/X Thread\n")
    for i, tweet in enumerate(pkg.content.twitter_thread.tweets, 1):
        lines.append(f"**{i}.** {tweet}\n")

    lines.append("---\n## Email Sequence\n")
    for i, email in enumerate(pkg.content.email_sequence.emails, 1):
        lines.append(f"### Email {i}\n")
        lines.append(f"**Subject:** {email.subject}")
        lines.append(f"**Preview:** {email.preview_text}\n")
        lines.append(email.body + "\n")
        lines.append(f"**CTA:** {email.cta}\n")

    lines.append("---\n## Blog Post Outline\n")
    lines.append(f"### {pkg.content.blog_outline.title}\n")
    lines.append(f"{pkg.content.blog_outline.intro}\n")
    for section in pkg.content.blog_outline.sections:
        lines.append(f"#### {section.heading}")
        lines.append(f"_{section.summary}_\n")
        for pt in section.key_points:
            lines.append(f"- {pt}")
        lines.append("")
    lines.append(f"**Conclusion:** {pkg.content.blog_outline.conclusion}\n")

    lines.append("---\n## Ad Copy Variations\n")
    for i, ad in enumerate(pkg.content.ad_copies, 1):
        lines.append(f"### Variation {i}")
        lines.append(f"**Headline:** {ad.headline}")
        lines.append(f"**Body:** {ad.body}")
        lines.append(f"**CTA:** {ad.cta}\n")

    lines.append("---\n## Quality Scores\n")
    for s in pkg.evaluation.scores:
        lines.append(f"- **{s.piece_name}**: Voice {s.voice_score}/10 | Coherence {s.coherence_score}/10 | Channel {s.channel_score}/10")
    lines.append(f"\n**Overall:** {pkg.evaluation.overall_feedback}")

    return "\n".join(lines)


# --- Sidebar: Input Form ---
with st.sidebar:
    st.title("Campaign Input")

    product_url = st.text_input("Product/Company URL", placeholder="https://yourproduct.com")
    product_description = st.text_area("Brief Product Description", placeholder="What does your product do? (1-2 sentences)", height=80)
    target_audience = st.text_input("Target Audience", placeholder="e.g., Startup CTOs, fitness-conscious millennials")

    st.markdown("**Competitor URLs** (at least 1)")
    comp1 = st.text_input("Competitor 1", placeholder="https://competitor1.com", key="comp1")
    comp2 = st.text_input("Competitor 2 (optional)", placeholder="https://competitor2.com", key="comp2")
    comp3 = st.text_input("Competitor 3 (optional)", placeholder="https://competitor3.com", key="comp3")

    campaign_goal = st.selectbox("Campaign Goal", CAMPAIGN_GOALS)

    can_launch = product_url and product_description and target_audience and comp1
    launch = st.button("Launch Campaign", type="primary", disabled=not can_launch, use_container_width=True)


# --- Main Area ---
st.title("Marketing Campaign Agent")
st.caption("Research → Position → Strategize → Create → Evaluate → Deliver")

if launch:
    competitor_urls = [u for u in [comp1, comp2, comp3] if u and u.strip()]
    orchestrator = CampaignOrchestrator()

    progress_container = st.container()
    phase_statuses = {}

    def on_phase(phase_name):
        phase_statuses[phase_name] = progress_container.status(
            {
                "research": "Phase 1: Research",
                "strategy": "Phase 2: Strategy",
                "content": "Phase 3: Content Creation",
                "evaluation": "Phase 4: Evaluation",
                "delivery": "Phase 5: Delivery",
            }[phase_name],
            expanded=True,
        )
        # Collapse previous phase
        for name, status in phase_statuses.items():
            if name != phase_name:
                status.update(state="complete", expanded=False)

    current_status_text = [None]

    def on_progress(msg):
        current_phase = list(phase_statuses.keys())[-1] if phase_statuses else None
        if current_phase and current_phase in phase_statuses:
            phase_statuses[current_phase].write(f"⏳ {msg}")

    try:
        package = orchestrator.run(
            product_url=product_url,
            product_description=product_description,
            target_audience=target_audience,
            competitor_urls=competitor_urls,
            campaign_goal=campaign_goal,
            on_phase=on_phase,
            on_progress=on_progress,
        )

        # Mark final phase complete
        for status in phase_statuses.values():
            status.update(state="complete", expanded=False)

        st.session_state["campaign"] = package

    except Exception as e:
        st.error(f"Campaign generation failed: {e}")
        st.stop()


# --- Display Results ---
if "campaign" in st.session_state:
    pkg: CampaignPackage = st.session_state["campaign"]

    st.divider()
    st.header("Campaign Dashboard")

    # Quality overview
    avg_voice = sum(s.voice_score for s in pkg.evaluation.scores) / len(pkg.evaluation.scores)
    avg_coherence = sum(s.coherence_score for s in pkg.evaluation.scores) / len(pkg.evaluation.scores)
    avg_channel = sum(s.channel_score for s in pkg.evaluation.scores) / len(pkg.evaluation.scores)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Content Pieces", len(pkg.evaluation.scores))
    m2.metric("Avg Voice Score", f"{avg_voice:.1f}/10")
    m3.metric("Avg Coherence", f"{avg_coherence:.1f}/10")
    m4.metric("Avg Channel Fit", f"{avg_channel:.1f}/10")

    st.caption(f"📝 {pkg.evaluation.overall_feedback}")

    # Tabs for content
    tab_research, tab_strategy, tab_linkedin, tab_twitter, tab_email, tab_blog, tab_ads, tab_scores = st.tabs(
        ["Research", "Strategy", "LinkedIn", "Twitter/X", "Email", "Blog", "Ads", "Scores"]
    )

    with tab_research:
        st.subheader("Product Intelligence Brief")
        st.write(pkg.product_brief.summary)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Features**")
            for f in pkg.product_brief.features:
                st.markdown(f"- {f}")
        with col2:
            st.markdown("**Value Propositions**")
            for v in pkg.product_brief.value_propositions:
                st.markdown(f"- {v}")

        st.subheader("Competitive Analysis")
        for comp in pkg.competitive_analysis.competitors:
            with st.expander(f"{comp.name} — {comp.url}"):
                st.write(f"**Positioning:** {comp.positioning}")
                st.write(f"**Messaging:** {comp.messaging_approach}")
                st.write("**Strengths:** " + ", ".join(comp.strengths))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Gaps**")
            for g in pkg.competitive_analysis.gaps:
                st.markdown(f"- {g}")
        with col2:
            st.markdown("**Opportunities**")
            for o in pkg.competitive_analysis.opportunities:
                st.markdown(f"- {o}")

    with tab_strategy:
        st.subheader("Brand Positioning")
        st.info(pkg.positioning.statement)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Key Messages**")
            for m in pkg.positioning.key_messages:
                st.markdown(f"- {m}")
            st.markdown("**Differentiators**")
            for d in pkg.positioning.differentiators:
                st.markdown(f"- {d}")
        with col2:
            st.markdown("**Proof Points**")
            for p in pkg.positioning.proof_points:
                st.markdown(f"- {p}")

        st.subheader("Brand Voice Guide")
        st.write("**Tone:** " + " | ".join(pkg.voice_guide.tone_attributes))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Do's**")
            for d in pkg.voice_guide.dos:
                st.markdown(f"✅ {d}")
        with col2:
            st.markdown("**Don'ts**")
            for d in pkg.voice_guide.donts:
                st.markdown(f"❌ {d}")
        st.markdown("**Words to Avoid:** " + ", ".join(f"`{w}`" for w in pkg.voice_guide.words_to_avoid))

    with tab_linkedin:
        for i, post in enumerate(pkg.content.linkedin_posts, 1):
            st.subheader(f"Post {i} — {post.angle.replace('_', ' ').title()}")
            st.markdown(f"**{post.hook}**")
            st.write(post.body)
            st.caption(f"CTA: {post.cta}")
            st.divider()

    with tab_twitter:
        st.subheader("Tweet Thread")
        for i, tweet in enumerate(pkg.content.twitter_thread.tweets, 1):
            st.markdown(f"**{i}.** {tweet}")

    with tab_email:
        for i, email in enumerate(pkg.content.email_sequence.emails, 1):
            st.subheader(f"Email {i}")
            st.markdown(f"**Subject:** {email.subject}")
            st.caption(f"Preview: {email.preview_text}")
            st.write(email.body)
            st.info(f"CTA: {email.cta}")
            st.divider()

    with tab_blog:
        st.subheader(pkg.content.blog_outline.title)
        st.write(pkg.content.blog_outline.intro)
        for section in pkg.content.blog_outline.sections:
            with st.expander(section.heading):
                st.caption(section.summary)
                for pt in section.key_points:
                    st.markdown(f"- {pt}")
        st.write(f"**Conclusion:** {pkg.content.blog_outline.conclusion}")

    with tab_ads:
        cols = st.columns(3)
        for i, ad in enumerate(pkg.content.ad_copies):
            with cols[i]:
                st.subheader(f"Variation {i + 1}")
                st.markdown(f"### {ad.headline}")
                st.write(ad.body)
                st.button(ad.cta, key=f"ad_cta_{i}", disabled=True)

    with tab_scores:
        st.subheader("Quality Scores")
        render_scores_table(pkg.evaluation)
        st.caption(f"Overall: {pkg.evaluation.overall_feedback}")

    # Export
    st.divider()
    export_md = generate_export(pkg)
    st.download_button(
        label="Download Campaign Package (.md)",
        data=export_md,
        file_name="marketing_campaign.md",
        mime="text/markdown",
        use_container_width=True,
    )
