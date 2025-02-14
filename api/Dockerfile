#This file may not be used

# Use an official Python base image
FROM python:3.9-slim 
#Layer1

# Set the working directory
WORKDIR /app
#Layer2

# Copy the current directory contents into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files
COPY . .
# Expose port 8000
EXPOSE 8000

# Define the entrypoint
CMD ["uvicorn", "project_api:app", "--host", "0.0.0.0", "--port", "8000"]
