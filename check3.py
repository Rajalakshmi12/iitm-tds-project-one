import requests
import os

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "").strip().strip('"')

url = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}"
    
}
data = {
    "model": "text-embedding-3-small",
    "input": "Raji"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())