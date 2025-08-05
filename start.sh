#!/bin/bash
set -e

echo "Starting FastAPI server..."
echo "Testing Ollama..."
curl http://localhost:11434/api/tags
exec uvicorn backend.api:app --host 0.0.0.0 --port 8080