


import requests
import logging
from datetime import datetime
import yfinance as yf

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FINNHUB_API_KEY = "d0tkeqpr01qlvahcn8vgd0tkeqpr01qlvahcn900"

def clean_query(raw_query):
    """Remove common noise words from the query."""
    noise_words = ['stock price', 'stock', 'price', 'shares', 'quote']
    query = raw_query.lower()
    for word in noise_words:
        query = query.replace(word, '')
    return query.strip()

def lookup_ticker(company_query):
    """Use Finnhub's symbol lookup API to find ticker symbol and name."""
    url = f"https://finnhub.io/api/v1/search?q={company_query}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for result in data.get('result', []):
            if result.get('type') == 'Common Stock':
                return result.get('symbol'), result.get('description')
        if data.get('result'):
            first = data['result'][0]
            return first.get('symbol'), first.get('description')
    except Exception as e:
        logging.error(f"Error looking up ticker for '{company_query}': {e}")
    return None, None

def get_stock_quote_finnhub(symbol):
    """Fetch current stock quote from Finnhub."""
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            logging.warning(f"Finnhub access forbidden for {symbol}. Trying fallback.")
        else:
            logging.error(f"Error fetching quote for '{symbol}': {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching quote for '{symbol}': {e}")
    return None

def get_stock_quote_yfinance(symbol):
    """Fallback using yfinance for unsupported markets like India (NSE)."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        if hist.empty:
            logging.warning(f"No data in yfinance for {symbol}")
            return None

        data = {
            'c': hist['Close'][-1],
            'o': hist['Open'][-1],
            'h': hist['High'][-1],
            'l': hist['Low'][-1],
            'pc': hist['Close'][-2] if len(hist) > 1 else hist['Open'][-1],
            't': int(hist.index[-1].timestamp())
        }
        return data
    except Exception as e:
        logging.error(f"Error fetching data from yfinance for {symbol}: {e}")
        return None

def financial_agent():
    while True:
        raw_query = input("Enter company name or query (or type 'exit' to quit): ").strip()
        if raw_query.lower() == "exit":
            print("Exiting. Goodbye!")
            break

        query = clean_query(raw_query)
        logging.info(f"Searching ticker for query: '{query}'")
        ticker, company_name = lookup_ticker(query)

        if not ticker:
            print(f"Could not resolve ticker for '{raw_query}'. Please check the input.")
            continue

        logging.info(f"Found ticker: {ticker} ({company_name})")

        stock_data = get_stock_quote_finnhub(ticker)
        if not stock_data:
            logging.info("Trying yfinance fallback...")
            stock_data = get_stock_quote_yfinance(ticker)

        if not stock_data:
            print(f"Unable to fetch stock data for {ticker}. Please try again later.")
            continue

        price = stock_data.get('c')
        open_price = stock_data.get('o')
        high = stock_data.get('h')
        low = stock_data.get('l')
        prev_close = stock_data.get('pc')
        timestamp = stock_data.get('t')

        change = price - open_price if price and open_price else None
        change_percent = (change / open_price * 100) if change and open_price else None

        last_trading_day = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d') if timestamp else "N/A"

        print(f"""
Stock data for {company_name} ({ticker}) as of {last_trading_day} UTC:
Price: ${price:.2f}
Change: {change:+.2f} ({change_percent:+.2f}%)
Open: ${open_price:.2f}
High: ${high:.2f}
Low: ${low:.2f}
Previous Close: ${prev_close:.2f}
""")

if __name__ == "__main__":
    if FINNHUB_API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your Finnhub API key in the FINNHUB_API_KEY variable.")
    else:
        financial_agent()


