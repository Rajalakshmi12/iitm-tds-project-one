import requests
import os
import numpy as np

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "").strip().strip('"')

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
        print(data)
        return np.array(data["data"][0]["embedding"])
    
    except Exception as e:
        print(f"Error processing API response: {e}")
        return None

    
def cosine_similarity(vec1, vec2):
    if vec1 is None or vec2 is None:
        print("Error: One or both embeddings are None")
        return 0  # Return a default similarity score

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))



def find_most_similar_comments(path):
    
    # Define paths
    COMMENTS_FILE = "/data/comments.txt"
    OUTPUT_FILE = "/data/comments-similar.txt"

    # Read all comments
    with open(COMMENTS_FILE, "r", encoding="utf-8") as file:
        comments = [line.strip() for line in file.readlines() if line.strip()]

    if len(comments) < 2:
        print("Error: Not enough comments to compare.")

    # Generate embeddings for all comments
    embeddings = {comment: get_embedding(comment) for comment in comments}
    #print(embeddings)
    
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
        print(f"Most similar comments saved to {OUTPUT_FILE}")
    
    
find_most_similar_comments("/data/comments.txt")