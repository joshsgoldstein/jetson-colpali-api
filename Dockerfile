# Use Python slim base image for ARM64/Jetson compatibility
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    wget \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY requirements-jetson.txt .

# Install PyTorch wheel separately with increased timeout
RUN pip3 install --no-cache-dir --timeout=600 \
    https://pypi.jetson-ai-lab.io/jp6/cu126/+f/62a/1beee9f2f1470/torch-2.8.0-cp310-cp310-linux_aarch64.whl#sha256=62a1beee9f2f147076a974d2942c90060c12771c94740830327cae705b2595fc

# Install remaining dependencies from PyPI
RUN pip3 install --no-cache-dir --index-url https://pypi.org/simple \
    transformers>=4.53.1,<4.54.0 \
    fastapi \
    uvicorn \
    pillow \
    "numpy<2.0.0" \
    accelerate \
    python-dotenv \
    huggingface-hub \
    colpali-engine

# Copy the application code
COPY . /app

EXPOSE 8012

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]