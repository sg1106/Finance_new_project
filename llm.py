import logging
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Add it to your .env file."
    )

_client = Groq(api_key=GROQ_API_KEY)

_CLASSIFIER_PROMPT = """You are a query classifier. Reply with exactly one word: YES or NO.

Is the following question related to finance, investing, trading, economics, stock markets,
cryptocurrency, personal finance, banking, or financial planning?

Question: "{query}"

Answer:"""

_SYSTEM_PROMPT = """You are FinanceIQ, a professional financial assistant with deep expertise in:
- Global equity markets (US, India NSE/BSE, EU, Asia)
- Fundamental and technical analysis
- Macroeconomics and central bank policy
- Portfolio construction and risk management
- Cryptocurrency markets
- Personal finance and retirement planning

Guidelines:
- Be concise, precise, and data-driven.
- Always note when advice depends on individual circumstances.
- Cite relevant ratios, metrics, or frameworks when appropriate.
- If a question requires real-time data you don't have, say so clearly.
- Never provide advice that should come from a licensed financial advisor without that disclaimer.
- Format responses with clear structure using markdown when helpful.
"""


def is_finance_query(prompt: str) -> bool:
    """Classify whether a query is finance-related."""
    try:
        resp = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": _CLASSIFIER_PROMPT.format(query=prompt)}],
            temperature=0,
            max_tokens=5,
        )
        result = resp.choices[0].message.content.strip().upper().rstrip(".")
        logger.debug("Classifier → '%s' for query: %s", result, prompt[:60])
        return result == "YES"
    except Exception as e:
        logger.error("Classifier error: %s", e)
        return True


def ask_financial_question(prompt: str) -> str:
    """
    Answer a finance question using Groq (Llama 3.3 70B). Returns the model's
    response as a markdown string, or an error message.
    """
    if not is_finance_query(prompt):
        return (
            "I specialise in finance topics — investing, markets, economics, "
            "and financial planning. Could you rephrase your question within that scope?"
        )
    try:
        resp = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=1024,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Groq generation error: %s", e)
        return "An error occurred while generating a response. Please try again."


def financial_llm_loop():
    """Interactive CLI loop for general finance Q&A."""
    print("\n🤖  FinanceIQ — AI Finance Assistant  (Powered by Groq)")
    print("Ask any finance question. Type 'exit' to quit.\n")

    while True:
        query = input("Question: ").strip()
        if query.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break
        if not query:
            continue

        print("\nThinking…\n")
        answer = ask_financial_question(query)
        print(answer)
        print()


if __name__ == "__main__":
    financial_llm_loop()