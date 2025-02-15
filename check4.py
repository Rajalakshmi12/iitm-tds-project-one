import requests
import os
import json


# Set up API token
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "").strip().strip('"')
project_root = os.getcwd()  # Project root folder

# OpenAI API for vision-based OCR
url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
    "Content-Type": "application/json"
}

def get_full_path(file_path):
    print(file_path)
    if os.path.isabs(file_path):
        # If it's an absolute path, make sure it's within the project root directory
        return os.path.join(project_root, file_path.lstrip('/'))  # lstrip removes the leading "/"
    else:
        return os.path.join(project_root, file_path)
    
def extract_credit_card_number():
    """Extracts credit card number from image using an LLM."""
    
    # Define file paths
    IMAGE_PATH = get_full_path("/data/credit-card.png")
    OUTPUT_FILE = get_full_path("/data/credit-card.txt")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: {IMAGE_PATH} does not exist.")
        return

    with open(IMAGE_PATH, "rb") as img_file:
        files = {"file": img_file}
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Extract only the credit card number from the image and return as string. Do not include any other text."},
                {"role": "user", "content": "Here is an image of a credit card. Extract only the number, without spaces."}
            ],
            "max_tokens": 50
        }
        
        response = requests.post(url, headers=headers, json=data, files=files)

    if response.status_code != 200:
        print(f"Error: Failed to extract text. {response.json()}")
        return

    response_data = response.json()
    print(response_data)
    
    # Extract text response from API
    if "choices" in response_data and response_data["choices"]:
        extracted_text = response_data["choices"][0]["message"]["content"]

        # Filter only numeric characters (removes spaces or dashes)
        card_number = "".join(filter(str.isdigit, extracted_text))

        if card_number:
            with open(OUTPUT_FILE, "w") as file:
                file.write(card_number)
            print(f"Credit card number extracted and saved: {OUTPUT_FILE}")
        else:
            print("Error: No valid credit card number found in response.")
    else:
        print("Error: No valid response from LLM.")


extract_credit_card_number()
