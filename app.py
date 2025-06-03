from flask import Flask, render_template, request
from financial_agent import lookup_ticker, get_stock_quote_finnhub, get_stock_quote_yfinance  # Adjust imports to your functions
from llm import is_finance_query, ask_financial_question  # Adjust if needed
from datetime import datetime

app = Flask(__name__)

def format_stock_data(stock_data, ticker, company_name):
    price = stock_data.get('c')
    open_price = stock_data.get('o')
    high = stock_data.get('h')
    low = stock_data.get('l')
    prev_close = stock_data.get('pc')
    timestamp = stock_data.get('t')

    if price is None or open_price is None:
        return "Stock data incomplete or unavailable."

    change = price - open_price
    change_percent = (change / open_price) * 100 if open_price else 0
    last_trading_day = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d') if timestamp else "N/A"

    result_text = (
        f"Stock data for {company_name} ({ticker}) as of {last_trading_day} UTC:\n"
        f"Price: ${price:.2f}\n"
        f"Change: {change:+.2f} ({change_percent:+.2f}%)\n"
        f"Open: ${open_price:.2f}\n"
        f"High: ${high:.2f}\n"
        f"Low: ${low:.2f}\n"
        f"Previous Close: ${prev_close:.2f}"
    )
    return result_text

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/stock', methods=['POST'])
def stock_price():
    company_query = request.form.get('company', '').strip()
    if not company_query:
        return render_template('index.html', result="Please enter a company name or ticker.")

    ticker, company_name = lookup_ticker(company_query)
    if not ticker:
        return render_template('index.html', result=f"Could not resolve ticker for '{company_query}'. Please try again.")

    stock_data = get_stock_quote_finnhub(ticker)
    if not stock_data:
        stock_data = get_stock_quote_yfinance(ticker)

    if not stock_data:
        return render_template('index.html', result=f"Unable to fetch stock data for {ticker}.")

    result_text = format_stock_data(stock_data, ticker, company_name)
    return render_template('index.html', result=result_text)

@app.route('/general', methods=['POST'])
def general_query():
    user_query = request.form.get('query', '').strip()
    if not user_query:
        return render_template('index.html', result="Please enter a finance-related question.")

    if not is_finance_query(user_query):
        return render_template('index.html', result=" Sorry, I can only answer finance-related questions.")

    answer = ask_financial_question(user_query)
    return render_template('index.html', result=answer)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

