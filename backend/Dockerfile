# Use official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy your FastAPI app code
COPY . .

# Expose the port (mainly for local use)
EXPOSE $PORT

# Start the FastAPI app
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
