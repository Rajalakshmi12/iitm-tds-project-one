import requests
import os
import re

# Define file paths
EMAIL_FILE = "/data/email.txt"
OUTPUT_FILE = "/data/email-sender.txt"

# Get API Token
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "").strip().strip('"')

# API endpoint
url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
    "Content-Type": "application/json"
}

def extract_email_address():
    """Extracts sender's email from /data/email.txt using LLM and writes it to /data/email-sender.txt."""
    if not os.path.exists(EMAIL_FILE):
        print(f"Error: {EMAIL_FILE} does not exist.")
        return

    # Read email content
    with open(EMAIL_FILE, "r", encoding="utf-8") as file:
        email_content = file.read()

    # LLM Request
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Extract only the sender's email address from the email text."},
            {"role": "user", "content": email_content}
        ],
        "max_tokens": 50
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        print(f"Error: Failed to extract email. {response.json()}")
        return

    response_data = response.json()

    # Extract response
    if "choices" in response_data and response_data["choices"]:
        extracted_text = response_data["choices"][0]["message"]["content"]

        # Use regex to extract the email address
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", extracted_text)
        if email_match:
            sender_email = email_match.group(0)

            # Write email to file
            with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
                file.write(sender_email)

            print(f"Sender's email extracted and saved: {sender_email}")
        else:
            print("Error: No valid email found in the response.")
    else:
        print("Error: No valid response from LLM.")

# Run the function
extract_email_address()
