from models import Itinerary


def itinerary_to_markdown(itinerary: Itinerary) -> str:
    """Convert an itinerary to a downloadable Markdown string."""
    lines = [
        f"# Trip to {itinerary.destination}",
        f"**Duration**: {itinerary.total_days} days",
        f"**Estimated Total Cost**: ~${itinerary.estimated_total_cost_usd:.0f} USD",
        f"**Currency**: {itinerary.currency}",
        "",
    ]

    # Local tips
    if itinerary.local_tips:
        lines.append("## Local Tips")
        for tip in itinerary.local_tips:
            lines.append(f"- {tip}")
        lines.append("")

    # Packing suggestions
    if itinerary.packing_suggestions:
        lines.append("## Packing Suggestions")
        for item in itinerary.packing_suggestions:
            lines.append(f"- {item}")
        lines.append("")

    # Day-by-day
    for day in itinerary.days:
        lines.append(f"## Day {day.day_number} - {day.date}")
        lines.append(f"**Theme**: {day.theme}")
        lines.append(f"**Weather**: {day.weather_note}")
        lines.append("")

        for activity in day.activities:
            lines.append(f"### {activity.time_slot.title()} ({activity.time_range})")
            lines.append(f"**{activity.name}** - {activity.location}")
            lines.append(f"{activity.description}")
            lines.append(f"*Estimated cost: ~${activity.estimated_cost_usd:.0f} USD*")

            if activity.meal:
                m = activity.meal
                lines.append(
                    f"*Meal: {m.restaurant_name} ({m.cuisine}) - {m.price_range}*"
                )

            lines.append("")

    return "\n".join(lines)
