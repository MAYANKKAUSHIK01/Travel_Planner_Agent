"""
Agentic AI Travel Planning Assistant — Streamlit App
Built with LangChain + OpenAI + Open-Meteo API
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st

# Add project root to path — guard prevents duplicate entries on every Streamlit rerun
_project_root = str(Path(__file__).parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from utils.helpers import (
    get_suggested_queries, sanitize_api_key,
    extract_trip_info, POPULAR_ROUTES
)

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

  :root {
    --saffron: #FF6B35;
    --gold: #F4A261;
    --teal: #2A9D8F;
    --navy: #1A1A2E;
    --cream: #FEFAE0;
    --card-bg: #ffffff08;
    --border: #ffffff18;
  }

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Hide default Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* Hero header */
  .hero-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(255,107,53,0.3);
    position: relative;
    overflow: hidden;
  }
  .hero-header::before {
    content: '✈️';
    position: absolute;
    font-size: 120px;
    right: 40px;
    top: -10px;
    opacity: 0.08;
  }
  .hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FF6B35, #F4A261, #FFD166);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
  }
  .hero-subtitle {
    color: #aab4c8;
    font-size: 1.05rem;
    margin-top: 0.5rem;
    font-weight: 300;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(255,107,53,0.15);
    border: 1px solid rgba(255,107,53,0.4);
    color: #FF6B35;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 1rem;
  }

  /* Cards */
  .info-card {
    background: linear-gradient(135deg, rgba(26,26,46,0.8), rgba(22,33,62,0.8));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
  }
  .stat-card {
    background: linear-gradient(135deg, rgba(42,157,143,0.15), rgba(42,157,143,0.05));
    border: 1px solid rgba(42,157,143,0.3);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: transform 0.2s;
  }
  .stat-card:hover { transform: translateY(-2px); }
  .stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #2A9D8F;
  }
  .stat-label { font-size: 0.8rem; color: #8899aa; font-weight: 500; }

  /* Suggestion chips */
  .suggestion-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.5rem 0 1rem 0; }
  .chip {
    background: rgba(244,162,97,0.1);
    border: 1px solid rgba(244,162,97,0.3);
    color: #F4A261;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
    display: inline-block;
  }
  .chip:hover {
    background: rgba(244,162,97,0.25);
    border-color: rgba(244,162,97,0.6);
    transform: translateY(-1px);
  }

  /* Tool step badges */
  .tool-step {
    background: rgba(42,157,143,0.1);
    border-left: 3px solid #2A9D8F;
    border-radius: 0 8px 8px 0;
    padding: 6px 12px;
    margin: 4px 0;
    font-size: 0.82rem;
    color: #7ecac3;
    font-family: 'DM Mono', monospace;
  }

  /* Result box */
  .result-container {
    background: linear-gradient(135deg, rgba(26,26,46,0.95), rgba(15,52,96,0.95));
    border: 1px solid rgba(255,107,53,0.2);
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    line-height: 1.8;
    color: #e8edf5;
  }

  /* Input styling */
  .stTextArea textarea {
    background: rgba(26,26,46,0.8) !important;
    border: 1px solid rgba(255,107,53,0.3) !important;
    border-radius: 12px !important;
    color: #e8edf5 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
  }
  .stTextArea textarea:focus {
    border-color: rgba(255,107,53,0.7) !important;
    box-shadow: 0 0 0 2px rgba(255,107,53,0.15) !important;
  }

  /* Button */
  .stButton > button {
    background: linear-gradient(135deg, #FF6B35, #F4A261) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
    width: 100% !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(255,107,53,0.35) !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1B2A 0%, #1A1A2E 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
  }
  [data-testid="stSidebar"] .stMarkdown { color: #c5cfe0; }

  /* Expander */
  .streamlit-expanderHeader {
    background: rgba(42,157,143,0.08) !important;
    border-radius: 10px !important;
    color: #7ecac3 !important;
    font-weight: 500 !important;
  }

  /* Progress */
  .stProgress > div > div { background: linear-gradient(90deg, #FF6B35, #F4A261) !important; }

  /* History item */
  .history-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  .history-item:hover {
    background: rgba(255,107,53,0.08);
    border-color: rgba(255,107,53,0.2);
  }

  /* Section divider */
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #F4A261;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* Alert boxes */
  .tip-box {
    background: rgba(255,209,102,0.08);
    border: 1px solid rgba(255,209,102,0.25);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    color: #FFD166;
    font-size: 0.88rem;
    margin: 0.5rem 0;
  }
  .warning-box {
    background: rgba(255,107,53,0.08);
    border: 1px solid rgba(255,107,53,0.25);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    color: #FF6B35;
    font-size: 0.88rem;
    margin: 0.5rem 0;
  }
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "provider": "Google Gemini (Free)",
        "openai_api_key": "",
        "gemini_api_key": "",
        "chat_history": [],
        "query_history": [],
        "last_result": None,
        "last_steps": [],
        "is_loading": False,
        "current_query": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size:2.5rem;">🌍</div>
        <div style="font-family:'Playfair Display',serif; font-size:1.1rem; color:#F4A261; font-weight:700;">
            AI Travel Planner
        </div>
        <div style="font-size:0.75rem; color:#667788; margin-top:2px;">Powered by LangChain + LLM</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # LLM Provider selection
    st.markdown("#### 🤖 LLM Provider")
    provider = st.selectbox(
        "Choose Provider",
        options=["Google Gemini (Free)", "OpenAI"],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.provider = provider

    st.markdown("---")

    # API Key depending on selection
    if provider == "Google Gemini (Free)":
        st.markdown("#### 🔑 Gemini API Key")
        api_input = st.text_input(
            "Enter your key",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="AIzaSy... or AQ...",
            label_visibility="collapsed",
        )
        if api_input:
            api_input = api_input.strip()
            if (api_input.startswith("AIzaSy") or api_input.startswith("AQ.")) and len(api_input) > 20:
                st.session_state.gemini_api_key = api_input
                st.success("✅ Key looks valid!", icon="🔒")
            else:
                st.error("Invalid format (should start with AIzaSy or AQ.)", icon="⚠️")
        else:
            st.markdown(
                '<div style="font-size:0.75rem; color:#8899bb; margin-top:-10px;">'
                'Get a free API key at <a href="https://aistudio.google.com/" target="_blank" style="color:#F4A261; font-weight:500;">Google AI Studio ↗</a>'
                '</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown("#### 🔑 OpenAI API Key")
        api_input = st.text_input(
            "Enter your key",
            value=st.session_state.openai_api_key,
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed",
        )
        if api_input:
            cleaned = sanitize_api_key(api_input)
            if cleaned:
                st.session_state.openai_api_key = cleaned
                st.success("✅ Key looks valid!", icon="🔒")
            else:
                st.error("Invalid format (should start with sk-)", icon="⚠️")
        else:
            st.markdown(
                '<div style="font-size:0.75rem; color:#8899bb; margin-top:-10px;">'
                'Get an API key at <a href="https://platform.openai.com/" target="_blank" style="color:#F4A261; font-weight:500;">platform.openai.com ↗</a>'
                '</div>',
                unsafe_allow_html=True
            )

    st.divider()

    # Quick stats
    st.markdown("#### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number">{len(st.session_state.query_history)}</div>
            <div class="stat-label">Trips Planned</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-number">{len(st.session_state.last_steps)}</div>
            <div class="stat-label">Tools Used</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Popular Routes
    st.markdown("#### 🗺️ Popular Routes")
    for src, dst in POPULAR_ROUTES[:6]:
        if st.button(f"✈️ {src} → {dst}", key=f"route_{src}_{dst}", use_container_width=True):
            st.session_state.current_query = (
                f"Plan a 3-day trip to {dst} from {src} "
                f"starting {(datetime.now() + timedelta(days=14)).strftime('%B %d, %Y')} "
                f"for 2 people with mid-range budget."
            )
            st.rerun()

    st.divider()

    # Query History
    if st.session_state.query_history:
        st.markdown("#### 🕐 Recent Queries")
        for i, q in enumerate(reversed(st.session_state.query_history[-5:])):
            short = q[:45] + "..." if len(q) > 45 else q
            if st.button(f"↩ {short}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current_query = q
                st.rerun()

    st.divider()
    st.markdown("""
    <div style="text-align:center; color:#445566; font-size:0.75rem; padding:0.5rem;">
        Built with LangChain · Open-Meteo API<br>
        Flights · Hotels · Weather · Budget
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ──────────────────────────────────────────────────────────────

# Hero Header
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">✨ Agentic AI · LangChain Powered</div>
    <h1 class="hero-title">Your AI Travel Planning<br>Assistant for India</h1>
    <p class="hero-subtitle">
        Describe your dream trip — I'll find flights, hotels, attractions, 
        check weather & give you a complete itinerary with budget breakdown.
    </p>
</div>
""", unsafe_allow_html=True)

# Stats row
c1, c2, c3, c4 = st.columns(4)
for col, emoji, number, label in [
    (c1, "✈️", "30+", "Flight Routes"),
    (c2, "🏨", "30+", "Hotels"),
    (c3, "🗺️", "40+", "Attractions"),
    (c4, "🌤️", "Live", "Weather Data"),
]:
    with col:
        st.markdown(f"""<div class="stat-card">
            <div style="font-size:1.5rem;">{emoji}</div>
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Query Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🧳 Plan Your Trip</div>', unsafe_allow_html=True)

# Suggested queries
st.markdown("**Try one of these examples:**")
suggestions = get_suggested_queries()
cols = st.columns(3)
for i, sug in enumerate(suggestions):
    with cols[i % 3]:
        short = sug[:55] + "..." if len(sug) > 55 else sug
        if st.button(f"💡 {short}", key=f"sug_{i}", use_container_width=True):
            st.session_state.current_query = sug
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Query input
query_val = st.session_state.get("current_query", "")
query = st.text_area(
    "Describe your trip",
    value=query_val,
    placeholder=(
        "e.g. Plan a 3-day trip to Goa from Delhi starting February 12, 2025 "
        "for 2 people with mid-range budget. I love beaches and heritage sites."
    ),
    height=110,
    label_visibility="collapsed",
)

# Trip details quick-fill
with st.expander("⚙️ Quick Trip Builder (Optional — or just type above)"):
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        q_source = st.selectbox("From City", ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Hyderabad"])
        q_days = st.slider("Number of Days", 1, 7, 3)
    with qc2:
        q_dest = st.selectbox("To City", ["Goa", "Jaipur", "Udaipur", "Manali", "Mumbai", "Delhi", "Bangalore"])
        q_travelers = st.number_input("Travelers", 1, 10, 2)
    with qc3:
        q_date = st.date_input("Start Date", datetime.now() + timedelta(days=14))
        q_budget = st.selectbox("Budget", ["mid-range", "budget", "luxury"])

    if st.button("🔧 Build Query from Selections"):
        built = (
            f"Plan a {q_days}-day trip to {q_dest} from {q_source} "
            f"starting {q_date.strftime('%B %d, %Y')} for {q_travelers} people "
            f"with {q_budget} budget."
        )
        st.session_state.current_query = built
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Plan button
col_btn, col_clear = st.columns([3, 1])
with col_btn:
    plan_clicked = st.button("🚀 Plan My Trip", type="primary", use_container_width=True)
with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.current_query = ""
        st.session_state.last_result = None
        st.session_state.last_steps = []
        st.rerun()


# ─── Agent Execution ───────────────────────────────────────────────────────────
if plan_clicked and query.strip():
    active_provider = "gemini" if st.session_state.provider == "Google Gemini (Free)" else "openai"
    active_key = st.session_state.gemini_api_key if active_provider == "gemini" else st.session_state.openai_api_key

    if not active_key:
        st.markdown(f"""<div class="warning-box">
            ⚠️ Please enter your {st.session_state.provider} API key in the sidebar to run the AI agent.
        </div>""", unsafe_allow_html=True)
    else:
        # Show loading UI
        st.markdown("---")
        st.markdown('<div class="section-title">⚡ Agent Working...</div>', unsafe_allow_html=True)
        
        progress_bar = st.progress(0, text="Initializing travel agent...")
        status_container = st.empty()
        steps_container = st.empty()
        retry_notice = st.empty()
        
        tool_steps = []
        tool_messages = {
            "search_flights": "✈️ Searching available flights...",
            "get_flight_price": "💰 Checking flight prices...",
            "search_hotels": "🏨 Finding best hotels...",
            "get_hotel_price": "💰 Calculating hotel costs...",
            "search_places": "🗺️ Discovering top attractions...",
            "build_day_itinerary": "📅 Building day-wise itinerary...",
            "get_weather_forecast": "🌤️ Fetching live weather forecast...",
            "estimate_budget": "💳 Calculating total budget...",
        }

        try:
            from agent.travel_agent import run_travel_query

            progress_bar.progress(15, text="Agent initialized! Analyzing your query...")
            time.sleep(0.3)

            # Add to history
            if query not in st.session_state.query_history:
                st.session_state.query_history.append(query)

            progress_bar.progress(25, text="Calling travel tools... (this may take 20-40s)")
            retry_notice.markdown(f"""
            <div class="tip-box">
                ⏳ The AI agent is working using {st.session_state.provider}. If you hit a rate limit, it will auto-retry up to 3 times.
            </div>
            """, unsafe_allow_html=True)

            result_dict = run_travel_query(
                query=query,
                api_key=active_key,
                provider=active_provider,
                chat_history=st.session_state.chat_history[-6:],
                max_retries=3,
            )

            # Normalise result dict to match previous format
            result = {
                "output": result_dict.get("output", ""),
                "intermediate_steps": result_dict.get("steps", []),
            }

            # Extract steps
            steps = result.get("intermediate_steps", [])
            total_steps = max(len(steps), 1)
            
            for idx, (action, observation) in enumerate(steps):
                tool_name = getattr(action, "tool", "unknown")
                tool_steps.append({
                    "tool": tool_name,
                    "input": getattr(action, "tool_input", ""),
                    "output_preview": str(observation)[:120] + "..." if len(str(observation)) > 120 else str(observation),
                })
                
                msg = tool_messages.get(tool_name, f"🔧 Running {tool_name}...")
                prog = 25 + int(60 * (idx + 1) / total_steps)
                progress_bar.progress(prog, text=msg)
                
                # Show steps live
                with steps_container.container():
                    st.markdown("**🔧 Tools Called:**")
                    for step in tool_steps:
                        st.markdown(
                            f'<div class="tool-step">✅ {step["tool"]} — {step["output_preview"][:80]}</div>',
                            unsafe_allow_html=True
                        )
                time.sleep(0.1)

            retry_notice.empty()
            progress_bar.progress(95, text="Compiling your perfect itinerary...")
            time.sleep(0.3)
            progress_bar.progress(100, text="Done!")
            time.sleep(0.3)

            # Store result
            st.session_state.last_result = result.get("output", "No output generated.")
            st.session_state.last_steps = tool_steps

            # Update chat history
            st.session_state.chat_history.append({"role": "human", "content": query})
            st.session_state.chat_history.append({"role": "assistant", "content": st.session_state.last_result})
            if len(st.session_state.chat_history) > 20:
                st.session_state.chat_history = st.session_state.chat_history[-20:]

            progress_bar.empty()
            status_container.empty()

        except ImportError as e:
            import traceback
            traceback.print_exc()
            progress_bar.empty()
            st.error(f"Import error: {e}. Please install requirements: `pip install -r requirements.txt`")
        except Exception as e:
            import traceback
            traceback.print_exc()
            progress_bar.empty()
            err_msg = str(e)

            # Special diagnostics for Gemini 404 model not found
            if "gemini" in err_msg.lower() and ("404" in err_msg or "not found" in err_msg or "not_found" in err_msg):
                available_models = []
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=active_key)
                    available_models = [m.name for m in genai.list_models()]
                except Exception:
                    pass
                
                if available_models:
                    clean_models = [m.replace("models/", "") for m in available_models if "generateContent" in getattr(m, "supported_generation_methods", ["generateContent"]) or "generate_content" in str(getattr(m, "supported_generation_methods", []))]
                    if not clean_models:
                        clean_models = [m.replace("models/", "") for m in available_models]
                    models_list_str = "<br><br><strong>Active models for your key:</strong><ul>" + "".join([f"<li><code>{m}</code></li>" for m in clean_models]) + "</ul>"
                else:
                    models_list_str = "<br><br><em>(Could not retrieve available models, please double-check your key permissions)</em>"

                st.markdown(f"""
                <div class="warning-box">
                    <strong>❌ Google Gemini Model Not Found (404)</strong><br>
                    The selected model was not found or is not supported for your API key/region.<br>
                    {models_list_str}<br>
                    <strong>How to fix:</strong><br>
                    &nbsp;• Verify you entered the correct Gemini API key in the sidebar.<br>
                    &nbsp;• Let me know if you see a different model in the list above, and I will set it up for you!
                </div>
                """, unsafe_allow_html=True)
            elif "503" in err_msg or "unavailable" in err_msg.lower() or "high demand" in err_msg.lower():
                st.markdown("""
                <div class="warning-box">
                    <strong>⏳ Model Temporarily Unavailable (503)</strong><br>
                    The Gemini model is currently experiencing very high demand globally and returned a temporary 503 error.<br><br>
                    <strong>What to do:</strong><br>
                    &nbsp;• <strong>Wait 10–30 seconds</strong>, then click <em>Plan My Trip</em> again.<br>
                    &nbsp;• This is a transient Google-side issue and resolves quickly.
                </div>
                """, unsafe_allow_html=True)
            elif "api_key" in err_msg.lower() or "authentication" in err_msg.lower() or "401" in err_msg:
                st.markdown("""
                <div class="warning-box">
                    <strong>❌ Invalid API Key</strong><br>
                    Your OpenAI API key was rejected (401 Unauthorized).<br><br>
                    <strong>How to fix:</strong><br>
                    &nbsp;• Paste a valid key starting with <code>sk-</code> in the sidebar<br>
                    &nbsp;• Get a key at <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com/api-keys</a>
                </div>
                """, unsafe_allow_html=True)
            elif "quota" in err_msg.lower() or "insufficient_quota" in err_msg.lower():
                st.markdown(f"""
                <div class="warning-box">
                    <strong>💳 {st.session_state.provider} Quota Exceeded / Expired</strong><br>
                    Your account has run out of API credits or your free tier limit has been reached.<br><br>
                    <strong>How to fix:</strong><br>
                    &nbsp;• If using Gemini free tier, you may have hit the daily request limit. Try again tomorrow or use a different key.<br>
                    &nbsp;• If using OpenAI, go to <a href="https://platform.openai.com/settings/billing" target="_blank">platform.openai.com/settings/billing</a> and check your credit balance.
                </div>
                """, unsafe_allow_html=True)
            elif "rate_limit" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                st.markdown(f"""
                <div class="warning-box">
                    <strong>⏳ {st.session_state.provider} Rate Limit Reached (429)</strong><br>
                    You've hit your API rate limit.<br><br>
                    <strong>What to do:</strong><br>
                    &nbsp;• Wait <strong>30–60 seconds</strong>, then click <em>Plan My Trip</em> again<br>
                    &nbsp;• If using Gemini, check your limits at <a href="https://aistudio.google.com/" target="_blank">Google AI Studio</a><br>
                    &nbsp;• If using OpenAI, check your usage at <a href="https://platform.openai.com/usage" target="_blank">platform.openai.com/usage</a>
                </div>
                """, unsafe_allow_html=True)
            elif "timeout" in err_msg.lower() or "timed out" in err_msg.lower():
                st.markdown("""
                <div class="warning-box">
                    <strong>⌛ Request Timed Out</strong><br>
                    The AI agent took too long to respond. Please try again.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>⚠️ Unexpected Error</strong><br>
                    <code>{err_msg[:300]}</code>
                </div>
                """, unsafe_allow_html=True)


# ─── Display Results ───────────────────────────────────────────────────────────
if st.session_state.last_result:
    st.markdown("---")
    
    result_col, info_col = st.columns([3, 1])
    
    with result_col:
        st.markdown('<div class="section-title">🌴 Your Travel Itinerary</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="result-container">{st.session_state.last_result}</div>',
            unsafe_allow_html=True
        )
        
        # Download button
        st.download_button(
            label="📥 Download Itinerary (.txt)",
            data=st.session_state.last_result,
            file_name=f"travel_itinerary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with info_col:
        st.markdown('<div class="section-title">🔍 Agent Details</div>', unsafe_allow_html=True)
        
        if st.session_state.last_steps:
            st.markdown(f"**{len(st.session_state.last_steps)} tools used:**")
            for step in st.session_state.last_steps:
                with st.expander(f"🔧 {step['tool']}", expanded=False):
                    st.markdown(f"**Input:** `{str(step['input'])[:100]}`")
                    st.markdown(f"**Result Preview:**")
                    st.caption(step["output_preview"])

        st.markdown("""<div class="tip-box">
            💡 <strong>Tip:</strong> Click any Popular Route in the sidebar for instant trip ideas!
        </div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class="tip-box">
            🔄 You can ask follow-up questions like:<br>
            <em>"What if I want to extend by 2 days?"</em><br>
            <em>"Show me only luxury hotels"</em>
        </div>""", unsafe_allow_html=True)

# ─── Features Section (shown when idle) ───────────────────────────────────────
if not st.session_state.last_result:
    st.markdown("---")
    st.markdown('<div class="section-title">🎯 What This Agent Does</div>', unsafe_allow_html=True)
    
    feat_cols = st.columns(4)
    features = [
        ("✈️", "Flight Search", "Finds cheapest/fastest flights from your city using real data"),
        ("🏨", "Hotel Picks", "Recommends budget to luxury hotels filtered by your preferences"),
        ("🌤️", "Live Weather", "Real-time forecasts via Open-Meteo API — no key needed"),
        ("📅", "Day Planner", "Builds morning-to-evening itineraries across all your days"),
        ("🎫", "Top Attractions", "Discovers POIs with entry fees, timing, and descriptions"),
        ("💰", "Budget Calc", "Full cost breakdown: flight + hotel + food + transport + fees"),
        ("🧠", "AI Reasoning", "ReAct agent explains why it chose each option"),
        ("💬", "Multi-turn", "Chat to refine — extend days, change budget, add preferences"),
    ]
    
    for i, (emoji, title, desc) in enumerate(features):
        with feat_cols[i % 4]:
            st.markdown(f"""<div class="info-card">
                <div style="font-size:1.8rem; margin-bottom:0.4rem;">{emoji}</div>
                <div style="font-weight:600; color:#F4A261; font-size:0.95rem; margin-bottom:0.3rem;">{title}</div>
                <div style="color:#8899bb; font-size:0.82rem; line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)
