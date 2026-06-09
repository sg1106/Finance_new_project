import logging
import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from financial_agent import clean_query, lookup_ticker, fetch_quote, format_quote
from llm import is_finance_query, ask_financial_question

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def _wants_json() -> bool:
    return request.headers.get("Accept", "").startswith("application/json")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/stock", methods=["POST"])
def stock_price():
    company_query = request.form.get("company", "").strip()
    if not company_query:
        error = "Please enter a company name or ticker symbol."
        if _wants_json():
            return jsonify({"error": error}), 400
        return render_template("index.html", error=error)

    query = clean_query(company_query)
    ticker, company_name = lookup_ticker(query)

    if not ticker:
        error = f"Couldn't find a ticker for '{company_query}'. Check the spelling and try again."
        if _wants_json():
            return jsonify({"error": error}), 404
        return render_template("index.html", error=error, last_query=company_query)

    data = fetch_quote(ticker)
    if not data:
        error = f"Market data for {ticker} is temporarily unavailable. Try again shortly."
        if _wants_json():
            return jsonify({"error": error}), 503
        return render_template("index.html", error=error, last_query=company_query)

    quote = format_quote(data, ticker, company_name)

    if _wants_json():
        return jsonify(quote)

    return render_template(
        "index.html",
        quote=quote,
        last_query=company_query,
    )


@app.route("/general", methods=["POST"])
def general_query():
    user_query = request.form.get("query", "").strip()
    if not user_query:
        error = "Please enter a finance-related question."
        if _wants_json():
            return jsonify({"error": error}), 400
        return render_template("index.html", error=error)

    if not is_finance_query(user_query):
        answer = (
            "I specialise in finance topics — investing, markets, economics, "
            "and financial planning. Please ask a question within that scope."
        )
        if _wants_json():
            return jsonify({"answer": answer, "finance_query": False})
        return render_template("index.html", answer=answer, last_general_query=user_query)

    answer = ask_financial_question(user_query)
    if _wants_json():
        return jsonify({"answer": answer, "finance_query": True})
    return render_template("index.html", answer=answer, last_general_query=user_query)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.errorhandler(404)
def not_found(e):
    if _wants_json():
        return jsonify({"error": "Not found"}), 404
    return render_template("index.html", error="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    logger.exception("Unhandled exception")
    if _wants_json():
        return jsonify({"error": "Internal server error"}), 500
    return render_template("index.html", error="Something went wrong. Please try again."), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
