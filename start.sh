#!/bin/bash

# Load variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Validate that required variables are set
if [ -z "$REMOTE_USER" ] || [ -z "$REMOTE_HOST" ]; then
    echo "REMOTE_USER or REMOTE_HOST not set. Exiting."
    exit 1
fi

# Start SSH tunnel to Ollama
echo "Creating SSH tunnel to $REMOTE_USER@$REMOTE_HOST..."
ssh -o StrictHostKeyChecking=no -N -L 11434:localhost:11434 $REMOTE_USER@$REMOTE_HOST &

# Wait for the tunnel to be ready
sleep 2

# Start FastAPI
uvicorn backend.api:app --host 0.0.0.0 --port $PORT
