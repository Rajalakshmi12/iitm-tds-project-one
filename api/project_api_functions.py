from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import openai
import uvicorn
import os
import sqlite3
import subprocess
import json
import requests
from datetime import datetime
import numpy as np
import dateutil.parser  # To auto-detect date formats

# Load the AI Proxy token from the environment
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "").strip().strip('"')


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
    wednesday_count = 0

    """Count Wednesdays in a given dates file and write to output file as mentioned in the Project Requirement"""
    with open(file_path, 'r') as file:
        for line in file:
            date_str = line.strip()
            try:
                # Automatically detect and parse date format
                date_obj = dateutil.parser.parse(date_str)
                
                # Check if it's a Wednesday (2 = Wednesday)
                if date_obj.weekday() == 2:
                    wednesday_count += 1

            except ValueError:
                print(f"Skipping invalid date: {date_str}")
    
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
    print(url)
    
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




def format_markdown(file_path: str):
    
    # Move this to a function
    if not (path.startswith("/data/") or path.startswith("data/")):
        raise HTTPException(status_code=400, detail="Raji Access to this path is not allowed. Only files under '/data' are allowed.")
    
    full_path = get_full_path(file_path)
    print(f"fullpath: {full_path}")
    
    # Return the content of the specified file
    if os.path.exists(full_path):    
        os.system(f'npx prettier@3.4.2 --write "{full_path}"')
        print(f"Formatted: {full_path}")

def calculate_gold_ticket_sales():
    # Config directory for storing files
    path = "/data/ticket-sales.db"
    output_path = "/data/ticket-sales-gold.txt"
    DB_PATH = get_full_path(path)
    OUTPUT_FILE = get_full_path(output_path)

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query to calculate total sales for 'Gold' ticket type
        cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
        total_sales = cursor.fetchone()[0] or 0  # Default to 0 if no sales

        # Write the total sales to the output file
        with open(OUTPUT_FILE, "w") as file:
            file.write(str(total_sales))

        return f"Total sales for 'Gold' tickets: {total_sales}"

    except Exception as e:
        print(f"Error: {e}")

    finally:
        conn.close()
    
def get_full_path(file_path: str):
    
    print(file_path)
    if os.path.isabs(file_path):
        # If it's an absolute path, make sure it's within the project root directory
        return os.path.join(project_root, file_path.lstrip('/'))  # lstrip removes the leading "/"
    else:
        return os.path.join(project_root, file_path)
    

def find_most_similar_comments(path):

    # Define paths
    COMMENTS_FILE = get_full_path(path)
    
    output_path = "/data/comments-similar.txt"
    OUTPUT_FILE = get_full_path(output_path)

    # Read all comments
    with open(COMMENTS_FILE, "r", encoding="utf-8") as file:
        comments = [line.strip() for line in file.readlines() if line.strip()]

    if len(comments) < 2:
        print("Error: Not enough comments to compare.")

    # Generate embeddings for all comments
    embeddings = {comment: get_embedding(comment) for comment in comments}
    
    # Find the most similar pair
    most_similar_pair = None
    highest_similarity = -1

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):  # Compare unique pairs
            sim = cosine_similarity(embeddings[comments[i]], embeddings[comments[j]])
            if sim > highest_similarity:
                highest_similarity = sim
                most_similar_pair = (comments[i], comments[j])    

    if most_similar_pair:
        # Write the most similar comments to the output file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
            out_file.write(f"{most_similar_pair[0]}\n{most_similar_pair[1]}")
        return f"Most similar comments saved to {OUTPUT_FILE}"

def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        print("Error: One or both embeddings are None")
        return 0  # Return a default similarity score
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# Function to generate embeddings using OpenAI
def get_embedding(text):
    
    url = "http://aiproxy.sanand.workers.dev/openai/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
        
    }
    data = {
        "model": "text-embedding-3-small",
        "input": [text]
    }

    response = requests.post(url, json=data, headers=headers)
    
    # Ensure request was successful with status 200
    if response.status_code != 200:
        print(f"API Error ({response.status_code}): {response.text}")
        return None
    
    try:
        data = response.json()  # Convert response to JSON
        return np.array(data["data"][0]["embedding"])
    
    except Exception as e:
        print(f"Error processing API response: {e}")
        return None


# Task execution handler
def execute_task(task_description: str):
    # Generate a concise prompt based on the task description
    prompt = f"Parse the task: '{task_description}' and determine what action to perform. Provide only the action, no additional explanation."

    # Call the AI Proxy to parse the task
    action = call_ai_proxy(prompt)

    if action:
        content = action['choices'][0]['message']['content']
        print(f"Action determined by LLM: {content}")

        # Match action to specific tasks
        if "format" in content.lower() and "prettier" in content.lower():
            print("calling markdown")
            format_markdown("/data/format.md")

        elif "count" in content.lower() and "wednesday" in content.lower():
            return count_wednesdays(f"{config['root']}/dates.txt")
        elif "sort" in content.lower() and "contacts" in content.lower():
            return sort_contacts(f"{config['root']}/contacts.json")
        elif "log" in content.lower() and "write" in content.lower():
            return write_first_log_line(f"{config['root']}/logs/")
        elif ("analyze" in content.lower() and "tickets" in content.lower()) or ("analyze" in content.lower() and "sales" in content.lower()):
            return calculate_gold_ticket_sales()
        elif ("comments" in content.lower() and "similarity" in content.lower()) or ("compare" in content.lower() and "similar" in content.lower()):
            return find_most_similar_comments(f"{config['root']}/comments.txt")
        else:
            return f"Unknown action: {content}"
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
    
    if not (path.startswith("/data/") or path.startswith("data/")):
        raise HTTPException(status_code=400, detail="Raji Access to this path is not allowed. Only files under '/data' are allowed.")
    
    full_path = get_full_path(path)
    # Return the content of the specified file
    if os.path.exists(full_path):
        with open(full_path, 'r') as file:
            return {"content": file.read()}
    else:
        raise HTTPException(status_code=404, detail=f"File not found {os.path.exists}")

@app.get("/")
async def say_hello():
    return "Raji, Welcome to the custom API endpoints"

if __name__ == "__main__":
    path = "/data/dates.txt"
    
    #Code1
    full_path = get_full_path(path)

    if os.path.exists(full_path):
        with open(full_path, 'r') as file:
            #print({"content exist": file.read()})
            print("content exist")
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
    #Code3
    # print(execute_task("log write"))
    # print(execute_task("sort contacts"))
    print(execute_task("count wednesday"))
    print(execute_task("analyze sales for gold tickets"))
    print(execute_task("find most similar comments"))
    
