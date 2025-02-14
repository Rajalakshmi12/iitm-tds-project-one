import requests

# Define the URL for the POST request
url = "https://localhost:8000/read?path=eee"

# Send the POST request
response = requests.get(url)

# Check if the response status code is HTTP 200
if response.status_code == 200:
    print("Success! Response status is HTTP 200.")
    print("Response body:", response.text)
else:
    print(f"Error: Received status code {response.status_code}")
