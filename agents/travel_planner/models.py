from __future__ import annotations
from pydantic import BaseModel
from datetime import date


class TripInput(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget_tier: str  # "Budget", "Moderate", "Luxury"
    interests: list[str]
    notes: str = ""


class MealRecommendation(BaseModel):
    restaurant_name: str
    cuisine: str
    price_range: str  # "$", "$$", "$$$"


class Activity(BaseModel):
    time_slot: str  # "morning", "afternoon", "evening"
    time_range: str  # "09:00 - 11:30"
    name: str
    location: str
    latitude: float
    longitude: float
    description: str
    estimated_cost_usd: float
    category: str
    meal: MealRecommendation | None = None


class DayPlan(BaseModel):
    day_number: int
    date: str
    theme: str
    weather_note: str
    activities: list[Activity]


class Itinerary(BaseModel):
    destination: str
    total_days: int
    currency: str
    estimated_total_cost_usd: float
    local_tips: list[str]
    packing_suggestions: list[str]
    days: list[DayPlan]
