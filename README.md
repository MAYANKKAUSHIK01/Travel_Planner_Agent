# 🌍 Agentic AI Travel Planning Assistant

> An intelligent travel planner powered by **LangChain**, **OpenAI GPT**, and real-time APIs.  
> Autonomously creates complete India trip itineraries — flights, hotels, weather, attractions & budget.

---

## 📸 Features

| Feature | Description |
|---|---|
| ✈️ **Flight Search** | Finds cheapest / fastest flights from 30+ routes |
| 🏨 **Hotel Recommendations** | Budget to luxury hotels across 15+ cities |
| 🗺️ **Places & POIs** | 40+ top attractions with entry fees & timings |
| 🌤️ **Live Weather** | Real-time forecasts via Open-Meteo API (free, no key) |
| 📅 **Day-wise Itinerary** | Morning → Afternoon → Evening plans per day |
| 💰 **Budget Estimator** | Complete cost breakdown with reasoning |
| 🧠 **ReAct Agent** | LangChain agent explains every decision |
| 💬 **Multi-turn Chat** | Refine your trip in follow-up messages |

---

## 🗂️ Project Structure

```
travel_agent/
│
├── app.py                    # Streamlit web application
│
├── agent/
│   ├── __init__.py
│   └── travel_agent.py       # LangChain ReAct / ToolCalling Agent
│
├── tools/
│   ├── __init__.py
│   ├── flight_tool.py        # Flight search & price lookup
│   ├── hotel_tool.py         # Hotel recommendations & pricing
│   ├── places_tool.py        # Attractions discovery & day planning
│   ├── weather_tool.py       # Live weather via Open-Meteo API
│   └── budget_tool.py        # Budget estimation & breakdown
│
├── data/
│   ├── flights.json          # 30 flight routes across India
│   ├── hotels.json           # 30 hotels across 15 cities
│   ├── places.json           # 40 tourist attractions
│   └── city_coordinates.json # Lat/Long for weather API
│
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Utilities: parsing, formatting, validation
│
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd travel_agent
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

```bash
# Option A: Environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Option B: Enter it in the Streamlit sidebar at runtime
```

### 3. Run the App

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🧠 How the Agent Works

The agent uses the **LangChain OpenAI Tools Agent** (ReAct pattern):

```
User Query → Agent Thinks → Selects Tools → Calls Tools → 
Analyzes Results → Thinks Again → Final Answer
```

### Agent Tool Execution Flow:
1. **`search_flights`** — Find best flight from source → destination
2. **`search_hotels`** — Find top-rated hotels in destination
3. **`search_places`** — Discover attractions matching preferences
4. **`get_weather_forecast`** — Live weather for travel dates
5. **`build_day_itinerary`** — Construct day-by-day plan
6. **`estimate_budget`** — Full cost breakdown

---

## 🗺️ Supported Cities

**Destinations:** Goa, Udaipur, Delhi, Mumbai, Bangalore, Kolkata, Hyderabad, Chennai, Jaipur, Manali, Shimla

**Source Cities:** Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad

---

## 📝 Example Queries

```
Plan a 3-day trip to Goa from Delhi starting February 12, 2025 for 2 people

I want a luxury 5-day honeymoon in Udaipur from Mumbai

Budget backpacker trip to Manali for 4 days from Delhi, solo traveler

Family trip to Jaipur for 3 days, 4 people, mid-range budget from Mumbai
```

---

## 📊 Example Output

```
🌴 YOUR 3-DAY TRIP TO GOA (Feb 12–14, 2025)

✈️ FLIGHT SELECTED
SpiceJet (SG-312) | Economy
Departs: 14:00 → Arrives: 16:30 (2.5h) | Non-stop
Price: ₹3,900/person ← Selected for best price-to-value ratio

🏨 HOTEL RECOMMENDATION
Sea View Resort (⭐⭐⭐⭐)
Area: Baga | ₹3,200/night × 3 nights = ₹9,600
Amenities: Pool, Restaurant, WiFi, AC
Review Score: 8.1/10

🌤️ WEATHER OVERVIEW
Day 1 (Feb 12): Clear Sky ☀️ | High: 31°C / Low: 22°C
Day 2 (Feb 13): Partly Cloudy ⛅ | High: 30°C / Low: 21°C
Day 3 (Feb 14): Mainly Clear 🌤️ | High: 32°C / Low: 23°C

📅 DAY-WISE ITINERARY
Day 1 — Beach Arrival
  🌅 Morning: Calangute Beach (~3h) | Free Entry
  🌞 Afternoon: Fort Aguada (~2h) | ₹25
  🌆 Evening: Anjuna Flea Market (~2h) | Free
...

💰 BUDGET BREAKDOWN
  ✈️ Flights (×2):          ₹7,800
  🏨 Hotel (3 nights):      ₹9,600
  🍽️ Food & Dining:         ₹7,200
  🚗 Local Transport:        ₹3,000
  🎫 Entry Fees:               ₹850
  🛍️ Miscellaneous:          ₹3,000
  ─────────────────────────────────
  💳 TOTAL:                ₹31,450
     Per Person:           ₹15,725
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Agent** | LangChain + OpenAI GPT-4o-mini |
| **Agent Pattern** | ReAct (Reason + Act) with Tool Calling |
| **Weather API** | Open-Meteo (free, no key required) |
| **UI Framework** | Streamlit |
| **Data Storage** | JSON flat files |
| **Language** | Python 3.11+ |

---

## 🔧 Configuration

You can customize in `agent/travel_agent.py`:
- `model` — Change LLM (gpt-4o, gpt-3.5-turbo, etc.)
- `temperature` — Adjust creativity (0.0 = deterministic, 1.0 = creative)
- `max_iterations` — Max tool calls per query

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

*Built as a Capstone Project for Agentic AI using LangChain.*
