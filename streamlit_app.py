"""
🌍 AI Trip Planner — Premium Streamlit UI
A beautiful, agentic travel planner with streaming support,
chat history, and real-time tool-call visibility.
"""

import streamlit as st
import requests
import json
import datetime
import sseclient  # for SSE streaming

# ── Page Config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trip Planner ✈️",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global Styles ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Gradient Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141432 0%, #1e1e3f 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e0ff;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    color: #a8a8d0;
}

/* ── Hero Title ── */
.hero-title {
    text-align: center;
    padding: 1rem 0 0.5rem;
}
.hero-title h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    text-align: center;
    color: #8b8bb8;
    font-size: 1.05rem;
    font-weight: 400;
    margin-bottom: 2rem;
    letter-spacing: 0.3px;
}

/* ── Chat Bubbles ── */
.user-bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border-radius: 20px 20px 4px 20px;
    padding: 1rem 1.4rem;
    margin: 0.6rem 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
    animation: slideInRight 0.35s ease-out;
}

.assistant-bubble {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px 20px 20px 4px;
    padding: 1.2rem 1.6rem;
    margin: 0.6rem 0;
    max-width: 90%;
    color: #d0d0e8;
    font-size: 0.93rem;
    line-height: 1.7;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
    animation: slideInLeft 0.35s ease-out;
}

.assistant-bubble h1, .assistant-bubble h2, .assistant-bubble h3,
.assistant-bubble h4, .assistant-bubble h5 {
    color: #c8b6ff;
    margin-top: 1rem;
}

.assistant-bubble strong {
    color: #e0d0ff;
}

.assistant-bubble code {
    background: rgba(102, 126, 234, 0.15);
    padding: 2px 6px;
    border-radius: 4px;
    color: #b8c0ff;
}

/* ── Tool Call Card ── */
.tool-card {
    background: rgba(102, 126, 234, 0.08);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.82rem;
    color: #9fa8da;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    animation: fadeIn 0.3s ease;
}

.tool-card .tool-icon {
    font-size: 1.1rem;
}

.tool-card .tool-name {
    color: #b8c0ff;
    font-weight: 600;
}

/* ── Status Badges ── */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.status-online {
    background: rgba(76, 175, 80, 0.15);
    color: #81c784;
    border: 1px solid rgba(76, 175, 80, 0.3);
}
.status-offline {
    background: rgba(244, 67, 54, 0.15);
    color: #ef9a9a;
    border: 1px solid rgba(244, 67, 54, 0.3);
}

/* ── Input Area ── */
[data-testid="stChatInput"] {
    border-color: rgba(102, 126, 234, 0.3) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.15) !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #667eea !important;
}

/* ── Quick Suggestion Chips ── */
.chip-container {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    justify-content: center;
    margin: 1.5rem 0 2rem;
}

.chip {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 0.55rem 1.2rem;
    color: #b8b8d8;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.25s ease;
    backdrop-filter: blur(8px);
}
.chip:hover {
    background: rgba(102, 126, 234, 0.15);
    border-color: rgba(102, 126, 234, 0.4);
    color: #d0d0ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
}

/* ── Feature Cards ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}
.feature-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.3rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
}
.feature-card:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}
.feature-card .emoji {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.feature-card .title {
    color: #d0d0ff;
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 0.3rem;
}
.feature-card .desc {
    color: #8888b0;
    font-size: 0.8rem;
    line-height: 1.4;
}

/* ── Animations ── */
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.5);
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Backend Config ──────────────────────────────────────────────
BASE_URL = "http://localhost:8000"


def check_backend_health() -> bool:
    """Check if the FastAPI backend is alive."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ── Session State Initialization ────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []    # list of {"role": ..., "content": ...}
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = []  # list of tool call dicts for display
if "trip_count" not in st.session_state:
    st.session_state.trip_count = 0


# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    model_provider = st.selectbox(
        "AI Model Provider",
        options=["google", "groq"],
        index=0,
        help="Google uses Gemini 2.0 Flash; Groq uses Llama 3.3 70B",
    )

    use_streaming = st.toggle("🔄 Stream Response", value=False, help="Show tool calls in real-time")

    st.markdown("---")

    # Backend status
    is_online = check_backend_health()
    if is_online:
        st.markdown('<span class="status-badge status-online">● Backend Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-offline">● Backend Offline</span>', unsafe_allow_html=True)
        st.caption("Start the backend with: `uvicorn main:app --reload`")

    st.markdown("---")
    st.markdown("### 🛠️ Available Tools")
    tools_info = {
        "🌤️ Weather Forecast": "7-day forecasts via Open-Meteo",
        "📍 Place Search": "Attractions, restaurants, hotels via OSM",
        "💱 Currency Converter": "Live exchange rates",
        "💰 Expense Calculator": "Trip budget breakdowns",
    }
    for name, desc in tools_info.items():
        st.markdown(f"**{name}**  \n<span style='color:#8888b0;font-size:0.82rem'>{desc}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 📊 Session Stats")
    st.markdown(f"**Trips Planned:** {st.session_state.trip_count}")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.tool_calls = []
        st.session_state.trip_count = 0
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#6666a0;font-size:0.75rem'>"
        "Built with ❤️ using LangGraph + Streamlit</div>",
        unsafe_allow_html=True,
    )

# ── Main Content Area ───────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero-title">
    <h1>✈️ AI Trip Planner</h1>
</div>
<p class="hero-subtitle">Your intelligent travel companion — powered by agentic AI with real-time tools</p>
""", unsafe_allow_html=True)

# Show feature cards only when chat is empty
if not st.session_state.messages:
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="emoji">🗺️</div>
            <div class="title">Smart Itineraries</div>
            <div class="desc">Day-by-day plans with timings, tips, and local insights</div>
        </div>
        <div class="feature-card">
            <div class="emoji">🌤️</div>
            <div class="title">Live Weather</div>
            <div class="desc">7-day forecasts for any destination worldwide</div>
        </div>
        <div class="feature-card">
            <div class="emoji">💱</div>
            <div class="title">Currency Rates</div>
            <div class="desc">Real-time exchange rates and conversions</div>
        </div>
        <div class="feature-card">
            <div class="emoji">💰</div>
            <div class="title">Budget Planner</div>
            <div class="desc">Detailed cost breakdowns for every budget level</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick suggestions
    st.markdown("#### 💡 Try asking:")
    suggestion_cols = st.columns(3)
    suggestions = [
        "Plan a 5-day trip to Goa on a budget",
        "7-day luxury itinerary for Tokyo, Japan",
        "Weekend getaway to Paris for couples",
    ]
    for i, suggestion in enumerate(suggestions):
        with suggestion_cols[i]:
            if st.button(f"🔹 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()


# ── Chat History Display ────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f'<div class="assistant-bubble">', unsafe_allow_html=True)
        st.markdown(msg["content"])
        st.markdown('</div>', unsafe_allow_html=True)
    elif msg["role"] == "tool":
        icon_map = {
            "get_weather_forecast": "🌤️",
            "search_places": "📍",
            "search_hotels": "🏨",
            "convert_currency": "💱",
            "get_exchange_rate": "💱",
            "calculate_trip_budget": "💰",
            "estimate_daily_food_cost": "🍽️",
        }
        icon = icon_map.get(msg.get("tool", ""), "🔧")
        st.markdown(
            f'<div class="tool-card">'
            f'<span class="tool-icon">{icon}</span>'
            f'<span class="tool-name">{msg.get("tool", "Tool")}</span>'
            f'<span style="color:#7a7aab">→ {msg.get("preview", "")}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ── Chat Input ──────────────────────────────────────────────────
user_input = st.chat_input("Where would you like to travel? ✈️")

if user_input and user_input.strip():
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

    if not is_online:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "⚠️ The backend server is offline. Please start it with:\n\n```bash\nuvicorn main:app --reload\n```"
        })
        st.rerun()
    else:
        # ── Streaming Mode ──
        if use_streaming:
            try:
                with st.spinner("🧠 Agent is researching your trip..."):
                    response = requests.post(
                        f"{BASE_URL}/query/stream",
                        json={"question": user_input, "model_provider": model_provider},
                        stream=True,
                        timeout=120,
                    )

                    if response.status_code == 200:
                        client = sseclient.SSEClient(response)
                        final_content = ""
                        tool_placeholder = st.empty()
                        tool_log = []

                        for event in client.events():
                            try:
                                data = json.loads(event.data)
                                etype = data.get("type", "")

                                if etype == "tool_call":
                                    tool_name = data.get("tool", "unknown")
                                    args_preview = data.get("args", "")[:100]
                                    tool_log.append(f"🔧 Calling **{tool_name}**({args_preview})")
                                    tool_placeholder.markdown("\n\n".join(tool_log))
                                    st.session_state.messages.append({
                                        "role": "tool",
                                        "tool": tool_name,
                                        "preview": args_preview,
                                    })

                                elif etype == "tool_result":
                                    tool_name = data.get("tool", "tool")
                                    preview = data.get("content", "")[:80]
                                    tool_log.append(f"✅ **{tool_name}** returned results")
                                    tool_placeholder.markdown("\n\n".join(tool_log))

                                elif etype == "response":
                                    final_content = data.get("content", "")

                                elif etype == "error":
                                    final_content = f"⚠️ Error: {data.get('content', 'Unknown error')}"

                                elif etype == "done":
                                    break

                            except json.JSONDecodeError:
                                continue

                        if final_content:
                            st.session_state.messages.append({"role": "assistant", "content": final_content})
                            st.session_state.trip_count += 1

                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"⚠️ Server returned status {response.status_code}: {response.text[:300]}"
                        })

            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ Connection error: {str(e)}"
                })

        # ── Non-Streaming Mode ──
        else:
            try:
                with st.spinner("🧠 Agent is researching your trip..."):
                    response = requests.post(
                        f"{BASE_URL}/query",
                        json={"question": user_input, "model_provider": model_provider},
                        timeout=120,
                    )

                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer returned.")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.session_state.trip_count += 1
                else:
                    error_text = response.text[:300]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ Server error ({response.status_code}): {error_text}",
                    })

            except requests.Timeout:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⏱️ Request timed out. The trip plan may be too complex. Try simplifying your request."
                })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ Error: {str(e)}"
                })

        # Rerun to display the new messages
        st.rerun()


# ── Download Last Trip Plan ─────────────────────────────────────
# Show download button for the last assistant message
assistant_msgs = [m for m in st.session_state.messages if m["role"] == "assistant"]
if assistant_msgs:
    last_plan = assistant_msgs[-1]["content"]
    if len(last_plan) > 100:  # only show download for actual plans
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        md_content = f"""# ✈️ AI Trip Plan

**Generated:** {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}  
**Powered by:** AI Trip Planner

---

{last_plan}

---

*This travel plan was generated by AI. Please verify all information before your trip.*
"""
        st.download_button(
            label="📥 Download Trip Plan (.md)",
            data=md_content,
            file_name=f"Trip_Plan_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True,
        )