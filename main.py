from financial_agent import financial_agent
from llm import financial_llm_loop

def main():
    print("Hi! Do you want the stock price of a specific company or do you have a general finance query and want recommendations?")
    print("Type 'stock' for stock price or 'general' for general finance queries and recommendations(or 'exit' to quit):")

    while True:
        choice = input("> ").strip().lower()
        if choice == 'exit':
            print("Goodbye!")
            break
        elif choice == 'stock':
            financial_agent()  # Run stock price lookup flow
            print("\nBack to main menu. Choose again or type 'exit' to quit.")
        elif choice == 'general':
            financial_llm_loop()  # Run finance LLM flow
            print("\nBack to main menu. Choose again or type 'exit' to quit.")
        else:
            print("Please type 'stock', 'general', or 'exit'.")

if __name__ == "__main__":
    main()
