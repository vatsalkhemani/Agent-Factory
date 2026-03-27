def company_research_prompt(company_name: str, research_content: str) -> tuple[str, str]:
    system = "You are a company research analyst who helps job applicants understand a company's culture, values, and recent activities. You focus on actionable intelligence that can be woven into applications."

    prompt = f"""Analyze the following information about {company_name} and produce a company intelligence brief for a job applicant.

## Research Data
{research_content if research_content else "(No research data available -- provide general guidance based on the company name)"}

Produce a JSON object with these exact fields:
- "company_name": "{company_name}"
- "industry": The company's primary industry/sector
- "mission_or_values": The company's stated mission or core values (1-2 sentences). If not found, write "Not available from research"
- "recent_news": List of 2-4 recent developments, product launches, or news items. If none found, provide empty list.
- "culture_signals": List of 2-4 signals about company culture (from careers page language, values statements, news). Things like "emphasis on innovation", "remote-first", "fast-paced startup culture"
- "talking_points": List of 3-5 specific things the applicant could mention in their cover letter to show they researched the company. Be specific -- reference actual initiatives, values, or products.

Focus on information that's useful for a job application. Skip generic corporate boilerplate.
"""
    return system, prompt
