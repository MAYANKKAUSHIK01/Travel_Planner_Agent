"""
Places & Points of Interest Discovery Tool for the AI Travel Agent.
Reads places.json and recommends attractions based on city, type, and preferences.
"""

import json
from pathlib import Path
from langchain.tools import tool


DATA_PATH = Path(__file__).parent.parent / "data" / "places.json"


def _load_places() -> list[dict]:
    """Load places data from JSON file."""
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@tool
def search_places(query: str) -> str:
    """
    Search for tourist attractions and points of interest in a city.

    Input format: "city:Goa days:3" or "city:Delhi type:Heritage"
    Types available: Beach, Heritage, Nature, Adventure, Religious, Shopping, Cultural, Market, Monument, Garden, Activity, Promenade
    
    Returns a curated list of top attractions with entry fees, duration, and descriptions.
    """
    try:
        places = _load_places()

        parts = query.lower().split()
        city = None
        place_type = None
        days = 3

        for part in parts:
            if part.startswith("city:"):
                city = part.split(":", 1)[1].strip().title()
            elif part.startswith("type:"):
                place_type = part.split(":", 1)[1].strip().title()
            elif part.startswith("days:"):
                try:
                    days = int(part.split(":", 1)[1].strip())
                except ValueError:
                    days = 3

        if not city:
            city = query.title().split()[0]

        # Filter by city
        matched = [p for p in places if p["city"].lower() == city.lower()]

        if not matched:
            return f"No attractions found in {city}. Please check the city name."

        # Filter by type if specified
        if place_type:
            type_filtered = [p for p in matched if p["type"].lower() == place_type.lower()]
            matched = type_filtered if type_filtered else matched

        # Sort by rating
        matched.sort(key=lambda x: x["rating"], reverse=True)

        # Calculate how many places to show (approx 2-3 per day)
        num_places = min(days * 3, len(matched))
        shown = matched[:num_places]

        results = [f"🗺️ Top Attractions in {city}" + (f" ({place_type})" if place_type else "") + ":"]
        results.append("-" * 50)

        for i, p in enumerate(shown, 1):
            fee_str = f"₹{p['entry_fee']}" if p["entry_fee"] > 0 else "Free Entry"
            tags_str = ", ".join(p["tags"][:3])
            results.append(
                f"{i}. {p['name']} ({'⭐' * round(p['rating'])}  {p['rating']}/5)\n"
                f"   Type: {p['type']} | Entry: {fee_str} | Duration: ~{p['duration_hours']}h\n"
                f"   Best Time: {p['best_time']}\n"
                f"   {p['description']}\n"
                f"   Tags: {tags_str}"
            )

        return "\n".join(results)

    except FileNotFoundError:
        return "Error: Places data file not found. Please ensure places.json exists in the data directory."
    except Exception as e:
        return f"Error searching places: {str(e)}"


@tool
def build_day_itinerary(query: str) -> str:
    """
    Build a day-by-day itinerary for a city visit.

    Input format: "city:Goa days:3" or "city:Delhi days:5 type:Heritage"
    
    Returns a structured day-wise plan with morning, afternoon, and evening activities.
    Also includes entry fees and estimated time at each attraction.
    """
    try:
        places = _load_places()

        parts = query.lower().split()
        city = None
        days = 3
        place_type = None

        for part in parts:
            if part.startswith("city:"):
                city = part.split(":", 1)[1].strip().title()
            elif part.startswith("days:"):
                try:
                    days = int(part.split(":", 1)[1].strip())
                except ValueError:
                    days = 3
            elif part.startswith("type:"):
                place_type = part.split(":", 1)[1].strip().title()

        if not city:
            city = query.title().split()[0]

        days = max(1, min(days, 7))  # Cap between 1 and 7 days

        # Filter and sort places
        matched = [p for p in places if p["city"].lower() == city.lower()]
        if place_type:
            type_filtered = [p for p in matched if p["type"].lower() == place_type.lower()]
            matched = type_filtered if type_filtered else matched

        matched.sort(key=lambda x: x["rating"], reverse=True)

        if not matched:
            return f"No attractions found in {city}."

        # Build day-wise itinerary (2 places per day)
        results = [f"📅 {days}-Day Itinerary for {city}:"]
        results.append("=" * 50)

        total_entry_fees = 0
        place_idx = 0

        for day in range(1, days + 1):
            results.append(f"\n🗓️  Day {day}:")
            slots = ["🌅 Morning", "🌞 Afternoon", "🌆 Evening"]
            
            for slot_idx, slot in enumerate(slots):
                if place_idx >= len(matched):
                    place_idx = 0  # cycle through if needed

                p = matched[place_idx]
                fee_str = f"₹{p['entry_fee']}" if p["entry_fee"] > 0 else "Free"
                total_entry_fees += p["entry_fee"]
                results.append(
                    f"  {slot}: {p['name']}\n"
                    f"    ➤ {p['description'][:80]}...\n"
                    f"    ⏱️  ~{p['duration_hours']}h | Entry: {fee_str} | {p['type']}"
                )
                place_idx += 1
                
                # Skip evening if days * 3 would exceed places
                if slot_idx == 1 and len(matched) <= days * 2:
                    break

        results.append(f"\n💰 Estimated Entry Fees Total: ₹{total_entry_fees:,}")
        results.append(f"📍 All attractions in {city} | Adjust timings based on actual travel time")

        return "\n".join(results)

    except Exception as e:
        return f"Error building itinerary: {str(e)}"
