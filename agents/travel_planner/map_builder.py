import folium
from models import Itinerary
from config import DAY_COLORS


def build_trip_map(itinerary: Itinerary) -> folium.Map:
    """Build an interactive Folium map with color-coded pins per day and route lines."""

    # Collect all coordinates to auto-fit bounds
    all_coords = []
    for day in itinerary.days:
        for activity in day.activities:
            all_coords.append((activity.latitude, activity.longitude))

    if not all_coords:
        # Default to world view if no coordinates
        return folium.Map(location=[20, 0], zoom_start=2)

    # Center on average of all coordinates
    avg_lat = sum(c[0] for c in all_coords) / len(all_coords)
    avg_lng = sum(c[1] for c in all_coords) / len(all_coords)
    trip_map = folium.Map(location=[avg_lat, avg_lng], zoom_start=13)

    for day in itinerary.days:
        color = DAY_COLORS[(day.day_number - 1) % len(DAY_COLORS)]
        day_coords = []

        for activity in day.activities:
            lat, lng = activity.latitude, activity.longitude
            day_coords.append((lat, lng))

            # Pin with popup
            popup_html = f"""
            <b>{activity.name}</b><br>
            <i>Day {day.day_number} - {activity.time_slot.title()}</i><br>
            {activity.time_range}<br>
            ~${activity.estimated_cost_usd:.0f}
            """
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Day {day.day_number}: {activity.name}",
                icon=folium.Icon(color=color, icon="info-sign"),
            ).add_to(trip_map)

        # Connect activities within the same day with a dashed line
        if len(day_coords) > 1:
            folium.PolyLine(
                day_coords,
                color=color,
                weight=2,
                opacity=0.7,
                dash_array="10",
            ).add_to(trip_map)

    # Fit map to show all pins
    trip_map.fit_bounds(all_coords)

    return trip_map
