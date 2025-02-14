from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
import uvicorn
import os
import json
import re
from datetime import datetime
import requests

# Load the AI Proxy token from the environment
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")

# Validate that the token is set
if not AIPROXY_TOKEN:
    AIPROXY_TOKEN = ""
    #raise ValueError("AIPROXY_TOKEN is not set. Please export it before running the script.")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def count_wednesdays(file_path: str):
    """Count Wednesdays in a given dates file and write to output."""
    with open(file_path, 'r') as file:
        dates = file.readlines()

    wednesday_count = sum(1 for date in dates if datetime.strptime(date.strip(), '%d/%m/%Y').weekday() == 2)  # 2 = Wednesday
    with open('/data/dates-wednesdays.txt', 'w') as output_file:
        output_file.write(str(wednesday_count))
    return f"Number of Wednesdays: {wednesday_count}"

def sort_contacts(file_path: str):
    """Sort contacts by last name, then first name, and save to a new file."""
    with open(file_path, 'r') as file:
        contacts = json.load(file)
    
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    
    with open('/data/contacts-sorted.json', 'w') as output_file:
        json.dump(sorted_contacts, output_file, indent=4)
    return "Contacts sorted successfully"

def write_first_log_line(file_path: str):
    """Write the first line of the 10 most recent log files to a new file."""
    log_files = sorted([f for f in os.listdir(file_path) if f.endswith('.log')], reverse=True)
    
    with open('/data/logs-recent.txt', 'w') as output_file:
        for log_file in log_files[:10]:
            with open(os.path.join(file_path, log_file), 'r') as log:
                first_line = log.readline()
                output_file.write(first_line + "\n")
    return "First lines of recent logs written successfully"

# Endpoint to handle task automation
@app.post("/run")
async def run_task(task: str = Query(..., title="Plain English Instruction")):
    """Run the requested task based on the plain English description."""
    try:
        if "data generation" in task.lower():
            user_email = "user@example.com"  # Replace with actual logic to extract email
            return {"message": run_datagen_script(user_email)}
        
        if "count wednesdays" in task.lower():
            return {"message": count_wednesdays("/data/dates.txt")}
        
        if "sort contacts" in task.lower():
            return {"message": sort_contacts("/data/contacts.json")}
        
        if "write first log line" in task.lower():
            return {"message": write_first_log_line("/data/logs/")}
        
        # Add more conditions for other tasks here (A4 to A10)

        raise HTTPException(status_code=400, detail="Task not recognized")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def get_file(path: str = Query(..., title="File path to verify the exact output")):
    """Return the content of a specified file."""
    if os.path.exists(path):
        with open(path, 'r') as file:
            return {"content": file.read()}
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Example usage (task description passed to the function)
if __name__ == "__main__":
    # Set up the AI Proxy token and model
    AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
    openai.api_key = AIPROXY_TOKEN  # Use the token for the AI Proxy (GPT-4o-Mini)

    # Config directory for storing files
    project_root = os.getcwd()  # Project root folder
    config = {"root": f"{project_root}/data"}

    task_description = "The file /data/dates.txt contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to /data/dates-wednesdays.txt"
    execute_task(task_description)
