# 💹 FinanceIQ

Real-time stock quotes and AI-powered finance insights in a single Flask app.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.x-green?style=flat-square)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange?style=flat-square)

---

## Features

- **Real-time quotes** — US, NSE/BSE, EU, and crypto tickers via Finnhub → yFinance fallback
- **AI finance assistant** — Gemini 2.5 Flash with query classification (finance-only guardrail)
- **Web UI** — dark/light mode, quick-lookup chips, responsive layout, markdown rendering
- **REST-friendly** — all routes return JSON when `Accept: application/json` is sent
- **CLI mode** — full-featured terminal interface via `main.py`

---

## Architecture

```
User
 │
 ├─ Web (Flask)  app.py
 │    ├─ /stock    → financial_agent.py → Finnhub API → yFinance fallback
 │    └─ /general  → llm.py → Gemini API (classify + answer)
 │
 └─ CLI  main.py
      ├─ stock mode   → financial_agent.financial_agent()
      └─ general mode → llm.financial_llm_loop()
```

---

## Quick Start

```bash
# 1. Clone & create virtualenv
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — add your FINNHUB_API_KEY and GEMINI_API_KEY

# 4a. Run web server
flask run              # or: python app.py

# 4b. Run CLI
python main.py
```

> **Free API keys:** [Finnhub](https://finnhub.io) · [Google AI Studio (Gemini)](https://aistudio.google.com)

---

## API Keys

| Service | Used for | Free tier |
|---------|----------|-----------|
| [Finnhub](https://finnhub.io/register) | US stock quotes | 60 req/min |
| [Google AI Studio](https://aistudio.google.com) | Gemini AI answers | Yes |
| yFinance | Fallback (NSE/BSE/crypto) | No key needed |

---

## Project Structure

```
financeiq/
├── app.py              # Flask routes + JSON API
├── financial_agent.py  # Quote fetching, ticker resolution, CLI
├── llm.py              # Gemini integration, query classifier
├── main.py             # Unified CLI entry point
├── requirements.txt
├── Procfile            # Gunicorn for Render/Heroku
├── .env.example
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## Deployment

**Render (recommended):**
1. Connect your GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:app`
4. Add `FINNHUB_API_KEY` and `GEMINI_API_KEY` as environment variables

---

## Disclaimer

For educational purposes only. FinanceIQ does not provide licensed financial advice.
