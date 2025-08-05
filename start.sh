#!/bin/bash
set -e

# Start Ollama in the background
ollama serve &

# Wait a few seconds to ensure Ollama is ready
sleep 5

# Start FastAPI app
exec uvicorn backend.api:app --host 0.0.0.0 --port 8080
