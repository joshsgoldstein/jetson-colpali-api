# jetson-colpali-api

A FastAPI-based REST API for ColPali vision-language model embeddings, optimized for NVIDIA Jetson devices.

## Quick Start

### Using Docker (Recommended)

Build and run with Docker:
```bash
make build
make run
```

Or manually:
```bash
docker build -t joshsgoldstein/jetson-colpali-api .
docker run -d --runtime nvidia -p 8012:8012 -v $(pwd)/models:/app/models joshsgoldstein/jetson-colpali-api
```

### Local Development on Jetson

Install dependencies:
```bash
make dev-install
```

Download the model:
```bash
make download-model
```

Run the API:
```bash
make dev-run
```

## API Endpoints

- `POST /embed` - Generate embeddings for text and/or images
- `POST /embed_batch` - Batch process multiple images

## Requirements

- NVIDIA Jetson device (tested on AGX Orin with JetPack 6)
- Docker with NVIDIA runtime
- Python 3.10+ (for local development)

## Available Make Commands

Run `make help` to see all available commands.