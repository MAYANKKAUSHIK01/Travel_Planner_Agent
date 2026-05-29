"""
Budget Estimation Tool for the AI Travel Agent.
Calculates total trip cost based on flights, hotels, food, and local expenses.
"""

import json
from pathlib import Path
from langchain.tools import tool


DATA_PATH = Path(__file__).parent.parent / "data"

# Per-day local expense estimates by city tier
CITY_EXPENSE_TIERS = {
    "budget": {
        "food_per_day": 500,
        "local_transport_per_day": 200,
        "misc_per_day": 200,
    },
    "mid-range": {
        "food_per_day": 1200,
        "local_transport_per_day": 500,
        "misc_per_day": 500,
    },
    "luxury": {
        "food_per_day": 3000,
        "local_transport_per_day": 1500,
        "misc_per_day": 1500,
    },
}

EXPENSIVE_CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad"]
HILL_STATIONS = ["Manali", "Shimla", "Darjeeling", "Ooty"]


def _load_flights() -> list[dict]:
    with open(DATA_PATH / "flights.json") as f:
        return json.load(f)


def _load_hotels() -> list[dict]:
    with open(DATA_PATH / "hotels.json") as f:
        return json.load(f)


def _load_places() -> list[dict]:
    with open(DATA_PATH / "places.json") as f:
        return json.load(f)


@tool
def estimate_budget(query: str) -> str:
    """
    Estimate the total budget for a trip.

    Input format: "source:Delhi destination:Goa days:3 travelers:2 budget_type:mid-range"
    Budget types: budget, mid-range, luxury
    Travelers: number of people (default: 1)

    Returns a detailed budget breakdown with flight, hotel, food, transport, entry fees,
    and total cost estimation.
    """
    try:
        flights = _load_flights()
        hotels = _load_hotels()
        places = _load_places()

        parts = query.lower().split()
        source = None
        destination = None
        days = 3
        travelers = 1
        budget_type = "mid-range"

        for part in parts:
            if part.startswith("source:"):
                source = part.split(":", 1)[1].strip().title()
            elif part.startswith("destination:"):
                destination = part.split(":", 1)[1].strip().title()
            elif part.startswith("days:"):
                try:
                    days = int(part.split(":", 1)[1].strip())
                except ValueError:
                    days = 3
            elif part.startswith("travelers:"):
                try:
                    travelers = int(part.split(":", 1)[1].strip())
                except ValueError:
                    travelers = 1
            elif part.startswith("budget_type:") or part.startswith("budget:"):
                budget_type = part.split(":", 1)[1].strip().lower()
                if budget_type in ["mid", "moderate"]:
                    budget_type = "mid-range"

        if not destination:
            return "Error: Please provide at least a destination city. Example: 'source:Delhi destination:Goa days:3'"

        # --- 1. FLIGHT COST ---
        flight_cost_per_person = 0
        flight_name = "Not specified"
        if source:
            dest_flights = [
                f for f in flights
                if f["source"].lower() == source.lower()
                and f["destination"].lower() == destination.lower()
            ]
            if dest_flights:
                if budget_type == "luxury":
                    dest_flights.sort(key=lambda x: x["price"], reverse=True)
                else:
                    dest_flights.sort(key=lambda x: x["price"])
                best_flight = dest_flights[0]
                flight_cost_per_person = best_flight["price"]
                flight_name = f"{best_flight['airline']} {best_flight['flight_number']}"
            else:
                flight_cost_per_person = 5000  # fallback
                flight_name = "Estimated (no direct flight data)"

        # --- 2. HOTEL COST ---
        dest_hotels = [h for h in hotels if h["city"].lower() == destination.lower()]
        hotel_cost_per_night = 0
        hotel_name = "Not specified"

        if dest_hotels:
            if budget_type == "budget":
                filtered = [h for h in dest_hotels if h["price_per_night"] <= 2000]
            elif budget_type == "mid-range":
                filtered = [h for h in dest_hotels if 2000 < h["price_per_night"] <= 8000]
            else:
                filtered = [h for h in dest_hotels if h["price_per_night"] > 8000]

            pool = filtered if filtered else dest_hotels
            pool.sort(key=lambda x: x["review_score"], reverse=True)
            best_hotel = pool[0]
            hotel_cost_per_night = best_hotel["price_per_night"]
            hotel_name = best_hotel["name"]

        hotel_total = hotel_cost_per_night * days

        # --- 3. ENTRY FEES ---
        dest_places = [p for p in places if p["city"].lower() == destination.lower()]
        dest_places.sort(key=lambda x: x["rating"], reverse=True)
        top_places = dest_places[:days * 2]
        entry_fees_total = sum(p["entry_fee"] for p in top_places)

        # --- 4. LOCAL EXPENSES ---
        expense_tier = CITY_EXPENSE_TIERS.get(budget_type, CITY_EXPENSE_TIERS["mid-range"])

        # Adjust for expensive cities
        multiplier = 1.0
        if destination in EXPENSIVE_CITIES:
            multiplier = 1.2
        elif destination in HILL_STATIONS:
            multiplier = 1.1

        food_total = int(expense_tier["food_per_day"] * days * multiplier)
        transport_total = int(expense_tier["local_transport_per_day"] * days * multiplier)
        misc_total = int(expense_tier["misc_per_day"] * days)

        # --- 5. TOTALS ---
        flight_total = flight_cost_per_person * travelers
        accommodation_total = hotel_total  # shared for group
        local_total = (food_total + transport_total + misc_total) * travelers

        grand_total = flight_total + accommodation_total + entry_fees_total + local_total

        # --- FORMAT OUTPUT ---
        results = [
            f"💰 Budget Breakdown — {days}-Day Trip to {destination}",
            f"   ({travelers} traveler{'s' if travelers > 1 else ''} | {budget_type.title()} budget)",
            "=" * 50,
        ]

        if source:
            results.append(
                f"\n✈️  Flights ({source} → {destination})\n"
                f"   {flight_name}\n"
                f"   ₹{flight_cost_per_person:,}/person × {travelers} = ₹{flight_total:,}"
            )

        results.append(
            f"\n🏨  Accommodation\n"
            f"   {hotel_name}\n"
            f"   ₹{hotel_cost_per_night:,}/night × {days} nights = ₹{accommodation_total:,}"
        )

        results.append(
            f"\n🍽️  Food & Dining\n"
            f"   ₹{expense_tier['food_per_day']:,}/day × {days} days × {travelers} = ₹{food_total * travelers:,}"
        )

        results.append(
            f"\n🚗  Local Transport\n"
            f"   ₹{expense_tier['local_transport_per_day']:,}/day × {days} days × {travelers} = ₹{transport_total * travelers:,}"
        )

        results.append(
            f"\n🎫  Entry Fees (top attractions)\n"
            f"   {len(top_places)} attractions × avg fee = ₹{entry_fees_total:,}"
        )

        results.append(
            f"\n🛍️  Miscellaneous & Shopping\n"
            f"   ₹{expense_tier['misc_per_day']:,}/day × {days} days × {travelers} = ₹{misc_total * travelers:,}"
        )

        results.append("\n" + "=" * 50)
        results.append(f"🧾 TOTAL ESTIMATED COST: ₹{grand_total:,}")
        results.append(f"   Per Person: ₹{grand_total // travelers:,}")

        # Budget advice
        if budget_type == "budget":
            results.append("\n💡 Tip: Book flights 3-4 weeks in advance for best prices. Use hostels and street food to save more.")
        elif budget_type == "mid-range":
            results.append("\n💡 Tip: Consider booking a combo of mid-range hotels and occasional splurges for best experience.")
        else:
            results.append("\n💡 Tip: Look for early-bird luxury hotel deals and business class upgrades for premium travel.")

        return "\n".join(results)

    except Exception as e:
        return f"Error estimating budget: {str(e)}"
