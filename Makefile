.PHONY: help build run stop clean logs shell download-model

# Docker image name
IMAGE_NAME := joshsgoldstein/jetson-colpali-api
CONTAINER_NAME := jetson-colpali-api
PORT := 8012

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image (run from parent directory with colpali-lib)
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME) -f Dockerfile ..

build-local: ## Build the Docker image from current directory (assumes colpali-lib is accessible)
	@echo "Building Docker image from current directory..."
	docker build -t $(IMAGE_NAME) .

run: ## Run the Docker container
	@echo "Starting container..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		--runtime nvidia \
		-p $(PORT):$(PORT) \
		-v $(PWD)/models:/app/models \
		$(IMAGE_NAME)
	@echo "Container started. API available at http://localhost:$(PORT)"

run-interactive: ## Run the Docker container in interactive mode
	docker run -it --rm \
		--runtime nvidia \
		-p $(PORT):$(PORT) \
		-v $(PWD)/models:/app/models \
		$(IMAGE_NAME) /bin/bash

stop: ## Stop the running container
	@echo "Stopping container..."
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

logs: ## Show container logs
	docker logs -f $(CONTAINER_NAME)

shell: ## Open a shell in the running container
	docker exec -it $(CONTAINER_NAME) /bin/bash

download-model: ## Download the model locally
	@echo "Downloading model..."
	python3 download-model.py

clean: ## Remove containers and images
	@echo "Cleaning up..."
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi $(IMAGE_NAME) 2>/dev/null || true

clean-models: ## Remove downloaded models
	@echo "Removing models directory..."
	rm -rf models/

dev-install: ## Install dependencies for local Jetson development
	pip3 install -r requirements-jetson.txt

dev-install-docker: ## Install dependencies (for non-Jetson or inside Docker)
	pip3 install -r requirements.txt

dev-run: ## Run the API locally (not in Docker)
	uvicorn app:app --host 0.0.0.0 --port $(PORT) --reload

test-embed: ## Test the /embed endpoint with a sample request
	@echo "Testing /embed endpoint..."
	curl -X POST http://localhost:$(PORT)/embed \
		-F "text=What is machine learning?"

status: ## Show container status
	@docker ps -a | grep $(CONTAINER_NAME) || echo "Container not running"
