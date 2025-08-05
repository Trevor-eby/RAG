# Start from Ubuntu base
FROM ubuntu:22.04

# Prevent prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Set up working directory
WORKDIR /app

# Copy your code
COPY . .

# Install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Download your model (e.g., gemma3)
RUN ollama pull gemma:latest

# Expose the port
EXPOSE 8080

# Entrypoint
CMD ["./start.sh"]
