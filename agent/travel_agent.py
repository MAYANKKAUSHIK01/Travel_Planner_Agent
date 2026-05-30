"""
AI Travel Planning Agent using LangChain ReAct / Tool Calling.
Orchestrates all travel tools to produce comprehensive trip itineraries.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path — guard prevents duplicate entries on repeated imports
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from langchain_openai import ChatOpenAI
# Use direct submodule imports — langchain's top-level __init__.py sometimes
# fails to re-export AgentExecutor on Streamlit Cloud due to caching/env issues.
try:
    # Direct path — always available in langchain 0.3.x
    from langchain.agents.agent import AgentExecutor
    from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
except ImportError:
    # Last resort: top-level namespace
    from langchain.agents import AgentExecutor, create_tool_calling_agent  # type: ignore[no-redef]
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from tools import ALL_TOOLS


SYSTEM_PROMPT = """You are an expert AI Travel Planning Assistant for India. 
You have access to real-time tools to search flights, hotels, attractions, weather, and calculate budgets.

Your goal is to create COMPLETE, DETAILED, and PERSONALIZED travel itineraries.

## How You Work:
1. **Understand the Request** — Extract: source city, destination, travel dates, number of days, travelers, budget preference
2. **Gather Data** — Use tools to fetch flights, hotels, attractions, and weather  
3. **Reason and Decide** — Pick the best options based on user preferences
4. **Build Itinerary** — Create a structured day-wise plan
5. **Estimate Budget** — Provide a complete cost breakdown

## Tool Usage Strategy:
- ALWAYS call `search_flights` first if a source city is given
- ALWAYS call `search_hotels` for the destination
- ALWAYS call `search_places` or `build_day_itinerary` for attractions
- ALWAYS call `get_weather_forecast` for the travel period
- ALWAYS call `estimate_budget` at the end for a full cost summary

## Output Format:
Structure your final response EXACTLY like this:

═══════════════════════════════════════════
🌴 YOUR [N]-DAY TRIP TO [DESTINATION]
   [Start Date] – [End Date]
═══════════════════════════════════════════

✈️ FLIGHT SELECTED
[Flight details with reasoning]

🏨 HOTEL RECOMMENDATION  
[Hotel name, price, amenities with reasoning]

🌤️ WEATHER OVERVIEW
[Day-wise weather summary]

📅 DAY-WISE ITINERARY
Day 1: [Date] — [Theme]
  🌅 Morning: [Activity/Place] (~Xh)
  🌞 Afternoon: [Activity/Place] (~Xh)
  🌆 Evening: [Activity/Place] (~Xh)
  🍽️ Dinner: [Restaurant suggestion]
[Repeat for each day...]

💰 BUDGET BREAKDOWN
  ✈️ Flights: ₹X,XXX
  🏨 Hotel (X nights): ₹X,XXX  
  🍽️ Food & Dining: ₹X,XXX
  🚗 Local Transport: ₹X,XXX
  🎫 Entry Fees: ₹X,XXX
  🛍️ Miscellaneous: ₹X,XXX
  ─────────────────────────
  💳 TOTAL: ₹XX,XXX

🔍 WHY WE SELECTED THESE OPTIONS
[Brief reasoning for your choices]

📝 TRAVEL TIPS
[3-4 practical tips for the destination]

## Important Rules:
- Always explain WHY you selected a particular flight/hotel
- If no flights found, suggest the nearest alternative or road/rail options  
- Keep itineraries realistic — don't over-pack days
- Prices are in Indian Rupees (₹)
- Be enthusiastic but accurate — this is real travel planning!
"""


def create_travel_agent(api_key: str = None, provider: str = "openai", model: str = None):
    """
    Create and return a configured LangChain Travel Agent.
    
    Args:
        api_key: API key for the chosen LLM provider
        provider: LLM provider ("openai" or "gemini")
        model: Specific model string to use (e.g., "gemini-1.5-pro")
    
    Returns:
        AgentExecutor instance ready for queries
    """
    if provider.lower() == "gemini":
        # Use the native Google GenAI SDK — supports both AIzaSy and AQ. key formats.
        from langchain_google_genai import ChatGoogleGenerativeAI
        resolved_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model=model or "gemini-2.5-flash",
            temperature=0.3,
            google_api_key=resolved_key,
        )
    else:
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            streaming=True,
            max_retries=3,          # built-in retry for transient errors
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
        )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # create_tool_calling_agent works seamlessly with both OpenAI and Gemini tool calling!
    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=False,
        max_iterations=15,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )

    return agent_executor


def run_travel_query(query: str, api_key: str = None, provider: str = "openai",
                     model: str = None, chat_history: list = None, max_retries: int = 3) -> dict:
    """
    Run a travel planning query through the agent.
    Automatically retries with exponential backoff on rate-limit (429) errors.

    Args:
        query: Natural language travel request
        api_key: LLM API key
        provider: LLM provider ("openai" or "gemini")
        model: Specific model string to use
        chat_history: Optional conversation history for multi-turn
        max_retries: Maximum retry attempts on rate-limit errors (default 3)

    Returns:
        Dictionary with 'output' and 'steps' keys
    """
    agent = create_travel_agent(api_key, provider=provider, model=model)

    inputs = {
        "input": query,
        "chat_history": chat_history or [],
    }

    config = {}
    if provider.lower() == "gemini":
        from langchain_core.callbacks import BaseCallbackHandler
        class RateLimitStaggerHandler(BaseCallbackHandler):
            """Callback handler to sleep between LLM calls to prevent free tier rate limit exhaustion."""
            def __init__(self, delay_secs: float = 13.0):
                self.delay_secs = delay_secs
                self.first_call = True

            def on_llm_start(self, serialized, prompts, **kwargs):
                if not self.first_call:
                    print(f"Staggering Gemini LLM call: sleeping for {self.delay_secs}s to respect free-tier rate limits...")
                    time.sleep(self.delay_secs)
                self.first_call = False
        config["callbacks"] = [RateLimitStaggerHandler()]

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            result = agent.invoke(inputs, config=config)
            return {
                "output": result.get("output", ""),
                "steps": result.get("intermediate_steps", []),
            }
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_rate_limit = ("rate_limit" in err_str or "429" in err_str
                             or "rate limit" in err_str)
            is_unavailable = ("503" in err_str or "unavailable" in err_str
                              or "high demand" in err_str)
            if (is_rate_limit or is_unavailable) and attempt < max_retries:
                wait_secs = 5 if is_unavailable else attempt * 10  # 5s for 503, 10/20/30s for rate limit
                print(f"[{'503 unavailable' if is_unavailable else 'Rate limit'}] Waiting {wait_secs}s before retry "
                      f"{attempt + 1}/{max_retries}...")
                time.sleep(wait_secs)
                continue
            raise  # re-raise if not retriable or retries exhausted

    raise last_error  # should not reach here


if __name__ == "__main__":
    # Quick CLI test
    test_query = "Plan a 3-day trip to Goa from Delhi starting February 12, 2025 for 2 people with a mid-range budget."
    print(f"Query: {test_query}\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Set OPENAI_API_KEY environment variable to test the agent.")
    else:
        result = run_travel_query(test_query, api_key)
        print(result["output"])
