from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import openai
import uvicorn
import os
import json
import requests
from datetime import datetime

# Load the AI Proxy token from the environment
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")

# Validate that the token is set
if not AIPROXY_TOKEN:
    AIPROXY_TOKEN = ""

# Config directory for storing files
project_root = os.getcwd()  # Project root folder
config = {"root": f"{project_root}/data"}

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task functions

def count_wednesdays(file_path: str):
    """Count Wednesdays in a given dates file and write to output."""
    with open(file_path, 'r') as file:
        dates = file.readlines()
    
    wednesday_count = sum(1 for date in dates if datetime.strptime(date.strip(), '%d/%m/%Y').weekday() == 2)  # 2 = Wednesday
    with open(f'{config["root"]}/dates-wednesdays.txt', 'w') as output_file:
        output_file.write(str(wednesday_count))
    return f"Number of Wednesdays: {wednesday_count}"

def sort_contacts(file_path: str):
    """Sort contacts by last name, then first name, and save to a new file."""
    with open(file_path, 'r') as file:
        contacts = json.load(file)
    
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    
    with open(f'{config["root"]}/contacts-sorted.json', 'w') as output_file:
        json.dump(sorted_contacts, output_file, indent=4)
    return "Contacts sorted successfully"

def write_first_log_line(file_path: str):
    """Write the first line of the 10 most recent log files to a new file."""
    log_files = sorted([f for f in os.listdir(file_path) if f.endswith('.log')], reverse=True)
    
    with open(f'{config["root"]}/logs-recent.txt', 'w') as output_file:
        for log_file in log_files[:10]:
            with open(os.path.join(file_path, log_file), 'r') as log:
                first_line = log.readline()
                output_file.write(first_line + "\n")
    return "First lines of recent logs written successfully"

# AI Proxy function for task parsing
def call_ai_proxy(prompt: str):
    # Define the API URL provided as per the instructions from the course
    url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
    }
    
    # Define the data payload with model, prompt, and other parameters
    data = {
        "model": "gpt-4o-mini",  # Use GPT-4o-Mini for task parsing
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,  # Limit to ensure the response is concise
        "temperature": 0.7,  # Control the creativity of the response
    }

    try:
        # Send the POST request
        response = requests.post(url, json=data, headers=headers, timeout=50)
        return response.json()
    except Exception as e:
        print(f"Error calling AI Proxy: {e}")
        return None

# Task execution handler
def execute_task(task_description: str):
    # Generate a concise prompt based on the task description
    prompt = f"Parse the task: '{task_description}' and determine what action to perform. Provide only the action, no additional explanation."

    # Call the AI Proxy to parse the task
    action = call_ai_proxy(prompt)

    if action:
        print(f"Action determined by LLM: {action}")

        # Match action to specific tasks
        if "format" in action.lower() and "markdown" in action.lower():
            format_markdown()
        elif "count" in action.lower() and "wednesday" in action.lower():
            return count_wednesdays(f"{config['root']}/dates.txt")
        elif "sort" in action.lower() and "contacts" in action.lower():
            return sort_contacts(f"{config['root']}/contacts.json")
        elif "log" in action.lower() and "write" in action.lower():
            return write_first_log_line(f"{config['root']}/logs/")
        else:
            return f"Unknown action: {action}"
    else:
        return "No valid action found from the AI Proxy."

# Endpoint to handle task automation
@app.post("/run")
async def run_task(task: str = Query(..., title="Plain English Instruction")):
    """Run the requested task based on the plain English description."""
    try:
        result = execute_task(task)
        return {"message": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to retrieve file content for verification
@app.get("/read")
async def get_file(path: str = Query(..., title="File path to verify the exact output")):
    """Returns content of the specified file if it exists."""
    file_path = os.path.join(config["root"], path)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return {"content": file.read()}
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def say_hello():
    return "Hello, Welcome to the custom API endpoints"

if __name__ == "__main__":
    # Running FastAPI with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
