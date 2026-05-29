"""
Hotel Recommendation Tool for the AI Travel Agent.
Reads hotels.json and filters/ranks based on city, budget, and preferences.
"""

import json
from pathlib import Path
from langchain.tools import tool


DATA_PATH = Path(__file__).parent.parent / "data" / "hotels.json"


def _load_hotels() -> list[dict]:
    """Load hotels data from JSON file."""
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@tool
def search_hotels(query: str) -> str:
    """
    Search for hotels in a specific city with optional filters.

    Input format: "city:Goa budget:mid-range nights:3"
    Budget options: budget (under ₹2000), mid-range (₹2000-₹8000), luxury (₹8000+)
    Also accepts: "city:Goa max_price:5000 min_rating:4.0"

    Returns ranked hotel options with price, rating, amenities and availability.
    """
    try:
        hotels = _load_hotels()

        parts = query.lower().split()
        city = None
        budget_type = None
        max_price = None
        min_rating = None
        nights = 1

        for part in parts:
            if part.startswith("city:"):
                city = part.split(":", 1)[1].strip().title()
            elif part.startswith("budget:"):
                budget_type = part.split(":", 1)[1].strip().lower()
            elif part.startswith("max_price:"):
                try:
                    max_price = int(part.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif part.startswith("min_rating:"):
                try:
                    min_rating = float(part.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif part.startswith("nights:"):
                try:
                    nights = int(part.split(":", 1)[1].strip())
                except ValueError:
                    nights = 1

        # Fallback: treat first word as city if no prefix
        if not city:
            city = query.title().split()[0]

        # Filter by city
        matched = [h for h in hotels if h["city"].lower() == city.lower()]

        if not matched:
            return f"No hotels found in {city}. Please check the city name."

        # Apply budget filter
        if budget_type == "budget":
            matched = [h for h in matched if h["price_per_night"] <= 2000] or matched
        elif budget_type == "mid-range" or budget_type == "midrange":
            matched = [h for h in matched if 2000 < h["price_per_night"] <= 8000] or matched
        elif budget_type == "luxury":
            matched = [h for h in matched if h["price_per_night"] > 8000] or matched

        # Apply max price filter
        if max_price:
            filtered = [h for h in matched if h["price_per_night"] <= max_price]
            matched = filtered if filtered else matched

        # Apply min rating filter
        if min_rating:
            filtered = [h for h in matched if h["rating"] >= min_rating]
            matched = filtered if filtered else matched

        # Sort by review score (descending)
        matched.sort(key=lambda x: x["review_score"], reverse=True)

        # Format results
        results = [f"🏨 Hotels in {city}:"]
        results.append("-" * 50)

        for i, h in enumerate(matched[:4], 1):
            total_cost = h["price_per_night"] * nights
            amenities_str = ", ".join(h["amenities"][:4])
            results.append(
                f"{i}. {h['name']} ({'⭐' * int(h['rating'])})\n"
                f"   Area: {h['area']} | Type: {h['type']}\n"
                f"   Price: ₹{h['price_per_night']:,}/night"
                + (f" × {nights} nights = ₹{total_cost:,}" if nights > 1 else "")
                + f"\n"
                f"   Review Score: {h['review_score']}/10 | Rooms Available: {h['rooms_available']}\n"
                f"   Amenities: {amenities_str}\n"
                f"   Breakfast: {'✅ Included' if h['breakfast_included'] else '❌ Not included'}"
            )

        # Best recommendation
        best = matched[0]
        results.append(
            f"\n✅ RECOMMENDED: {best['name']} at ₹{best['price_per_night']:,}/night "
            f"(Score: {best['review_score']}/10)"
        )

        return "\n".join(results)

    except FileNotFoundError:
        return "Error: Hotels data file not found. Please ensure hotels.json exists in the data directory."
    except Exception as e:
        return f"Error searching hotels: {str(e)}"


@tool
def get_hotel_price(query: str) -> str:
    """
    Get the best hotel price in a city for budget estimation.

    Input format: "Goa mid-range" or "city:Goa budget:luxury nights:3"
    Returns recommended hotel name and total cost for the stay.
    """
    try:
        hotels = _load_hotels()

        parts = query.lower().split()
        city = None
        budget_type = "mid-range"
        nights = 3

        for part in parts:
            if part.startswith("city:"):
                city = part.split(":", 1)[1].strip().title()
            elif part.startswith("budget:"):
                budget_type = part.split(":", 1)[1].strip()
            elif part.startswith("nights:"):
                try:
                    nights = int(part.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif part in ["budget", "mid-range", "luxury"]:
                budget_type = part

        if not city:
            # Try first word
            words = query.title().split()
            city = words[0] if words else "Goa"

        matched = [h for h in hotels if h["city"].lower() == city.lower()]
        if not matched:
            return f"No hotels found in {city}. Estimated: ₹3000-₹6000/night"

        # Filter by budget
        if budget_type == "budget":
            filtered = [h for h in matched if h["price_per_night"] <= 2000]
        elif budget_type in ["mid-range", "mid"]:
            filtered = [h for h in matched if 2000 < h["price_per_night"] <= 8000]
        elif budget_type == "luxury":
            filtered = [h for h in matched if h["price_per_night"] > 8000]
        else:
            filtered = matched

        pool = filtered if filtered else matched
        pool.sort(key=lambda x: x["review_score"], reverse=True)
        best = pool[0]

        total = best["price_per_night"] * nights
        return (
            f"Recommended hotel in {city} ({budget_type}): {best['name']}\n"
            f"₹{best['price_per_night']:,}/night × {nights} nights = ₹{total:,} total\n"
            f"Rating: {best['rating']}⭐ | Review Score: {best['review_score']}/10"
        )

    except Exception as e:
        return f"Error getting hotel price: {str(e)}"
