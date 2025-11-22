# Use a Jetson-compatible base image
# NOTE: Ensure this tag matches your JetPack version (e.g., r36.2.0 for JetPack 6)
FROM dustynv/l4t-pytorch:r36.2.0

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY colpali-lib-api-jetson/requirements.txt .

# Install dependencies
# Note: existing torch in base image is usually preferred on Jetson.
# You might need to comment out the specific torch wheel in requirements.txt
# if it conflicts with the system PyTorch.
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the local library from the build context
COPY colpali-lib/colpali-jetson /tmp/colpali-jetson

# Install the local library
RUN cd /tmp/colpali-jetson && pip3 install .

# Copy the application code
COPY colpali-lib-api-jetson /app

EXPOSE 8012

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]