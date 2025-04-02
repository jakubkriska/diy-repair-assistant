# Imports
import markdown
import time
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
from lvl import process_image
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from werkzeug.utils import secure_filename

LOGS_DIR = "backend/logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "app.log")),  # Save logs to a file
        logging.StreamHandler()  # Also print logs in the terminal
    ]
)

# Load environment variables from .env
load_dotenv()

# Get API key and URL from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")

# Define the retry mechanism
@retry(
    stop=stop_after_attempt(3),  # Use () to instantiate
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before=lambda retry_state: logging.warning(f"Retrying API call (attempt {retry_state.attempt_number})...")
)
def fetch_groq_response(data, headers):
    """
    Sends request to Groq API with retry mechanism.
    """
    try:
        response = requests.post(url=GROQ_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as req_err:
        logging.error(f"[REQUEST ERROR] {req_err}, Retrying...")
    except requests.exceptions.Timeout:
        logging.error("[TIMEOUT] The API request timed out after 10 seconds.")
        return {"error": "The request timed out. Please try again later.", "status_code": 408}

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"[HTTP ERROR {response.status_code}] {response.text}")
        return {"error": f"API error {response.status_code}: {response.text}", "status_code": response.status_code}

    except requests.exceptions.RequestException as req_err:
        logging.error(f"[REQUEST ERROR] {req_err}")
        return {"error": "A network error occurred. Please check your internet connection and try again.", "status_code": 503}

    except Exception as err:
        logging.critical(f"[UNKNOWN ERROR] {err}")
        return {"error": "An unexpected error occurred. Please contact support.", "status_code": 500}
    
    if "error" in api_response:
        logging.error(f"[ERROR] Groq API returned an error: {api_response['error']}")
        return jsonify({"error": "Failed to get a response from the assistant."}), 500

def validate_env_vars():
    required_vars = ["GROQ_API_KEY", "GROQ_API_URL"]
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Error: {var} is missing. Check your .env file.")

validate_env_vars()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Terminal history settings
MAX_HISTORY_LINES = 15
terminal_history = []  # Store chat output history

# Load YAML configuration
try:
    with open("config.yaml", "r") as file:
        bot_config = yaml.safe_load(file)
except FileNotFoundError:
    logging.error("Error: config.yaml not found. Loading default configuration.")
    bot_config = {"workflow": {"features": {"opening_statement": "Welcome! How can I help?"}}}

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

# Ensure image analysis is included in conversation if available
image_analysis = next(
    (msg["content"] for msg in reversed(conversation_history) if "image analysis" in msg.get("content", "").lower()), 
    None
)

def generate_response_with_context(user_input):
    """
    Runs a single iteration for response generation after the vision model has refined the analysis.
    """

    conversation_history.append({"role": "user", "content": user_input})
    logging.info(f"[DEBUG] Conversation history before API call: {conversation_history}")

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": bot_config['workflow']['features']['opening_statement']}] 
                    + conversation_history[-9:],
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    api_response = fetch_groq_response(data, headers)
    response_text = api_response.get("choices", [{}])[0].get("message", {}).get("content", "No content").strip()

    conversation_history.append({"role": "assistant", "content": response_text})
    
    return response_text if response_text else "No valid response generated."
    
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
        line = line.strip()
        if line.startswith("<ul>") or line.startswith("<li>") or line.isdigit():
            formatted_lines.append(line)
        elif line:
            formatted_lines.append(f"<p>{line}</p>")
        else:
            formatted_lines.append("<br>")
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
    if request.content_type != "application/json":
        logging.warning("[BAD REQUEST] Incorrect Content-Type.")
        return jsonify({"error": "Unsupported Media Type. Use Content-Type: application/json"}), 415

    user_input = request.json.get("message", "").strip()

    if not user_input:
        logging.warning("[BAD REQUEST] No message provided.")
        return jsonify({"error": "No message provided."}), 400

    if len(user_input) > 500:
        logging.warning(f"[BAD REQUEST] Message too long ({len(user_input)} chars).")
        return jsonify({"error": "Message is too long. Please limit it to 500 characters."}), 400

    if not is_relevant_message(user_input):
        logging.info("[FILTERED] Message was unrelated to DIY repairs.")
        return jsonify({"response": "I’d love to help you with a repair! 😊 Let’s focus on fixing something."})

    try:
        bot_response = generate_response_with_context(user_input)
        logging.info(f"[USER INPUT] {user_input}")
        logging.info(f"[BOT RESPONSE] {bot_response}")
        
        return jsonify({"response": bot_response}) if bot_response else jsonify({"error": "No valid response generated."}), 500
    
    except Exception as e:
        logging.error(f"[INTERNAL ERROR] {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def wait_for_file(file_path, retries=3, delay=0.05):
    """Ensures the file is fully saved before processing."""
    for _ in range(retries):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return True
        time.sleep(delay)
    return False

@app.route('/upload-image', methods=['POST'])
def upload_image():
    global conversation_history

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    logging.info(f"[FILE UPLOADED] {file_path}")

    try:
        # Step 1: Process the image using the vision model (4 iterations)
        refined_analysis = process_image(file_path, iterations=4)

        if "Analysis failed" in refined_analysis:
            logging.error(f"[ERROR] Image analysis failed: {refined_analysis}")
            return jsonify({'error': refined_analysis}), 500

        logging.info(f"[IMAGE ANALYSIS COMPLETED] {refined_analysis}")

        # Step 2: Use the refined analysis in the text model
        text_prompt = (
            f"The user uploaded an image. The image analysis returned this: '{refined_analysis}'. "
            "Based on this, provide a detailed repair guide or troubleshooting steps."
        )
        conversation_history.append({"role": "assistant", "content": text_prompt})

        # Step 3: Generate a response using the text model (1 iteration only)
        final_response = generate_response_with_context(text_prompt)

        # Store the response in conversation history
        if final_response:
            conversation_history.append({"role": "assistant", "content": final_response})
        else:
            logging.warning("[WARNING] No final response was generated.")

        if final_response:
            logging.info(f"[FINAL RESPONSE SENT] {final_response}")
            return jsonify({'response': final_response}), 200
        else:
            logging.error("[ERROR] No valid response generated after text processing.")
            return jsonify({'error': 'No valid response generated.'}), 500

    except Exception as e:
        logging.error(f"[ERROR] Image analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__" and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    mode = input("Enter mode (web/terminal): ").strip().lower()
    
    if mode == "web":
        app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
    
    elif mode == "terminal":
        print("\n========== DIY Repair Assistant ==========\n")
        print(f"{Fore.CYAN}Welcome to the DIY Repair Assistant! 🛠️")
        print(f"{Fore.CYAN}I’m here to help you diagnose and fix household items step-by-step.")
        print("=========================================")
        print(f"{Fore.CYAN}You can type your problem description, and I'll guide you further.")
        print("=========================================")
        print(f"{Fore.CYAN}(Type 'exit' or 'quit' to end the chat at any time.)")
        print("\nLet's get started!\n")
        
        while True:
            user_input = input(f"{Fore.GREEN}You: ").strip()
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
        print("Invalid mode. Please restart and choose 'web' or 'terminal'.")