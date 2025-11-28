# Use a Jetson-compatible base image
# NOTE: Ensure this tag matches your JetPack version (e.g., r36.2.0 for JetPack 6)
FROM nvcr.io/nvidia/l4t-jetpack:r36.4.0

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies INCLUDING Python and numeric libs
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    libopenblas-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install the colpali library FIRST
COPY colpali-lib/colpali-jetson /tmp/colpali-jetson
RUN cd /tmp/colpali-jetson && pip3 install .

# Copy requirements SECOND (this will downgrade numpy to <2.0.0)
COPY colpali-lib-api-jetson/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY colpali-lib-api-jetson/app.py /app/app.py
COPY colpali-lib-api-jetson/colpali.py /app/colpali.py
COPY colpali-lib-api-jetson/models /app/models


EXPOSE 8012

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]
