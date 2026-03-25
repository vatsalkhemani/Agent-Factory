def product_brief_prompt(scraped_data: str, user_description: str, target_audience: str) -> tuple[str, str]:
    system = "You are a senior marketing research analyst. You extract actionable product intelligence from raw website data."

    prompt = f"""Analyze this product and produce a structured intelligence brief.

## Scraped Website Data
{scraped_data}

## User's Product Description
{user_description}

## Target Audience
{target_audience}

Produce a JSON object with these exact fields:
- "summary": A clear 2-3 sentence description of what this product does and who it's for
- "features": List of 4-6 key features extracted from the website
- "value_propositions": List of 3-5 value propositions (benefits, not features)
- "audience_signals": List of 3-4 signals about who this product targets (from website language, positioning)
- "messaging_tone": A sentence describing the current tone of their messaging (e.g., "Professional and technical, aimed at developers")

Base your analysis primarily on the scraped website data. Use the user's description to fill gaps only.
"""
    return system, prompt


def competitive_analysis_prompt(competitors_data: str, product_brief: str) -> tuple[str, str]:
    system = "You are a competitive intelligence analyst. You identify positioning gaps and opportunities."

    prompt = f"""Analyze these competitors relative to our product and produce a competitive analysis.

## Our Product
{product_brief}

## Competitor Data
{competitors_data}

Produce a JSON object with these exact fields:
- "competitors": List of objects, each with:
  - "url": The competitor's URL
  - "name": The competitor's name/brand
  - "positioning": How they position themselves (1-2 sentences)
  - "strengths": List of 2-3 key strengths in their messaging
  - "messaging_approach": Their messaging style (1 sentence)
- "gaps": List of 3-4 messaging gaps — things competitors are NOT saying that we could own
- "opportunities": List of 3-4 positioning opportunities — angles we can take that competitors haven't claimed

Focus on messaging and positioning, not product features. We care about what they SAY, not what they DO.
"""
    return system, prompt
