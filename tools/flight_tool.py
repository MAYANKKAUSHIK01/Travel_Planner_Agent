"""Flight Search Tool for the AI Travel Agent."""
import json
from pathlib import Path
from langchain.tools import tool

DATA_PATH = Path(__file__).parent.parent / "data" / "flights.json"

def _load_flights():
    with open(DATA_PATH) as f:
        return json.load(f)

@tool
def search_flights(query: str) -> str:
    """Search for available flights between two cities.
    Input format: 'source:Delhi destination:Goa preference:cheapest'
    Preferences: cheapest, fastest, business. Returns top 3 flights with all details."""
    try:
        flights = _load_flights()
        parts = query.lower().split()
        source, destination, preference = None, None, "cheapest"
        for part in parts:
            if part.startswith("source:"): source = part.split(":",1)[1].title()
            elif part.startswith("destination:"): destination = part.split(":",1)[1].title()
            elif part.startswith("preference:"): preference = part.split(":",1)[1]
        if not source or not destination:
            words = query.title().replace(" To "," ").split()
            if len(words) >= 2: source, destination = words[0], words[-1]
        if not source or not destination:
            return "Error: Provide source and destination. Example: 'source:Delhi destination:Goa'"
        matched = [f for f in flights if f["source"].lower()==source.lower() and f["destination"].lower()==destination.lower()]
        if not matched:
            return f"No direct flights from {source} to {destination}."
        if preference == "fastest": matched.sort(key=lambda x: x["duration_hours"])
        elif preference == "business":
            biz = [f for f in matched if f["class"]=="Business"]
            matched = biz if biz else matched
            matched.sort(key=lambda x: x["price"])
        else:
            matched.sort(key=lambda x: x["price"])
        results = [f"Flights {source} to {destination} (pref: {preference}):"]
        for i, f in enumerate(matched[:3], 1):
            results.append(f"{i}. {f['airline']} {f['flight_number']} | {f['class']} | Dep: {f['departure_time']} Arr: {f['arrival_time']} ({f['duration_hours']}h) | Price: Rs{f['price']:,} | {'Non-stop' if f['stops']==0 else str(f['stops'])+' stop'}")
        best = matched[0]
        results.append(f"\nRECOMMENDED: {best['airline']} {best['flight_number']} at Rs{best['price']:,} departing {best['departure_time']}")
        return "\n".join(results)
    except Exception as e:
        return f"Error: {e}"

@tool
def get_flight_price(query: str) -> str:
    """Get cheapest flight price between two cities for budget. Input: 'Delhi to Goa' or 'source:Delhi destination:Goa'"""
    try:
        flights = _load_flights()
        parts = query.lower().split()
        source, destination = None, None
        for part in parts:
            if part.startswith("source:"): source = part.split(":",1)[1].title()
            elif part.startswith("destination:"): destination = part.split(":",1)[1].title()
        if not source or not destination:
            words = query.title().replace(" To "," ").split()
            if len(words) >= 2: source, destination = words[0], words[-1]
        matched = [f for f in flights if f["source"].lower()==source.lower() and f["destination"].lower()==destination.lower()]
        if not matched:
            return f"No flights from {source} to {destination}. Estimated Rs5000."
        cheapest = min(matched, key=lambda x: x["price"])
        return f"Cheapest {source}->{destination}: Rs{cheapest['price']:,} ({cheapest['airline']} {cheapest['flight_number']}, dep {cheapest['departure_time']})"
    except Exception as e:
        return f"Error: {e}"
