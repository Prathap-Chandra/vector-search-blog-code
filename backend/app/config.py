# VISION_TRANSFORMER_MODELS_CONFIG
vision_transformer_models_config = {
    "facebook/dino-vits16": {
        "dimensions": 384
    },
    "google/vit-base-patch16-224-in21k": {
        "dimensions": 768,
    }
}

DIFFUSION_MODEL = "segmind/tiny-sd"

VISION_TRANSFORMER_MODEL = "facebook/dino-vits16"

OPENAI_TEXT_EMBEDDING_DIMENSIONS = 1536

# For PDF Chat collection using open ai dimensions since we will be using openai endpoint to create embeddings
collection_mapping = {
    "PDFChatCollection": "pdf-chat",
    "ImageSearchCollection": "image-search",
}

max_top_query_results = 5

pdf_chunk_size = 500

allowed_image_extensions = ['png', 'jpg', 'jpeg']