import streamlit as st
from datetime import date, timedelta
from streamlit_folium import st_folium

from config import GOOGLE_API_KEY, AVAILABLE_INTERESTS, BUDGET_TIERS, MAX_TRIP_DAYS
from models import TripInput
from agent import generate_itinerary, refine_itinerary
from map_builder import build_trip_map
from export import itinerary_to_markdown

st.set_page_config(page_title="Travel Planner Agent", page_icon="🗺️", layout="wide")

# --- Session state init ---
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "generating" not in st.session_state:
    st.session_state.generating = False


def _check_api_keys():
    missing = []
    if not GOOGLE_API_KEY:
        missing.append(
            "**GOOGLE_API_KEY** - Get it from [Google AI Studio](https://aistudio.google.com/apikey)"
        )
    if missing:
        st.error("Missing required API keys:")
        for key in missing:
            st.markdown(f"- {key}")
        st.info("Add them to your `.env` file and restart the app.")
        st.stop()


def _render_sidebar() -> TripInput | None:
    with st.sidebar:
        st.title("🗺️ Travel Planner")
        st.markdown("Plan your perfect trip with AI")
        st.divider()

        with st.form("trip_form"):
            destination = st.text_input(
                "Destination", placeholder="e.g., Tokyo, Japan"
            )
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start date", value=date.today() + timedelta(days=7))
            with col2:
                end_date = st.date_input("End date", value=date.today() + timedelta(days=12))

            budget = st.selectbox("Budget", BUDGET_TIERS, index=1)
            interests = st.multiselect(
                "Interests", AVAILABLE_INTERESTS, default=["Food", "History"]
            )
            notes = st.text_area(
                "Special notes",
                placeholder="e.g., traveling with kids, vegetarian, want street food only...",
            )

            submitted = st.form_submit_button("✨ Plan My Trip", use_container_width=True)

        # Validation
        if submitted:
            if not destination:
                st.error("Please enter a destination.")
                return None

            if end_date <= start_date:
                st.error("End date must be after start date.")
                return None

            trip_days = (end_date - start_date).days
            if trip_days > MAX_TRIP_DAYS:
                st.error(f"Maximum trip length is {MAX_TRIP_DAYS} days.")
                return None

            return TripInput(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                budget_tier=budget,
                interests=interests,
                notes=notes,
            )

        # Export button (only when itinerary exists)
        if st.session_state.itinerary:
            st.divider()
            st.subheader("Export")
            md_content = itinerary_to_markdown(st.session_state.itinerary)
            st.download_button(
                "📥 Download as Markdown",
                data=md_content,
                file_name=f"trip_{st.session_state.itinerary.destination.replace(' ', '_').lower()}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    return None


def _render_itinerary():
    itinerary = st.session_state.itinerary
    if not itinerary:
        return

    # Summary bar
    cols = st.columns(4)
    cols[0].metric("Destination", itinerary.destination)
    cols[1].metric("Duration", f"{itinerary.total_days} days")
    cols[2].metric("Est. Cost", f"${itinerary.estimated_total_cost_usd:,.0f}")
    cols[3].metric("Currency", itinerary.currency)

    # Map
    st.subheader("📍 Trip Map")
    trip_map = build_trip_map(itinerary)
    st_folium(trip_map, use_container_width=True, height=400)

    # Day-by-day
    st.subheader("📋 Itinerary")
    for day in itinerary.days:
        with st.expander(
            f"**Day {day.day_number}** - {day.date} | {day.theme}",
            expanded=(day.day_number == 1),
        ):
            if day.weather_note:
                st.caption(f"🌤️ {day.weather_note}")

            for activity in day.activities:
                slot_emoji = {"morning": "🌅", "afternoon": "☀️", "evening": "🌙"}.get(
                    activity.time_slot, "📍"
                )

                col_main, col_cost = st.columns([4, 1])
                with col_main:
                    st.markdown(
                        f"**{slot_emoji} {activity.time_slot.title()}** ({activity.time_range})"
                    )
                    st.markdown(f"**{activity.name}** - _{activity.location}_")
                    st.markdown(activity.description)

                    if activity.meal:
                        m = activity.meal
                        st.markdown(
                            f"🍽️ *{m.restaurant_name}* ({m.cuisine}) - {m.price_range}"
                        )

                with col_cost:
                    st.markdown(f"**${activity.estimated_cost_usd:.0f}**")

                st.divider()

    # Local tips & packing
    col_tips, col_pack = st.columns(2)
    with col_tips:
        if itinerary.local_tips:
            st.subheader("💡 Local Tips")
            for tip in itinerary.local_tips:
                st.markdown(f"- {tip}")
    with col_pack:
        if itinerary.packing_suggestions:
            st.subheader("🎒 Packing Suggestions")
            for item in itinerary.packing_suggestions:
                st.markdown(f"- {item}")


def _render_chat():
    if not st.session_state.itinerary:
        return

    st.divider()
    st.subheader("💬 Refine Your Itinerary")
    st.caption("Ask me to adjust the plan - e.g., 'make day 2 more relaxed' or 'add more food spots'")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("What would you like to change?")
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate refinement
        with st.chat_message("assistant"):
            with st.spinner("Updating your itinerary..."):
                try:
                    updated = refine_itinerary(
                        st.session_state.itinerary,
                        user_input,
                        st.session_state.chat_history,
                    )
                    st.session_state.itinerary = updated
                    response_text = "✅ Itinerary updated! Scroll up to see the changes."
                    st.markdown(response_text)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response_text}
                    )
                    st.rerun()
                except Exception as e:
                    error_text = f"Sorry, I couldn't update the itinerary. Error: {str(e)}"
                    st.error(error_text)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": error_text}
                    )


def main():
    _check_api_keys()

    trip_input = _render_sidebar()

    if trip_input:
        # New trip requested
        st.session_state.chat_history = []
        with st.spinner("✨ Planning your trip... This may take a moment."):
            try:
                itinerary = generate_itinerary(trip_input)
                st.session_state.itinerary = itinerary
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate itinerary: {str(e)}")
                st.info("Please try again. If the error persists, check your API keys.")
                return

    if st.session_state.itinerary:
        _render_itinerary()
        _render_chat()
    else:
        # Welcome screen
        st.title("🗺️ Travel Planner Agent")
        st.markdown(
            """
            **Plan your perfect trip with AI!**

            1. Fill in your trip details in the sidebar
            2. Get a structured day-by-day itinerary with real places
            3. See your plan on an interactive map
            4. Chat to refine and adjust the plan
            5. Export when you're happy!

            👈 Start by filling in the sidebar form.
            """
        )


if __name__ == "__main__":
    main()
