import requests
import os

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "").strip().strip('"')

url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}",   
    
}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "What is 2 + 2"}]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())