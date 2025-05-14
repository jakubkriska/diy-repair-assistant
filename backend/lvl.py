from groq import Groq
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment and ensure it's set
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise Exception("GROQ_API_KEY environment variable is not set")

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Function to encode the image file into a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to process the image using the Groq vision model
def process_image(image_path):
    # Encode the image and build the data URL (assumes JPEG format; change MIME type if needed)
    base64_image = encode_image(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"
    
    # Use your original prompt exactly as provided:
    chat_completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Keep your description factual, short and strictly about this piece of furniture. Describe the visible damage (type and severity of the damage), the material this piece of furniture is made of (for example plastic, metal, wood or other) and what type of furniture this is (chair, sofa, table etc.). Only describe, don't guess."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ],
        temperature=0.7,
        max_completion_tokens=512,
        top_p=0.9,
        stream=False,
        stop=None,
    )
    
    # Extract the raw analysis from the API response
    raw_analysis = chat_completion.choices[0].message.content.strip()

    return raw_analysis
