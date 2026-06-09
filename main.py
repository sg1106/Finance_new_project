#!/usr/bin/env python3
"""
FinanceIQ CLI — unified entry point.

  python main.py             # interactive mode (asks what you want)
  python main.py stock       # jump straight to stock lookup
  python main.py general     # jump straight to AI assistant
"""

import sys
from financial_agent import financial_agent
from llm import financial_llm_loop

BANNER = """
╔══════════════════════════════════════════╗
║          💹  FinanceIQ  v2.0             ║
║   Real-time quotes · AI finance Q&A      ║
╚══════════════════════════════════════════╝
"""

MENU = """
  [1] stock    — Look up a stock price
  [2] general  — Ask an AI finance question
  [3] exit     — Quit
"""


def main():
    print(BANNER)

    # Allow a mode to be passed as a CLI argument
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "stock":
            return financial_agent()
        if mode in {"general", "llm", "ai"}:
            return financial_llm_loop()

    print(MENU)
    while True:
        choice = input("Choose [1/2/3] or type the name: ").strip().lower()
        if choice in {"3", "exit", "quit", "q"}:
            print("Goodbye! 👋")
            break
        elif choice in {"1", "stock"}:
            financial_agent()
            print("\n— Back to main menu —")
            print(MENU)
        elif choice in {"2", "general", "ai", "llm"}:
            financial_llm_loop()
            print("\n— Back to main menu —")
            print(MENU)
        else:
            print("  Please enter 1, 2, or 3.\n")


if __name__ == "__main__":
    main()
