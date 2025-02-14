import subprocess
import sys
import requests
from fastapi import FastAPI, HTTPException
import os

# Sample task handler functions
def install_uv_and_run_datagen(user_email: str):
    """Install uvicorn and run the datagen script from the provided URL."""
    # Step 1: Install uvicorn if not already installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn"])
        print("uvicorn installed successfully")
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error installing uvicorn")

    # Step 2: Run the data generation script
    url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    params = {"user.email": user_email}

    response = requests.get(url, params=params)
    
    # Write the response in a python file and execute it
    if response.status_code == 200:
        print(response.content)
        script_filename = "datagen_script.py"  # Use a temporary path or desired location
        with open(script_filename, 'w') as file:
            file.write(response.text)
        print(f"Script downloaded successfully: {script_filename}")
        
        # Step 3: Execute the downloaded Python script
        try:
            result = subprocess.run([sys.executable, script_filename, user_email], check=True, capture_output=True, text=True)

            print("Script executed successfully")
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {e}")
            print("Error Output:", e.stderr)
        return "Data generation successful"
    else:
        raise HTTPException(status_code=500, detail="Error running data generation script")
    
    
if __name__ == "__main__":
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    user_email = "23ds3000149@ds.study.iitm.ac.in"
    install_uv_and_run_datagen(user_email)
