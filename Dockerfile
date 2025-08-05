FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y curl

# Copy rest of the application code
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose FastAPI port
EXPOSE 8080

# Run app using the start.sh script
CMD ["./start.sh"]
