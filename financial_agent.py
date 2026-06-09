import requests
import logging
import time
from datetime import datetime, timezone
from functools import lru_cache
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

NOISE_WORDS = {
    "stock", "price", "shares", "quote", "ticker",
    "limited", "ltd", "inc", "corp", "corporation", "plc",
}

NSE_SUFFIX = ".NS"
BSE_SUFFIX = ".BO"


def clean_query(raw_query: str) -> str:
    """Strip noise words and normalize the search query."""
    tokens = raw_query.lower().split()
    cleaned = " ".join(t for t in tokens if t not in NOISE_WORDS)
    return cleaned.strip() or raw_query.strip()


@lru_cache(maxsize=128)
def lookup_ticker(company_query: str) -> tuple[str | None, str | None]:
    """
    Resolve a company name or partial ticker to (symbol, description).
    Falls back through Finnhub → direct symbol check → yfinance info.
    """
    if not FINNHUB_API_KEY:
        logger.warning("FINNHUB_API_KEY not set — skipping Finnhub lookup.")
        return _yfinance_lookup(company_query)

    url = "https://finnhub.io/api/v1/search"
    params = {"q": company_query, "token": FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        results = resp.json().get("result", [])

        # Prefer Common Stock on a US exchange
        for r in results:
            if r.get("type") == "Common Stock":
                return r.get("symbol"), r.get("description")

        # Fall back to first result
        if results:
            return results[0].get("symbol"), results[0].get("description")

    except requests.exceptions.Timeout:
        logger.error("Finnhub lookup timed out for '%s'.", company_query)
    except requests.exceptions.HTTPError as e:
        logger.error("Finnhub HTTP error for '%s': %s", company_query, e)
    except Exception as e:
        logger.error("Unexpected error in Finnhub lookup: %s", e)

    return _yfinance_lookup(company_query)


def _yfinance_lookup(query: str) -> tuple[str | None, str | None]:
    """Use yfinance .info to verify a symbol directly."""
    candidates = [
        query.upper(),
        query.upper() + NSE_SUFFIX,
        query.upper() + BSE_SUFFIX,
    ]
    for sym in candidates:
        try:
            info = yf.Ticker(sym).info
            name = info.get("longName") or info.get("shortName")
            if name:
                logger.info("yfinance confirmed symbol: %s (%s)", sym, name)
                return sym, name
        except Exception:
            pass
    return None, None


def get_stock_quote_finnhub(symbol: str) -> dict | None:
    """Fetch real-time quote from Finnhub."""
    if not FINNHUB_API_KEY:
        return None
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        # Finnhub returns c=0 when the symbol is unrecognised
        if not data.get("c"):
            logger.warning("Finnhub returned zero price for %s.", symbol)
            return None
        return data
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 403:
            logger.warning("Finnhub 403 for %s — likely a non-US symbol.", symbol)
        else:
            logger.error("Finnhub quote error for %s: %s", symbol, e)
    except requests.exceptions.Timeout:
        logger.error("Finnhub quote timed out for %s.", symbol)
    except Exception as e:
        logger.error("Unexpected error fetching Finnhub quote for %s: %s", symbol, e)
    return None


def get_stock_quote_yfinance(symbol: str) -> dict | None:
    """
    Fallback quote via yfinance — works for NSE (.NS), BSE (.BO),
    and any exchange yfinance supports.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            logger.warning("yfinance returned empty history for %s.", symbol)
            return None

        latest = hist.iloc[-1]
        prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Open"]

        return {
            "c": round(float(latest["Close"]), 4),
            "o": round(float(latest["Open"]), 4),
            "h": round(float(latest["High"]), 4),
            "l": round(float(latest["Low"]), 4),
            "pc": round(float(prev_close), 4),
            "t": int(hist.index[-1].timestamp()),
            "v": int(latest.get("Volume", 0)),
        }
    except Exception as e:
        logger.error("yfinance error for %s: %s", symbol, e)
    return None


def fetch_quote(symbol: str) -> dict | None:
    """Try Finnhub first, fall back to yfinance."""
    data = get_stock_quote_finnhub(symbol)
    if data:
        return data
    logger.info("Falling back to yfinance for %s.", symbol)
    return get_stock_quote_yfinance(symbol)


def format_quote(data: dict, ticker: str, company_name: str) -> dict:
    """
    Return a structured dict of quote fields for use by Flask or CLI.
    Avoids duplication of formatting logic.
    """
    price = data.get("c") or 0
    open_price = data.get("o") or price
    high = data.get("h") or price
    low = data.get("l") or price
    prev_close = data.get("pc") or open_price
    volume = data.get("v")
    ts = data.get("t")

    change = price - prev_close
    change_pct = (change / prev_close * 100) if prev_close else 0
    last_updated = (
        datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        if ts else "N/A"
    )

    return {
        "ticker": ticker,
        "company_name": company_name,
        "price": price,
        "open": open_price,
        "high": high,
        "low": low,
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "volume": volume,
        "last_updated": last_updated,
        "positive": change >= 0,
    }


def financial_agent():
    """Interactive CLI loop for stock lookups."""
    print("\n💹  FinanceIQ — Stock Lookup")
    print("Type a company name or ticker. 'exit' to quit.\n")

    while True:
        raw = input("Query: ").strip()
        if raw.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break
        if not raw:
            continue

        query = clean_query(raw)
        ticker, company_name = lookup_ticker(query)

        if not ticker:
            print(f"  ✗  Could not resolve ticker for '{raw}'. Check the name and try again.\n")
            continue

        data = fetch_quote(ticker)
        if not data:
            print(f"  ✗  Could not fetch quote for {ticker}. Try again later.\n")
            continue

        q = format_quote(data, ticker, company_name)
        arrow = "▲" if q["positive"] else "▼"
        color = "\033[92m" if q["positive"] else "\033[91m"
        reset = "\033[0m"

        print(f"""
  {q['company_name']} ({q['ticker']})  —  {q['last_updated']}
  ─────────────────────────────────────────
  Price        {q['price']:>12,.4f}
  Change       {color}{arrow} {q['change']:+,.4f}  ({q['change_pct']:+.2f}%){reset}
  Open         {q['open']:>12,.4f}
  High         {q['high']:>12,.4f}
  Low          {q['low']:>12,.4f}
  Prev Close   {q['prev_close']:>12,.4f}""")
        if q["volume"]:
            print(f"  Volume       {q['volume']:>12,}")
        print()


if __name__ == "__main__":
    financial_agent()
