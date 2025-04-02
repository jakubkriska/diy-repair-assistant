# Function to process the image using the Groq vision model
def process_image(image_path):
    # Encode the image and build the data URL (assumes JPEG format; change MIME type if needed)
    base64_image = encode_image(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"
    
    # Use your original prompt exactly as provided:
    chat_completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
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