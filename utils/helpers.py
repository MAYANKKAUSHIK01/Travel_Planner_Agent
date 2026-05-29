"""
Utility helpers for the AI Travel Agent.
Includes formatting, validation, and session state management.
"""

import re
from datetime import datetime, timedelta


# Indian cities mapping for normalization
CITY_ALIASES = {
    "new delhi": "Delhi",
    "bombay": "Mumbai",
    "bengaluru": "Bangalore",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "benaras": "Varanasi",
    "benares": "Varanasi",
    "mysuru": "Mysore",
    "kochi": "Kochi",
    "cochin": "Kochi",
    "trivandrum": "Thiruvananthapuram",
}

POPULAR_ROUTES = [
    ("Delhi", "Goa"),
    ("Mumbai", "Goa"),
    ("Delhi", "Mumbai"),
    ("Delhi", "Jaipur"),
    ("Delhi", "Manali"),
    ("Mumbai", "Bangalore"),
    ("Delhi", "Bangalore"),
    ("Bangalore", "Goa"),
    ("Delhi", "Kolkata"),
    ("Mumbai", "Chennai"),
]


def normalize_city(city: str) -> str:
    """Normalize city name to standard form."""
    city = city.strip()
    lower = city.lower()
    return CITY_ALIASES.get(lower, city.title())


def parse_date(date_str: str) -> datetime | None:
    """Parse date string in various formats."""
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%B %d %Y", "%b %d %Y", "%d %B %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def extract_trip_info(query: str) -> dict:
    """
    Extract structured trip information from a natural language query.
    
    Returns dict with keys: source, destination, days, start_date, travelers, budget
    """
    info = {
        "source": None,
        "destination": None,
        "days": 3,
        "start_date": None,
        "travelers": 1,
        "budget": "mid-range",
    }

    query_lower = query.lower()

    # Extract days
    day_patterns = [
        r"(\d+)[- ]day",
        r"for (\d+) days",
        r"(\d+) nights",
    ]
    for pattern in day_patterns:
        match = re.search(pattern, query_lower)
        if match:
            info["days"] = int(match.group(1))
            break

    # Extract travelers
    traveler_patterns = [
        r"(\d+) people",
        r"(\d+) persons",
        r"(\d+) travelers",
        r"for (\d+)",
    ]
    for pattern in traveler_patterns:
        match = re.search(pattern, query_lower)
        if match:
            info["travelers"] = int(match.group(1))
            break
    
    if "couple" in query_lower or "two of us" in query_lower:
        info["travelers"] = 2
    if "solo" in query_lower or "alone" in query_lower:
        info["travelers"] = 1
    if "family" in query_lower:
        info["travelers"] = 4

    # Extract budget preference
    if any(w in query_lower for w in ["luxury", "premium", "5-star", "five star"]):
        info["budget"] = "luxury"
    elif any(w in query_lower for w in ["budget", "cheap", "backpack", "hostel", "affordable"]):
        info["budget"] = "budget"
    else:
        info["budget"] = "mid-range"

    # Extract dates
    date_patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})",
        r"(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, query_lower)
        if match:
            info["start_date"] = match.group(0)
            break

    if not info["start_date"]:
        # Default: 2 weeks from now
        info["start_date"] = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    return info


def format_inr(amount: int) -> str:
    """Format amount in Indian Rupee notation with commas."""
    return f"₹{amount:,}"


def get_season(month: int) -> str:
    """Get travel season for a given month."""
    if month in [12, 1, 2]:
        return "Winter (Peak Season)"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Post-Monsoon (Good Season)"


def get_packing_tips(destination: str, season: str) -> list[str]:
    """Get packing tips based on destination and season."""
    tips = ["📱 Download offline maps", "💊 Carry basic medicines", "🪪 Keep ID copies"]
    
    dest_lower = destination.lower()
    
    if "goa" in dest_lower:
        tips += ["👙 Beachwear & sunscreen", "🩴 Flip-flops", "🕶️ Sunglasses"]
    elif dest_lower in ["manali", "shimla", "darjeeling"]:
        tips += ["🧥 Heavy woolens", "🧤 Gloves & muffler", "👢 Waterproof boots"]
    elif dest_lower in ["rajasthan", "jaipur", "udaipur"]:
        tips += ["👒 Sun hat", "🧴 High-SPF sunscreen", "💧 Water bottle"]
    
    if "monsoon" in season.lower():
        tips += ["☂️ Waterproof raincoat", "👟 Waterproof shoes"]
    
    return tips[:6]


def sanitize_api_key(key: str) -> str:
    """Basic validation of API key format."""
    if not key:
        return ""
    key = key.strip()
    if key.startswith("sk-") and len(key) > 20:
        return key
    return ""


def get_suggested_queries() -> list[str]:
    """Return example queries to show users."""
    return [
        "Plan a 3-day trip to Goa from Delhi starting Feb 12, 2025 for 2 people",
        "I want a luxury 5-day trip to Udaipur from Mumbai for 4 people",
        "Budget backpacker trip to Manali for 4 days from Delhi, solo traveler",
        "Family trip to Jaipur for 3 days from Mumbai, mid-range budget",
        "7-day honeymoon trip to Goa from Bangalore, luxury hotels",
        "Weekend trip to Rishikesh from Delhi, 2 days, budget travel",
    ]
