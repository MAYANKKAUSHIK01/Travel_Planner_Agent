# 🌍 Agentic AI Travel Planning Assistant (India)

> An intelligent, autonomous travel planner powered by **LangChain**, **Google Gemini 2.5 / OpenAI**, and real-time APIs.  
> Autonomously creates complete, customized trip itineraries across India — dynamically pulling flights, hotels, weather, local attractions, and budget breakdowns.

---

## 🚀 Live Demo & Streamlit Deployment
This application is fully prepared and optimized for immediate deployment on **Streamlit Community Cloud**!

* **GitHub Repository:** `https://github.com/MAYANKKAUSHIK01/Travel_Planner_Agent`
* **Local Web App Interface:** Runs seamlessly on `http://localhost:8501`.

---

## 📸 Key Features

| Feature | Description |
|---|---|
| 🤖 **Multi-LLM Support** | Seamless toggle between **Google Gemini (Free Tier)** and **OpenAI GPT** models. |
| ⚡ **Smart Rate-Limit Staggering** | Integrated `RateLimitStaggerHandler` to automatically delay sequential LLM calls by 13s on Google Free Tier, guaranteeing stable operation without hitting 429 quota exhaustion. |
| ✈️ **Flight Search** | Finds cheapest / fastest flights from 30+ real-world mapped routes. |
| 🏨 **Hotel Recommendations** | Handpicks budget to luxury hotels across 15+ major Indian cities. |
| 🗺️ **Places & POIs** | Over 40+ top tourist attractions with live coordinate parsing, entry fees, and timings. |
| 🌤️ **Live Weather** | Direct real-time forecasts via the Open-Meteo API (requires no API key). |
| 📅 **Day-wise Itinerary** | Constructs realistic Morning ➔ Afternoon ➔ Evening plans. |
| 💰 **Budget Estimator** | Provides itemized expenses with deep reasoning. |
| 🧠 **ReAct Agent Design** | Powered by LangChain's Tool Calling ReAct loop showing steps live. |

---

## 🗂️ Project Structure

```
travel_agent/
│
├── app.py                    # Sleek Streamlit Web App with Premium UI/CSS
│
├── agent/
│   ├── __init__.py
│   └── travel_agent.py       # LangChain ReAct Agent with Gemini 2.5 Flash & OpenAI
│
├── tools/
│   ├── __init__.py
│   ├── flight_tool.py        # Mapped flight searching & price calculation
│   ├── hotel_tool.py         # Hotel matching & lookup
│   ├── places_tool.py        # Attractions discovery & POI details
│   ├── weather_tool.py       # Weather fetching using city coordinates
│   └── budget_tool.py        # Global cost consolidator
│
├── data/
│   ├── flights.json          # Mock flight routes
│   ├── hotels.json           # Curated hotel data
│   ├── places.json           # Mapped tourist spots in India
│   └── city_coordinates.json # Coordinates mapping for Open-Meteo API
│
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Key validation, parsing, and text formatting helpers
│
├── .gitignore                # Clean Git version control exclusions
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/MAYANKKAUSHIK01/Travel_Planner_Agent.git
cd travel_agent
pip install -r requirements.txt
```

### 2. Configure Your API Key
The application supports both classic and modern API key formats:
* **Google Gemini (Free)**: Supports both classic `AIzaSy` and modern `AQ.` prefix keys from [Google AI Studio](https://aistudio.google.com/).
* **OpenAI**: Supports standard `sk-` prefix keys.

You can either enter your key inside the **Streamlit Web Sidebar** at runtime, or export it in your shell environment:
```bash
export OPENAI_API_KEY="sk-your-key"
# or
export GEMINI_API_KEY="AQ.your-key"
```

### 3. Run the App Locally

```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser!

---

## 🧠 Under the Hood: The ReAct Agent Loop
The LangChain Agent dynamically orchestrates tools step-by-step using modern Tool Calling:

```
User Request ➔ Parse Context ➔ Call Flight Tool ➔ Call Hotel Tool ➔ Call Weather Tool ➔ Call Places Tool ➔ Build Itinerary ➔ Consolidate Budget ➔ Explain Reasoning ➔ Output Final Travel Document
```

### ⏳ Auto-Staggering for Gemini Free Tier
To prevent the strict **5 Requests-Per-Minute (RPM)** limit on Google Gemini free tier keys, the agent is configured with a callback listener:
```python
class RateLimitStaggerHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        if not self.first_call:
            time.sleep(13.0)  # Safe delay to keep RPM strictly under 5
```
This lets the agent execute up to 15 iterations successfully without ever throwing a 429 error!

---

## 🗺️ Supported Cities
* **Source Hubs:** Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad
* **Destinations:** Goa, Udaipur, Delhi, Mumbai, Bangalore, Kolkata, Hyderabad, Chennai, Jaipur, Manali, Shimla

---

## 📝 Example Output

```text
═══════════════════════════════════════════
🌴 YOUR 2-DAY TRIP TO JAIPUR
═══════════════════════════════════════════

✈️ FLIGHT SELECTED
IndiGo 6E-341 | Economy | Departs: 07:30 AM ➔ Arrives: 08:45 AM (1.25h) | Price: ₹1,800/person

🏨 HOTEL RECOMMENDATION
Jaipur Marriott Hotel (⭐⭐⭐⭐⭐)
Price: ₹13,000/night × 2 nights = ₹26,000
Amenities: Pool, Spa, Restaurant, WiFi, Breakfast Included

🌤️ WEATHER OVERVIEW
📅 Day 1: Overcast ☁️ | High: 36°C | Low: 27°C
📅 Day 2: Overcast ☁️ | High: 36°C | Low: 26°C

📅 DAY-WISE ITINERARY
Day 1: Forts and Palaces
  🌅 Morning: Amber Fort (~3h)
  🌞 Afternoon: Hawa Mahal (~1.5h)
  🌆 Evening: Local Market Exploration
  🍽️ Dinner: Authentic Rajasthani thali at Chokhi Dhani

Day 2: Royal Heritage and Astronomy
  🌅 Morning: City Palace Jaipur (~2.5h)
  🌞 Afternoon: Jantar Mantar Jaipur (~1.5h)
  🌆 Evening: Albert Hall Museum

💰 BUDGET BREAKDOWN
  ✈️ Flights (x2):         ₹3,600
  🏨 Hotel (2 nights):     ₹26,000
  🍽️ Food & Dining:        ₹4,800
  🚗 Local Transport:      ₹2,000
  🎫 Entry Fees:           ₹1,450
  🛍️ Miscellaneous:        ₹2,000
  ───────────────────────────────
  💳 TOTAL:               ₹39,850
```

---

## 🛠️ Technology Stack

* **AI Agent Framework**: LangChain
* **LLM Foundations**: Google Gemini 2.5 Flash (`gemini-2.5-flash`) / OpenAI GPT-4o-Mini (`gpt-4o-mini`)
* **Real-time Weather**: Open-Meteo REST API
* **Web UI Layout**: Streamlit (with rich Custom CSS and glassmorphic aesthetics)
* **Language runtime**: Python 3.11+

---

## 📄 License
Licensed under the [MIT License](LICENSE). Feel free to use, modify, and build upon this workspace.

---

*Built with ❤️ as a state-of-the-art Capstone Project for Agentic AI.*

