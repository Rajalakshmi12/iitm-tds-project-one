from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
from typing import List
import numpy as np
import re
import json
import requests

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

@app.get("/execute")
async def get_wiki(country: str = Query(..., title="Country")):
    wiki_url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    response = requests.get(wiki_url)
    
    if response.status_code != 200:
        return {"error": "Page not found or invalid request"}
    
    # Parse HTML
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract headings
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    result = []
    # Generate Markdown outline from the headings
    markdown_outline = "## Contents\n\n"
    
    for heading in headings:
        level = int(heading.name[1])  # Extract heading level from h1, h2, etc...
        markdown_outline += f"{'#' * level} {heading.get_text(strip=True)}\n\n" # '#' * level creates the correct number of # symbols

    return {"outline": markdown_outline}

# uvicorn week4_api_q3:app --host 0.0.0.0 --port 8000