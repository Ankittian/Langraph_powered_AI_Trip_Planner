"""Expense Calculator Tool — helps estimate trip budgets and per-day costs."""

from langchain_core.tools import tool


@tool
def calculate_trip_budget(
    num_days: int,
    accommodation_per_night: float,
    food_per_day: float,
    transport_per_day: float,
    activities_per_day: float = 0.0,
    num_travelers: int = 1,
    miscellaneous_total: float = 0.0,
    currency: str = "USD",
) -> str:
    """
    Calculate an estimated total trip budget and per-person cost breakdown.

    Args:
        num_days: Number of days for the trip.
        accommodation_per_night: Cost of accommodation per night.
        food_per_day: Estimated food/dining cost per day.
        transport_per_day: Estimated local transport cost per day (e.g. taxi, metro).
        activities_per_day: Estimated cost of activities/attractions per day. Default 0.
        num_travelers: Number of travelers sharing costs. Default 1.
        miscellaneous_total: One-time misc costs (SIM, tips, shopping, etc.). Default 0.
        currency: Currency code for the estimates (e.g. 'USD', 'INR'). Default 'USD'.

    Returns:
        A detailed budget breakdown as a formatted string.
    """
    try:
        accommodation_total = accommodation_per_night * num_days
        food_total = food_per_day * num_days
        transport_total = transport_per_day * num_days
        activities_total = activities_per_day * num_days
        grand_total = accommodation_total + food_total + transport_total + activities_total + miscellaneous_total
        per_person = grand_total / num_travelers if num_travelers > 0 else grand_total
        per_person_per_day = per_person / num_days if num_days > 0 else per_person

        return (
            f"💰 Trip Budget Estimate ({num_days} days, {num_travelers} traveler{'s' if num_travelers > 1 else ''})\n"
            f"{'='*50}\n\n"
            f"  🏨 Accommodation: {accommodation_per_night:,.2f} × {num_days} nights = {accommodation_total:,.2f} {currency}\n"
            f"  🍽  Food & Dining:  {food_per_day:,.2f} × {num_days} days  = {food_total:,.2f} {currency}\n"
            f"  🚕 Transport:      {transport_per_day:,.2f} × {num_days} days  = {transport_total:,.2f} {currency}\n"
            f"  🎭 Activities:     {activities_per_day:,.2f} × {num_days} days  = {activities_total:,.2f} {currency}\n"
            f"  🛍  Miscellaneous:  {miscellaneous_total:,.2f} {currency}\n\n"
            f"{'='*50}\n"
            f"  📊 GRAND TOTAL:          {grand_total:,.2f} {currency}\n"
            f"  👤 Per Person:           {per_person:,.2f} {currency}\n"
            f"  📅 Per Person Per Day:   {per_person_per_day:,.2f} {currency}\n"
        )
    except Exception as e:
        return f"Error calculating budget: {e}"


@tool
def estimate_daily_food_cost(city: str, budget_level: str = "mid-range") -> str:
    """
    Estimate daily food costs for a given city and budget level.

    Args:
        city: City name (e.g. 'Bangkok', 'London', 'Mumbai').
        budget_level: One of 'budget', 'mid-range', 'luxury'. Default 'mid-range'.

    Returns:
        An estimated daily food cost range.
    """
    # Approximate multipliers based on cost-of-living indices
    budget_multipliers = {
        "budget": (0.6, "street food, local eateries, markets"),
        "mid-range": (1.0, "casual restaurants, cafés, occasional fine dining"),
        "luxury": (2.0, "upscale restaurants, fine dining, premium experiences"),
    }

    # Base daily food costs by region (USD estimates)
    region_costs = {
        # South/Southeast Asia
        "goa": 15, "mumbai": 18, "delhi": 16, "bangalore": 17, "jaipur": 14,
        "bangkok": 15, "bali": 14, "hanoi": 12, "singapore": 35,
        "tokyo": 40, "kyoto": 35, "seoul": 30, "osaka": 35,
        # Europe
        "paris": 45, "london": 50, "rome": 35, "barcelona": 35,
        "amsterdam": 40, "berlin": 30, "prague": 25, "lisbon": 28,
        # Americas
        "new york": 50, "los angeles": 45, "miami": 40,
        "cancun": 25, "rio de janeiro": 22, "buenos aires": 20,
        # Middle East / Africa
        "dubai": 40, "istanbul": 20, "cairo": 12, "cape town": 22,
        # Oceania
        "sydney": 45, "melbourne": 42, "auckland": 38,
    }

    city_lower = city.lower().strip()
    base_cost = region_costs.get(city_lower, 30)  # default ~$30/day

    level = budget_level.lower().strip()
    multiplier, description = budget_multipliers.get(level, (1.0, "mixed dining"))

    estimated = round(base_cost * multiplier, 2)
    low = round(estimated * 0.8, 2)
    high = round(estimated * 1.3, 2)

    return (
        f"🍽 Estimated Daily Food Cost in {city} ({budget_level}):\n"
        f"  Range: ${low} – ${high} USD per person per day\n"
        f"  Average: ~${estimated} USD\n"
        f"  Includes: {description}\n\n"
        f"  💡 Note: These are estimates. Actual costs may vary based on restaurants chosen."
    )


# Export tool list for the agent
expense_tools = [calculate_trip_budget, estimate_daily_food_cost]
