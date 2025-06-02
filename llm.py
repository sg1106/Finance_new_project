import google.generativeai as genai
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if not GEMINI_API_KEY:
    print(" Error: GEMINI_API_KEY not found in .env file.")
    exit()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model once
model = genai.GenerativeModel("gemini-2.0-flash")

def is_finance_query(prompt):
    try:
        response = model.generate_content(
            f"""You are a query classifier. Only answer YES or NO.

Determine if the following user input is a finance-related question.
Consider finance, investing, trading, economics, markets, etc.

User input: "{prompt}"
Answer:"""
        )
        answer = response.text.strip().upper()
        logging.info(f"Classifier response: {answer}")
        return answer == "YES"
    except Exception as e:
        logging.error(f"Error classifying prompt: {e}")
        return False

def ask_financial_question(prompt):
    if not is_finance_query(prompt):
        return " Sorry, I can only answer finance-related questions."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error generating content: {e}")
        return " Error generating a response. Please try again."

def financial_llm_loop():
    print("💰 Gemini Financial Assistant. Type 'exit' to quit.")
    while True:
        user_input = input("\nAsk your finance-related question: ").strip()
        if user_input.lower() == 'exit':
            print("👋 Exiting. Take care!")
            break
        answer = ask_financial_question(user_input)
        print("\n Response:")
        print(answer)

if __name__ == "__main__":
    financial_llm_loop()
