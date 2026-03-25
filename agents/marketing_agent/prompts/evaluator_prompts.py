def evaluation_prompt(voice_guide: str, positioning: str, all_content: str) -> tuple[str, str]:
    system = "You are a senior marketing editor and brand guardian. You evaluate content for voice consistency, campaign coherence, and channel fitness. You are rigorous but constructive."

    prompt = f"""Evaluate every content piece in this campaign against the brand standards.

## Brand Voice Guide
{voice_guide}

## Brand Positioning
{positioning}

## All Campaign Content
{all_content}

Score EACH content piece on three criteria (1-10 scale):
1. **Voice consistency** — Does it match the brand voice guide? Tone, word choice, style?
2. **Campaign coherence** — Does it tell the same story as other pieces? Consistent messaging?
3. **Channel optimization** — Is it properly optimized for its platform? Right length, format, conventions?

Produce a JSON object with fields:
- "scores": List of objects, one per content piece, each with:
  - "piece_name": Name of the piece (e.g., "linkedin_post_1", "email_2", "twitter_thread", "blog_outline", "ad_copy_3")
  - "voice_score": Integer 1-10
  - "coherence_score": Integer 1-10
  - "channel_score": Integer 1-10
  - "feedback": Specific, actionable feedback (2-3 sentences). What's working and what needs to change.
  - "needs_revision": Boolean — true if ANY score is below 7
- "overall_feedback": 2-3 sentences on the campaign as a whole

Content pieces to evaluate:
- linkedin_post_1, linkedin_post_2, linkedin_post_3
- twitter_thread
- email_1, email_2, email_3
- blog_outline
- ad_copy_1, ad_copy_2, ad_copy_3
"""
    return system, prompt


def revision_prompt(piece_name: str, original_content: str, feedback: str, voice_guide: str, positioning: str) -> tuple[str, str]:
    system = "You are a senior content editor. You revise content based on specific feedback while maintaining the original intent."

    prompt = f"""Revise this content piece based on the evaluator's feedback.

## Piece: {piece_name}

## Original Content
{original_content}

## Evaluator Feedback
{feedback}

## Brand Voice Guide
{voice_guide}

## Brand Positioning
{positioning}

Revise the content to address the feedback. Keep the same structure and format as the original. Return ONLY the revised content in the same JSON format as the original.
"""
    return system, prompt
