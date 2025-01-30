# Imports

import os
import yaml
import requests
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Configure logging

logging.basicConfig(level=logging.ERROR)

# Terminal history settings
MAX_HISTORY_LINES = 15
terminal_history = []  # Store chat output history

# Load environment variables from .env

load_dotenv()

# Get API key and URL from from environment variables

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")

# Check if the variables are set correctly

if not GROQ_API_KEY:
    raise ValueError("Error: GROQ_API_KEY is not set. Please check your .env file.")
if not GROQ_API_URL:
    raise ValueError("Error: GROQ_API_URL is not set. Please check your .env file.")

# Initialize Flask app

app = Flask(__name__)

# Load chatbot configuration from config.yaml

try:
    with open("config.yaml", "r") as file:
        bot_config = yaml.safe_load(file)
except FileNotFoundError:
    raise FileNotFoundError("Error: config.yaml not found. Ensure it exists in the project directory.")

# Memory to track ongoing conversation

conversation_history = []

def generate_response_with_context(user_input):
    """
    Sends user input and conversation history to Groq API and returns the chatbot's response.
    """
    # Append the user's input to the history
    conversation_history.append({"role": "user", "content": user_input})

    # Prepare the request data
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": bot_config['workflow']['features']['opening_statement']}] + conversation_history,
        "max_tokens": 800
    }

    # Send the request
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url=GROQ_API_URL, headers=headers, json=data)

    # Handle response
    if response.status_code == 200:
        try:
            response_text = response.json()["choices"][0]["message"]["content"].strip()
            conversation_history.append({"role": "assistant", "content": response_text})

            # Limit the history length to 10 messages
            if len(conversation_history) > 10:
                conversation_history.pop(0)
            return response_text

        except (KeyError, IndexError):
            logging.error("Unexpected response format from API")
            return "Error: Unexpected response format from API."
    else:
        logging.error(f"API error: {response.json()}")
        return f"Error: {response.json().get('error', 'Unknown error')}"
    
def print_response_with_history(response):
    """
    Print the bot response with limited terminal history and color formatting.
    """
    # Add new response to the history
    formatted_response = f"{Fore.MAGENTA}\n-----------------------------------\n"
    formatted_response += f"Bot: {Fore.LIGHTBLACK_EX}{response.splitlines()[0]}\n"

    # Handle multi-line responses with indentation
    if len(response.splitlines()) > 1:
        for line in response.splitlines()[1:]:
            formatted_response += "    " + line + "\n"

    formatted_response += f"{Fore.MAGENTA}-----------------------------------\n"
    
    terminal_history.append(formatted_response)

    # Keep only the last MAX_HISTORY_LINES
    if len(terminal_history) > MAX_HISTORY_LINES:
        terminal_history.pop(0)

    # Clear the terminal and display the limited history
    os.system('cls' if os.name == 'nt' else 'clear')  # 'cls' for Windows, 'clear' for Mac/Linux
    for line in terminal_history:
        print(line)

@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint to process user messages.
    """
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    bot_response = generate_response_with_context(user_input)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    # Check if running in interactive mode
    mode = input("Enter mode (web/terminal): ").strip().lower()
    if mode == "web":
        app.run(debug=True)
    elif mode == "terminal":
        print("\n========== DIY Repair Assistant ==========\n")
        print(f"{Fore.CYAN}\nWelcome to the DIY Repair Assistant! 🛠️")
        print(f"{Fore.CYAN}I’m here to help you diagnose and fix household items step-by-step.")
        print("=========================================")
        print(f"{Fore.CYAN}You can type your problem description, and I'll guide you further.")
        print("=========================================")
        print(f"{Fore.CYAN}(Type 'exit' or 'quit' to end the chat at any time.)")
        print("=========================================")
        print("\nLet's get started!\n")
        
        while True:
            user_input = input(f"{Fore.GREEN}You: ")
            if user_input.lower() in ['exit', 'quit']:
                print(f"{Fore.RED}Exiting chat... Goodbye!")
                break
            response = generate_response_with_context(user_input)
            
            print(f"{Fore.MAGENTA}\n-----------------------------------")
            
            print(f"Bot: {Fore.LIGHTBLACK_EX}{response.splitlines()[0]}")
            if len(response.splitlines()) > 1:
                for line in response.splitlines()[1:]:
                    print("    " + line)  # Indent each additional line

            print(f"{Fore.MAGENTA}-----------------------------------\n")
    else:
        print("Invalid mode. Use 'web' or 'terminal'.")

