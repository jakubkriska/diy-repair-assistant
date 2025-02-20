# Imports
import markdown
import os
import yaml
import requests
import logging
import json
import re   
import torch
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from colorama import Fore, Style, init
from flask_cors import CORS
from llama_vision_integration import analyze_image_llama_vision  # New integration module
from PIL import Image

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Terminal history settings
MAX_HISTORY_LINES = 15
terminal_history = []  # Store chat output history

# Load environment variables from .env
load_dotenv()

# Get API key and URL from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")

# Check if the variables are set correctly
if not GROQ_API_KEY:
    raise ValueError("Error: GROQ_API_KEY is not set. Please check your .env file.")
if not GROQ_API_URL:
    raise ValueError("Error: GROQ_API_URL is not set. Please check your .env file.")

# Load YAML configuration
try:
    with open("config.yaml", "r") as file:
        bot_config = yaml.safe_load(file)
        print(json.dumps(bot_config, indent=2))  # Debug: Check YAML data
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
    return not any(keyword in message_lower for keyword in irrelevant_keywords)

def generate_response_with_context(user_input):
    """
    Sends user input and conversation history to Groq API and returns the chatbot's response.
    """
    conversation_history.append({"role": "user", "content": user_input})
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": bot_config['workflow']['features']['opening_statement']}] + conversation_history,
        "max_tokens": 800
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url=GROQ_API_URL, headers=headers, json=data, timeout=10)
        print("Raw API Response:", json.dumps(response.json(), indent=2))  # Debug print
        if response.status_code == 200:
            api_response = response.json()
            response_text = api_response.get("choices", [{}])[0].get("message", {}).get("content", "No content").strip()
            formatted_response = apply_yaml_format(response_text) if "response_format" in bot_config else f"{response_text} 😊 Keep going, you're doing great!"
            conversation_history.append({"role": "assistant", "content": formatted_response})
            if len(conversation_history) > 10:
                conversation_history.pop(0)
            return format_response(formatted_response)
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
            print("Final formatted response before sending to frontend:", repr(formatted_response))
            return formatted_response.replace("\n", "<br>")
        except KeyError as e:
            logging.error("Missing data for response formatting: %s", e)
    return raw_response.replace("\n", "<br>")

def parse_response_data(response_text):
    """
    Extract relevant information from the response text.
    """
    response_lines = response_text.split("\n")
    response_data = {}
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
    response_text = markdown.markdown(response_text)
    lines = response_text.split("\n")
    formatted_lines = []
    for line in lines:
        if line.strip().startswith("<ul>") or line.strip().startswith("<li>") or line.strip().isdigit():
            formatted_lines.append(line)
        else:
            formatted_lines.append(f"<p>{line.strip()}</p>")
    return "".join(formatted_lines)

def print_response_with_history(response):
    """
    Print the bot response with limited terminal history and color formatting.
    """
    formatted_response = f"{Fore.MAGENTA}\n-----------------------------------\n"
    formatted_response += f"Bot: {Fore.LIGHTBLACK_EX}{response.splitlines()[0]}\n"
    if len(response.splitlines()) > 1:
        for line in response.splitlines()[1:]:
            formatted_response += "    " + line + "\n"
    formatted_response += f"{Fore.MAGENTA}-----------------------------------\n"
    terminal_history.append(formatted_response)
    if len(terminal_history) > MAX_HISTORY_LINES:
        terminal_history.pop(0)
    os.system('cls' if os.name == 'nt' else 'clear')
    for line in terminal_history:
        print(line)

# HTML interface route
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
            body { font-family: Arial, sans-serif; margin: 20px; padding: 10px; background-color: #f4f4f4; }
            .chat-box { border: 1px solid #ccc; padding: 15px; background-color: #fff; max-width: 600px; margin: 0 auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }
            .message { margin: 10px 0; padding: 8px; border-radius: 4px; }
            .user-message { background-color: #d1e7dd; text-align: right; }
            .bot-message { background-color: #f8d7da; }
            input[type="text"] { width: calc(100% - 50px); padding: 10px; margin: 10px 0; }
            button { padding: 10px 15px; background-color: #007bff; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
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
                addMessage('You', message, 'user-message');
                inputElement.value = '';
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
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
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type. Use Content-Type: application/json"}), 415

    user_input = request.json.get("message", "")
    image_analysis_results = request.json.get("image_analysis_results", None)  # ⬅️ Get image results

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # ✅ If image analysis results are provided, append them to user input
    if image_analysis_results:
        user_input += f"\n[Image Analysis Results: {image_analysis_results}]"

    if not is_relevant_message(user_input):
        return jsonify({"response": "I’d love to help you with a repair! 😊 Let’s focus on fixing something."})

    bot_response = generate_response_with_context(user_input)
    print("Final bot response:", bot_response)
    return jsonify({"response": bot_response})

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        print("[ERROR] No file part in the request.")
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        print("[ERROR] No selected file.")
        return jsonify({'message': 'No selected file'}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        print(f"[DEBUG] File saved at: {file_path}")
        try:
            analysis = analyze_image_llama_vision(file_path)
            print(f"[DEBUG] Image Analysis Results: {analysis}")
            return jsonify({'image_analysis_results': analysis}), 200
        except Exception as e:
            print(f"[ERROR] Image analysis failed: {e}")
            return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
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
                        print("    " + line)
                print(f"{Fore.MAGENTA}-----------------------------------\n")
        else:
            print("Invalid mode. Use 'web' or 'terminal'.")