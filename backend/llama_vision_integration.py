# llama_vision_integration.py
from groq import Groq
import base64
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_image_llama_vision(image_path):
    with open(image_path, "rb") as img_file:
        data_url = f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
    response = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[{"role": "user", "content": [{"type": "text", "text": "Describe visible damage and material."}, {"type": "image_url", "image_url": {"url": data_url}}]}]
    )
    return response.choices[0].message.content