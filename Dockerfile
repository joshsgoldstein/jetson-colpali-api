# Use Python slim base image for ARM64/Jetson compatibility
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements-jetson.txt .

# Install Python dependencies including Jetson PyTorch wheel
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements-jetson.txt

# Copy the application code
COPY . /app

EXPOSE 8012

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]