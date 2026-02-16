# ✈️ AI Trip Planner — Agentic Travel Planning

An intelligent, agentic travel planner powered by **LangGraph** with real-time tool calling. Ask it to plan any trip and it will research destinations, check weather, find hotels, convert currencies, and estimate budgets — all automatically.

![AI Trip Planner UI](agent_graph.png)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Agentic AI** | ReAct-style agent that autonomously calls tools and reasons through your request |
| 🌤️ **Live Weather** | 7-day forecasts for any city worldwide (Open-Meteo API) |
| 📍 **Place Search** | Find attractions, restaurants, and hotels via OpenStreetMap |
| 💱 **Currency Converter** | Real-time exchange rates (ExchangeRate API) |
| 💰 **Budget Planner** | Detailed trip cost breakdowns by category |
| 🔄 **Streaming Mode** | Watch the agent's tool calls in real-time via SSE |
| 📥 **Export Plans** | Download generated plans as Markdown files |
| 🎨 **Premium UI** | Dark glassmorphism theme with smooth animations |

## 🏗️ Architecture

```
User ──▶ Streamlit UI ──▶ FastAPI Backend ──▶ LangGraph Agent
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                              Weather Tool   Place Tool   Currency Tool
                                                              ▼
                                                        Expense Tool
```

## 🚀 Quick Start

### 1. Set up environment variables

Edit `.env` and add your API key(s):

```env
GOOGLE_API_KEY="your-google-api-key"    # For Gemini 2.0 Flash
GROQ_API_KEY="your-groq-api-key"        # For Llama 3.3 70B (optional)
```

> **Note:** You need at least ONE provider key. The tools (weather, places, currency) are **free** and don't require any keys.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the FastAPI backend

```bash
uvicorn main:app --reload --port 8000
```

### 4. Start the Streamlit UI (in a second terminal)

```bash
streamlit run streamlit_app.py
```

### 5. Open the app

Navigate to **http://localhost:8501** in your browser.

## 📁 Project Structure

```
AI_Trip_Planner/
├── main.py                    # FastAPI backend with /query and /query/stream endpoints
├── streamlit_app.py           # Premium Streamlit UI with chat, streaming, and export
├── agent/
│   └── workflow.py            # LangGraph ReAct agent with tool binding
├── tools/
│   ├── weather_search.py      # 7-day weather forecast (Open-Meteo, free)
│   ├── place_search.py        # Place/hotel search (OpenStreetMap Overpass, free)
│   ├── currency_converter.py  # Currency conversion (ExchangeRate API, free)
│   └── expense_calculator.py  # Trip budget calculator and food cost estimator
├── prompts/
│   └── prompt.py              # System prompt defining the agent's persona
├── utils/
│   ├── model_loader.py        # Model configuration and loading (Google/Groq)
│   └── save_to_document.py    # Export travel plans to Markdown files
├── logger/
│   └── logging.py             # Logging configuration
├── exception/
│   └── excep_handling.py      # Custom exception classes
├── .env                       # API keys (not committed)
├── requirements.txt           # Python dependencies
└── setup.py                   # Package setup
```

## 🛠️ Tools Reference

### Weather Forecast (`get_weather_forecast`)
- **API:** [Open-Meteo](https://open-meteo.com/) (free, no key required)
- Returns 7-day forecast with temperature, precipitation, and wind speed

### Place Search (`search_places`, `search_hotels`)
- **API:** [OpenStreetMap Overpass](https://overpass-api.de/) (free, no key required)  
- Searches for attractions, restaurants, and hotels within 10km radius

### Currency Converter (`convert_currency`, `get_exchange_rate`)
- **API:** [ExchangeRate API](https://open.er-api.com/) (free, no key required)
- Real-time exchange rates for 150+ currencies

### Expense Calculator (`calculate_trip_budget`, `estimate_daily_food_cost`)
- Local computation — no external API needed
- Budget breakdowns by accommodation, food, transport, activities

## 🎨 UI Features

- **Dark glassmorphism** theme with gradient backgrounds
- **Chat interface** with animated message bubbles
- **Model provider** selection (Google Gemini / Groq Llama)
- **Streaming mode** to see tool calls in real-time
- **Quick suggestion** buttons for common trip queries
- **Download** trip plans as Markdown
- **Backend health** indicator
- **Session stats** tracking

## 📝 License

MIT
