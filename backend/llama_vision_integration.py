def analyze_image_llama_vision(image_path):
    try:
        print(f"[DEBUG] Starting image analysis for: {image_path}")
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
            print(f"[DEBUG] Image successfully encoded (Base64 length: {len(encoded_image)})")
        data_url = f"data:image/jpeg;base64,{encoded_image}"

        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{"role": "user", "content": [{"type": "text", "text": "Describe visible damage and material."}, {"type": "image_url", "image_url": {"url": data_url}}]}]
        )
        print(f"[DEBUG] Groq API Response: {response}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] analyze_image_llama_vision failed: {e}")
        raise