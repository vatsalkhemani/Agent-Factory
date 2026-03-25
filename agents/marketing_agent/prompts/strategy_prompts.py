def positioning_prompt(product_brief: str, competitive_analysis: str, target_audience: str, campaign_goal: str) -> tuple[str, str]:
    system = "You are a brand strategist who builds sharp, differentiated positioning. You don't do generic. Every word earns its place."

    prompt = f"""Build brand positioning for this product based on real research.

## Product Intelligence
{product_brief}

## Competitive Landscape
{competitive_analysis}

## Target Audience
{target_audience}

## Campaign Goal
{campaign_goal}

Produce a JSON object with these exact fields:
- "statement": A positioning statement (format: "For [audience], [product] is the [category] that [key differentiator] unlike [alternatives] because [reason to believe]"). Make it specific and sharp, not generic.
- "key_messages": List of 3-5 key messages that support the positioning. Each should be a complete thought, ready to use in content.
- "differentiators": List of 3-4 things that make this product genuinely different (not just "easy to use" or "powerful")
- "proof_points": List of 3-4 evidence points that back up the claims (features, metrics, capabilities)

Avoid generic marketing speak. "Innovative solution" and "cutting-edge technology" are banned. Be specific.
"""
    return system, prompt


def voice_guide_prompt(product_brief: str, positioning: str, target_audience: str) -> tuple[str, str]:
    system = "You are a brand voice expert. You define how a brand speaks — not what it says, but HOW it says it."

    prompt = f"""Create a brand voice guide that will govern all content in this campaign.

## Product Intelligence
{product_brief}

## Brand Positioning
{positioning}

## Target Audience
{target_audience}

Produce a JSON object with these exact fields:
- "tone_attributes": List of 4-5 tone descriptors with nuance (e.g., "Confident but not arrogant — we state facts, not hype")
- "dos": List of 5-6 writing guidelines (e.g., "Use concrete numbers over vague claims", "Lead with the benefit, not the feature")
- "donts": List of 5-6 things to avoid (e.g., "Don't use buzzwords like 'synergy' or 'leverage'", "Don't start with 'In today's world...'")
- "example_phrases": List of 5-6 phrases that exemplify the voice (these should feel like they could appear in actual content)
- "words_to_avoid": List of 8-10 specific words or phrases that are off-brand

The voice guide must be specific to THIS product and audience. Generic advice like "be authentic" is not useful.
"""
    return system, prompt
