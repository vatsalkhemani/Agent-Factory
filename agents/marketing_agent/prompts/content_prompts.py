CONTENT_CONTEXT = """## Product Brief
{product_brief}

## Brand Positioning
{positioning}

## Brand Voice Guide
{voice_guide}

## Target Audience
{target_audience}

## Campaign Goal
{campaign_goal}"""


def linkedin_prompt(product_brief: str, positioning: str, voice_guide: str, target_audience: str, campaign_goal: str) -> tuple[str, str]:
    system = "You are a LinkedIn content strategist. You write posts that stop the scroll and drive engagement — not corporate fluff."

    context = CONTENT_CONTEXT.format(
        product_brief=product_brief, positioning=positioning,
        voice_guide=voice_guide, target_audience=target_audience, campaign_goal=campaign_goal,
    )

    prompt = f"""{context}

Create 3 LinkedIn posts, each with a different angle:
1. **Thought leadership** — share an insight about the problem this product solves. Don't mention the product until the end.
2. **Product value** — directly showcase what the product does and why it matters. Lead with the outcome.
3. **Social proof angle** — frame it as a story or scenario that demonstrates impact. Could be hypothetical but must feel real.

For each post, produce a JSON list of 3 objects with fields:
- "hook": The first 1-2 lines (this is what people see before "...see more"). Must stop the scroll.
- "body": The main content. 800-1300 characters. Use line breaks for readability.
- "cta": A clear call to action at the end.
- "angle": Which angle this post uses ("thought_leadership", "product_value", "social_proof")

LinkedIn rules: Professional but human. Short paragraphs. Hook must create curiosity. No hashtag spam (max 3, only if natural).
"""
    return system, prompt


def twitter_prompt(product_brief: str, positioning: str, voice_guide: str, target_audience: str, campaign_goal: str) -> tuple[str, str]:
    system = "You are a Twitter/X strategist. You write threads that build narrative momentum and get shared."

    context = CONTENT_CONTEXT.format(
        product_brief=product_brief, positioning=positioning,
        voice_guide=voice_guide, target_audience=target_audience, campaign_goal=campaign_goal,
    )

    prompt = f"""{context}

Create a tweet thread (5-7 tweets) that tells a compelling story about this product.

Produce a JSON object with field:
- "tweets": List of 5-7 strings, each under 280 characters

Thread structure:
- Tweet 1: Hook — a bold claim or surprising insight (must make people want to read more)
- Tweets 2-4: Build the narrative — problem, context, solution reveal
- Tweet 5-6: Proof/impact — what changes when you use this
- Final tweet: CTA — what should the reader do next

Twitter rules: Conversational tone. No corporate speak. Each tweet must stand alone AND connect to the thread. Use "1/" numbering.
"""
    return system, prompt


def email_prompt(product_brief: str, positioning: str, voice_guide: str, target_audience: str, campaign_goal: str) -> tuple[str, str]:
    system = "You are an email marketing expert. You write sequences that nurture leads from curiosity to action."

    context = CONTENT_CONTEXT.format(
        product_brief=product_brief, positioning=positioning,
        voice_guide=voice_guide, target_audience=target_audience, campaign_goal=campaign_goal,
    )

    prompt = f"""{context}

Create a 3-email nurture sequence:
1. **Hook email** — sent on signup/first touch. Goal: establish the problem, create resonance.
2. **Value email** — sent 2-3 days later. Goal: show how the product solves the problem with specifics.
3. **CTA email** — sent 2-3 days after that. Goal: drive action with urgency (without being sleazy).

Produce a JSON object with field:
- "emails": List of 3 objects, each with:
  - "subject": Subject line (under 60 chars, curiosity-driven)
  - "preview_text": Preview/preheader text (under 90 chars)
  - "body": Full email body. Use short paragraphs. Include personalization placeholder [First Name].
  - "cta": The call-to-action text and what it links to

Email rules: Subject line is everything. Body should be scannable. One CTA per email. Warm, direct tone.
"""
    return system, prompt


def blog_prompt(product_brief: str, positioning: str, voice_guide: str, target_audience: str, campaign_goal: str) -> tuple[str, str]:
    system = "You are a content marketing strategist. You create blog content that ranks, reads well, and converts."

    context = CONTENT_CONTEXT.format(
        product_brief=product_brief, positioning=positioning,
        voice_guide=voice_guide, target_audience=target_audience, campaign_goal=campaign_goal,
    )

    prompt = f"""{context}

Create a detailed blog post outline. The post should attract the target audience through the problem/solution angle — not be a product page.

Produce a JSON object with fields:
- "title": SEO-friendly title (include the core problem or benefit, under 70 chars)
- "intro": 2-3 sentence intro that hooks the reader with the problem
- "sections": List of 4-6 objects, each with:
  - "heading": Section heading (clear, benefit-oriented)
  - "key_points": List of 3-4 bullet points to cover in this section
  - "summary": 1-2 sentence description of what this section accomplishes
- "conclusion": 2-3 sentence conclusion with CTA woven in naturally

Blog rules: Lead with the problem, not the product. Educational tone. Product enters naturally mid-way. SEO-aware headings.
"""
    return system, prompt


def ad_copy_prompt(product_brief: str, positioning: str, voice_guide: str, target_audience: str, campaign_goal: str) -> tuple[str, str]:
    system = "You are a direct response copywriter. Every word must earn its place. You write ads that convert."

    context = CONTENT_CONTEXT.format(
        product_brief=product_brief, positioning=positioning,
        voice_guide=voice_guide, target_audience=target_audience, campaign_goal=campaign_goal,
    )

    prompt = f"""{context}

Create 3 short-form ad copy variations for paid channels (Google Ads, Facebook/Instagram, LinkedIn Ads).

Produce a JSON list of 3 objects with fields:
- "headline": Under 30 characters. Punchy, benefit-driven.
- "body": 90-150 characters. Expand on the benefit with specificity.
- "cta": Clear action phrase (e.g., "Start free trial", "See how it works")

Each variation should test a different angle:
1. Problem-focused (agitate the pain point)
2. Benefit-focused (promise the outcome)
3. Curiosity-focused (make them want to learn more)

Ad rules: No fluff. Every word must earn its place. Specific > generic. Numbers and results > vague promises.
"""
    return system, prompt
