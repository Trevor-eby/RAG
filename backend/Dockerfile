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
COPY backend ./backend
COPY api.py .
COPY file_processing.py
COPY get_embedding_function.py
COPY query_data.py

COPY frontend ./frontend
COPY script.js
COPY style.css
COPY webfront.html

COPY ./chroma

# Expose the port (mainly for local use)
EXPOSE $PORT

# Start the FastAPI app
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
