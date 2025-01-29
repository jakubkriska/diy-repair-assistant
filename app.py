import os
import yaml
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Error: GROQ_API_KEY is not set. Please check your .env file.")

# Initialize Flask app
app = Flask(__name__)

# Load chatbot configuration from config.yaml
try:
    with open("config.yaml", "r") as file:
        bot_config = yaml.safe_load(file)
except FileNotFoundError:
    raise FileNotFoundError("Error: config.yaml not found. Ensure it exists in the project directory.")

def generate_response(user_input):
    """
    Sends user input to Groq API and returns the chatbot's response.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",  # Replace with your chosen Groq model ID
        "messages": [
            {"role": "system", "content": bot_config['workflow']['features']['opening_statement']},
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except KeyError:
        return "Error: Unexpected response format from Groq API."

@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint to process user messages.
    """
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    bot_response = generate_response(user_input)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
