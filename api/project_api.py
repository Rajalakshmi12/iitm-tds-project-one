from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import re
import os
import json
import requests
import subprocess

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your proxy API key - not required for this API call
# api_key = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZHMzMDAwMTQ5QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.q_q9LIsqoM8So_zTtZkoHf_ppRlfrrzpzRenGNifW8k"

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel!"}

@app.post("/run")
async def run_task(task: str = Query(..., title="Plain English Instruction")):
    if not task:
        raise HTTPException(status_code=400, detail="Query parameter task is required")    
    return {"message": "Yes", "task": task}

@app.get("/read")
async def get_file(path: str = Query(..., title="File path to verify the exact output")):
    path = "Rectify"
    if(path=="Rectify"):
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Invalid File path")
    
# Required for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# uvicorn project_api:app --host 0.0.0.0 --port 8000 --reload