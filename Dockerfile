# Use Ollama as base image
FROM ollama/ollama

# Install Python and other tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip

# Set workdir
WORKDIR /app

# Copy your code
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose Ollama's port
EXPOSE 11434

# Run Ollama in the background and then start your app
CMD ollama serve & sleep 5 && python3 backend/api.py
