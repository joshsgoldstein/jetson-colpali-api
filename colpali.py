import os
import logging
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from PIL import Image
import torch
from io import BytesIO
from huggingface_hub import snapshot_download


# --- CHANGED: Import from colpali_engine instead of transformers ---
from colpali_engine.models import ColPali, ColPaliProcessor
# from transformers.utils.import_utils import is_flash_attn_2_available # Optional depending on colpali usage

from dotenv import load_dotenv
load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# --- Logger ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("colpali-server")

def get_device():
    if torch.cuda.is_available():
        return "cuda:0"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

# A convenience class to wrap the functionality we will use from
# https://huggingface.co/vidore/colqwen2-v1.0
class ColPaliModel:
    def __init__(self):
        """Load the model and processor from huggingface."""
        # About a 5 GB download and similar memory usage.
        print(get_device())
        
        self.model_id = os.getenv("MODEL_ID") or "vidore/colpali-v1.3-merged" 
        local_model_path = os.getenv("LOCAL_MODEL_PATH") or "./models/colpali-v1.3-merged"
        os.makedirs(local_model_path, exist_ok=True)

        # --- Ensure model is available locally ---
        if not os.listdir(local_model_path):
            log.info(f"Downloading model to {local_model_path} ...")
            snapshot_download(
                repo_id=self.model_id,
                local_dir=local_model_path,
                local_dir_use_symlinks=False
            )
            log.info("Download complete.")
        else:
            log.info(f"Using existing local model at: {local_model_path}")

        print("Loading model + processor from disk...")
        self.model = ColPali.from_pretrained(
            local_model_path,
            torch_dtype=torch.bfloat16,
            device_map=get_device(),
            attn_implementation="eager",  # or "flash_attention_2" if available
        ).eval()
        self.processor = ColPaliProcessor.from_pretrained(local_model_path)

    # def get_device(self):
    #     return get_device()

    # A batch size of one appears to be most performant when running on an M4.
    # Note: Reducing the image resolution speeds up the vectorizer and produces
    # fewer multi-vectors.
    def multi_vectorize_image(self, img):
        """Return the multi-vector image of the supplied PIL image."""
        image_batch = self.processor.process_images([img]).to(self.model.device)
        with torch.no_grad():
            image_embedding = self.model(**image_batch)
        return image_embedding[0]

    def multi_vectorize_text(self, query):
        """Return the multi-vector embedding of the query text string."""
        query_batch = self.processor.process_queries([query]).to(self.model.device)
        with torch.no_grad():
            query_embedding = self.model(**query_batch)
        return query_embedding[0]

    def maxsim(self, query_embedding, image_embedding):
        """Compute the MaxSim between the query and image multi-vectors."""
        return self.processor.score_multi_vector(
            [query_embedding], [image_embedding]
        ).item()
    
    def get_query_embedding(self, query: str):
        """Generates multi vector embedding for a query string"""
        query_emb = self.multi_vectorize_text(query)
        return query_emb.cpu().to(dtype=torch.float32).numpy()


