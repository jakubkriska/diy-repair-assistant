# Imports

import markdown
import os
import yaml
import requests
import logging
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from colorama import Fore, Style, init
from flask_cors import CORS
import json
import re

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

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

try:
    with open("config.yaml", "r") as file:
        bot_config = yaml.safe_load(file)
        print(json.dumps(bot_config, indent=2))  # Debug: Check the structure of the loaded YAML data
except FileNotFoundError:
    raise FileNotFoundError("Error: config.yaml not found. Ensure it exists in the project directory.")

# Memory to track ongoing conversation

conversation_history = []

diagnosis_prompt = bot_config['prompts']['diagnosis']['prompt']

def is_relevant_message(message):
    """
    Checks if the user message is related to DIY repairs.
    """
    irrelevant_keywords = [
        "weather", "politics", "news", "movies", "games", "sports", "celebrities",
        "music", "AI", "programming", "science", "history", "relationships", "jokes"
    ]

    message_lower = message.lower()
    
    # Check if message contains irrelevant topics
    return not any(keyword in message_lower for keyword in irrelevant_keywords)

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
    
    try:
        response = requests.post(url=GROQ_API_URL, headers=headers, json=data, timeout=10)

        # Debugging: Print the raw API response
        print("Raw API Response:", json.dumps(response.json(), indent=2))  # Debugging

        # Handle response
        if response.status_code == 200:
            try:
                api_response = response.json()
                print("Formatted API Response:", json.dumps(api_response, indent=2))  # Debug print

                response_text = api_response.get("choices", [{}])[0].get("message", {}).get("content", "No content").strip()

                # Apply YAML-based formatting
                formatted_response = apply_yaml_format(response_text) if "response_format" in bot_config else f"{response_text} 😊 Keep going, you're doing great!"

                # Add response to chat history
                conversation_history.append({"role": "assistant", "content": formatted_response})

                # Limit history length
                if len(conversation_history) > 10:
                    conversation_history.pop(0)

                return format_response(formatted_response)

            except (KeyError, IndexError, json.JSONDecodeError) as e:
                logging.error("Unexpected response format from API")
                logging.error(e)
                return "Error: Unexpected response format from API."

        # Handle API errors
        logging.error(f"API error: {response.json()}")
        return "Oops! It looks like I ran into a small issue. Let’s try again in a moment. 😊"

    except requests.exceptions.RequestException as e:
        logging.error("Request failed: %s", e)
        return "Error: Could not connect to the server. Please try again later."
    
def apply_yaml_format(raw_response):
    """
    Apply the response format defined in the YAML configuration.
    """
    response_format = bot_config['workflow']['features'].get('response_format', '').strip()
    response_data = parse_response_data(raw_response)

    if response_format and response_data:
        try:
            formatted_response = response_format.format(**response_data)
            print("Final formatted response before sending to frontend:", repr(formatted_response))  # Debugging
            return formatted_response.replace("\n", "<br>")  # Ensure line breaks
        except KeyError as e:
            logging.error("Missing data for response formatting: %s", e)

    return raw_response.replace("\n", "<br>")

def parse_response_data(response_text):
    """
    Extract relevant information from the response text.
    """
    response_lines = response_text.split("\n")
    response_data = {}

    # Look for patterns to extract key information
    for line in response_lines:
        if "Issue Type:" in line:
            response_data['issue_type'] = line.split(":")[1].strip()
        elif "Visible Damage:" in line:
            response_data['visible_damage'] = line.split(":")[1].strip()
        elif "Symptoms Reported:" in line:
            response_data['symptoms_reported'] = line.split(":")[1].strip()
        elif "Step 1:" in line:
            response_data['step_one'] = line.split(":")[1].strip()
        elif "Step 2:" in line:
            response_data['step_two'] = line.split(":")[1].strip()
        elif "Step 3:" in line:
            response_data['step_three'] = line.split(":")[1].strip()
        elif "Tools Required:" in line:
            response_data['tools_required'] = line.split(":")[1].strip()
        elif "Image Findings:" in line:
            response_data['image_findings'] = line.split(":")[1].strip()

    return response_data

def format_response(response_text):
    response_text = markdown.markdown(response_text)  # Convert Markdown to HTML
    
    lines = response_text.split("\n")
    formatted_lines = []
    
    for line in lines:
        if line.strip().startswith("<ul>") or line.strip().startswith("<li>") or line.strip().isdigit():
            formatted_lines.append(line)  # Preserve existing HTML lists
        else:
            formatted_lines.append(f"<p>{line.strip()}</p>")  # Wrap paragraphs in <p> tags
    
    return "".join(formatted_lines)  # Return full HTML string

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

# Route to HTML interface
@app.route("/", methods=["GET"])
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DIY Repair Assistant</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 10px;
                background-color: #f4f4f4;
            }
            .chat-box {
                border: 1px solid #ccc;
                padding: 15px;
                background-color: #fff;
                max-width: 600px;
                margin: 0 auto;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            .message {
                margin: 10px 0;
                padding: 8px;
                border-radius: 4px;
            }
            .user-message {
                background-color: #d1e7dd;
                text-align: right;
            }
            .bot-message {
                background-color: #f8d7da;
            }
            input[type="text"] {
                width: calc(100% - 50px);
                padding: 10px;
                margin: 10px 0;
            }
            button {
                padding: 10px 15px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="chat-box" id="chat-box">
            <h2>DIY Repair Assistant</h2>
            <div id="chat-messages"></div>
            <input type="text" id="user-input" placeholder="Type your message here..." />
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            async function sendMessage() {
                const inputElement = document.getElementById('user-input');
                const message = inputElement.value;

                if (!message.trim()) return;

                // Display user message
                addMessage('You', message, 'user-message');

                // Clear the input field
                inputElement.value = '';

                try {
                    // Send message to the backend
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ message })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        addMessage('Bot', data.response, 'bot-message');
                    } else {
                        addMessage('Bot', 'Error: Failed to get a response from the server.', 'bot-message');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Bot', 'Error: Could not reach the server.', 'bot-message');
                }
            }

            function addMessage(sender, text, cssClass) {
                const chatMessages = document.getElementById('chat-messages');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${cssClass}`;
                messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
                chatMessages.appendChild(messageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        </script>
    </body>
    </html>
    """)

@app.route("/chat", methods=["POST"])
def chat():
    # Check for the correct Content-Type header
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type. Use Content-Type: application/json"}), 415

    """
    API endpoint to process user messages.
    """

    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
        # Check if the message is relevant
    if not is_relevant_message(user_input):
        return jsonify({"response": "I’d love to help you with a repair! 😊 Let’s focus on fixing something"})

    bot_response = generate_response_with_context(user_input)

    print("Final bot response:", bot_response)  # Debugging print to check response format

    return jsonify({"response": bot_response})

@app.route("/upload-image", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Here you would process the image (e.g., save it, analyze it, etc.)
    # For now, we'll just return a success message
    return jsonify({"message": "Image uploaded successfully!"})

if __name__ == "__main__":
    # Skip the input prompt on auto-reload
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        # Check if running in interactive mode
        mode = input("Enter mode (web/terminal): ").strip().lower()
        if mode == "web":
            app.run(debug=True, host='0.0.0.0', port=5001)
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

