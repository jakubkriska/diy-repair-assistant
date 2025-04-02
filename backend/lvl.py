from groq import Groq
import base64
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise Exception("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=api_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path, iterations=4):
    """Processes an image multiple times, refining results at each step."""
    
    base64_image = encode_image(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"

    # Core instruction for every iteration
    general_prompt = (
        "Keep your description factual, short, and strictly about this piece of furniture. "
        "Only describe, don't guess."
    )

    # Iteration-specific refinements
    iteration_prompts = [
        
        "Step 1: Identify visible damage. Describe cracks, breaks, scratches, or any other defects. "
        "If no visible damage is found, state that explicitly, but do not assume the furniture is undamaged.",
    
        "Step 2: Reanalyze the image, ensuring that no damage was missed in Step 1. "
        "If damage was found in Step 1, confirm its severity and provide additional details."

        "Step 3: Describe the material and structure of the furniture, avoiding assumptions.",

        "Step 4: Summarize all findings from previous iterations into a final refined analysis."
    ]

    combined_analysis = []
    previous_findings = ""

    for i in range(iterations):
        prompt = f"{general_prompt}\n{iteration_prompts[i]}\n\nPrevious findings (if any): {previous_findings}"

        logging.info(f"[VISION MODEL ITERATION {i+1}] {iteration_prompts[i]}")

        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",  # Updated to correct model ID
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}}
                        ]
                    }
                ],
                temperature=0.4,
                max_completion_tokens=512
            )

            analysis = chat_completion.choices[0].message.content.strip()
            logging.info(f"[DEBUG] Vision Model Output after iteration {i+1}: {analysis}")

            # Append analysis and update previous findings
            combined_analysis.append(f"Iteration {i+1}: {analysis}")
            previous_findings += f"\nIteration {i+1}: {analysis}"

        except Exception as e:
            logging.error(f"[ERROR] Vision Model API call failed at iteration {i+1}: {e}")
            combined_analysis.append(f"Iteration {i+1}: Analysis failed.")

    # Final refined summary using all iterations
    final_summary = f"Final Refined Analysis:\n{'\n'.join(combined_analysis)}"
    return final_summary