# FastAPI for the Colpali Library on NVIDIA Jetson Jetpack 6


Step 1: Clone the Colpali Library Repo
```
git clone https://github.com/vidore/colpali-lib.git
```

Change the `pyproject.toml` file to use the Jetson-compatible PyTorch wheel.

```
dependencies = [
    "numpy",
    "peft>=0.14.0,<0.18.0",
    "pillow>=10.0.0",
    "requests",
    "scipy",
    "torch @ https://pypi.jetson-ai-lab.io/jp6/cu126/+f/62a/1beee9f2f1470/torch-2.8.0-cp310-cp310-linux_aarch64.whl#sha256=62a1beee9f2f147076a974d2942c90060c12771c94740830327cae705b2595fc",
    "torchvision",
    "transformers>=4.53.1,<4.58.0",
]

[tool.hatch.metadata]
allow-direct-references = true
```

Step 2: Build the Docker Image at the top level above both folders

This is so you can temporarily copy over colpali-lib to the build context.

```
docker build -t joshsgoldstein/colpali-lib-api-jetson -f colpali-lib-api-jetson/Dockerfile .
```

Step 3: Run the Docker Container
```
docker run -p 8012:8012 joshsgoldstein/jetson-colpali-api
```