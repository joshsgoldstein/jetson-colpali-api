import os
import logging
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image
import torch
from io import BytesIO
from huggingface_hub import snapshot_download

from colpali import ColPaliModel
# --- CHANGED: Import from colpali_engine instead of transformers ---

# from transformers.utils.import_utils import is_flash_attn_2_available # Optional depending on colpali usage

from dotenv import load_dotenv
load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# # --- Logger ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("colpali-server")

# # --- Settings ---
# # CHANGED: Model ID for ColPali
# model_id = os.getenv("MODEL_ID") or "vidore/colpali-v1.3-merged" 
# local_model_path = os.getenv("LOCAL_MODEL_PATH") or "./models/colpali-v1.3-merged"
# os.makedirs(local_model_path, exist_ok=True)

# # --- Ensure model is available locally ---
# if not os.listdir(local_model_path):
#     log.info(f"Downloading model to {local_model_path} ...")
#     snapshot_download(
#         repo_id=model_id,
#         local_dir=local_model_path,
#         local_dir_use_symlinks=False
#     )
#     log.info("Download complete.")
# else:
#     log.info(f"Using existing local model at: {local_model_path}")

# # --- Load model + processor ---
# log.info("Loading model + processor from disk...")
# device = get_device()

# # CHANGED: Instantiate ColPali


# model = ColPali.from_pretrained(
#     local_model_path,
#     torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
#     device_map=device(),
#     attn_implementation="eager"  # if is_flash_attn_2_available() else "eager", # Optional
# ).eval()


# # ColQwen2.from_pretrained(
# #             "vidore/colqwen2-v1.0",
# #             torch_dtype=torch.bfloat16,
# #             device_map=get_device(),  # or "cuda:0" if using a NVIDIA GPU
# #             attn_implementation="eager",  # or "flash_attention_2" if available
# #         ).eval()

# processor = ColPaliProcessor.from_pretrained(local_model_path)


model = ColPaliModel()

# log.info(f"Model loaded on {model.get_device()}.")

# --- Helper Functions ---

# def run_inference_images(images: List[Image.Image]):
#     """
#     Process a list of images using the ColPali processor's specialized image method.
#     Returns a list of embeddings (lists of vectors).
#     """
#     # Use process_images from ColPaliProcessor
#     # Note: Expected to return a BatchFeature or similar that works with model(**...)
#     inputs = processor.process_images(images).to(model.device)
    
#     with torch.no_grad():
#         outputs = model(**inputs)
#         # Handle potential different output structures
#         val = outputs.embeddings if hasattr(outputs, "embeddings") else outputs
        
#         return val.detach().cpu().float().numpy().tolist()

# def run_inference_queries(texts: List[str]):
#     """
#     Process a list of text queries using the ColPali processor's specialized query method.
#     Returns a list of embeddings (lists of vectors).
#     """
#     # Use process_queries from ColPaliProcessor
#     inputs = processor.process_queries(texts).to(model.device)
    
#     with torch.no_grad():
#         outputs = model(**inputs)
#         val = outputs.embeddings if hasattr(outputs, "embeddings") else outputs
        
#         return val.detach().cpu().float().numpy().tolist()


app = FastAPI()

# ================================
#   FLEXIBLE (TEXT / IMAGE / BOTH)
#   MULTI-VECTOR OUTPUT
# ================================
@app.post("/embed")
async def embed(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    if file is None and text is None:
        raise HTTPException(status_code=400, detail="Provide at least one of 'file' or 'text'.")

    embeddings = []
    
    # 1. Handle Image
    if file is not None:
        log.info(f"Received file: {file.filename}")
        img_bytes = await file.read()
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        
        # Generate embedding for image
        # run_inference_images expects a list and returns a list of results
        emb_batch = model.multi_vectorize_image(img)
        
        # Since we sent 1 image, we take the first result (which is a list of vectors)
        # We can just append to our results list
        embeddings.extend(emb_batch)

    # 2. Handle Text
    if text is not None:
        log.info(f"Received text query (len={len(text)})")
        
        # Generate embedding for text
        embedding = model.get_query_embedding(text).tolist()
        print(embedding)
    
    return {
        "object": "list",
        "data": {
            "object": "embedding",
            "index": 0,
            "embedding": embedding,
        },
        "model": model.model_id,
    }


# ================================
#        BATCH IMAGES ONLY
#        MULTI-VECTOR OUTPUT
# ================================
@app.post("/embed_batch")
async def embed_batch(files: List[UploadFile] = File(...)):
    imgs = []
    names = []

    for f in files:
        names.append(f.filename)
        img_bytes = await f.read()
        imgs.append(Image.open(BytesIO(img_bytes)).convert("RGB"))

    # Use the helper function for images
    embeddings = run_inference_images(imgs)

    if embeddings:
        num_vecs = len(embeddings[0])
        dim = len(embeddings[0][0]) if num_vecs > 0 else 0
        log.info(
            f"Batch embeddings generated (batch={len(embeddings)}, "
            f"num_vectors_per_item={num_vecs}, dim={dim})"
        )

    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": i,
                "file_name": names[i],
                "embedding": embeddings[i], 
            }
            for i in range(len(embeddings))
        ],
        "model": model_id,
    }
