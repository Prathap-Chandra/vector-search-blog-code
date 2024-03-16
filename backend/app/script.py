from db import QdrantDB
from dotenv import load_dotenv
import os
from utils import get_image_embeddings, get_text_embeddings, get_pdf_chunks, get_uuid
from qdrant_client.http.models import PointStruct
from config import vision_transformer_models_config, collection_mapping, VISION_TRANSFORMER_MODEL, OPENAI_TEXT_EMBEDDING_DIMENSIONS

load_dotenv()

qdrant = QdrantDB()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

VISION_TRANSFORMER_MODEL_DIMENSIONS = vision_transformer_models_config[VISION_TRANSFORMER_MODEL]["dimensions"]

script_directory = os.path.dirname(os.path.abspath(__file__))

seed_data_path = os.path.join(script_directory, 'seed_data')

pdfs_directory = os.path.join(seed_data_path, 'pdfs')

images_directory = os.path.join(seed_data_path, 'images')

qdrant.create_collection(collection_mapping['PDFChatCollection'], OPENAI_TEXT_EMBEDDING_DIMENSIONS)

qdrant.create_collection(collection_mapping['ImageSearchCollection'], VISION_TRANSFORMER_MODEL_DIMENSIONS)

def create_image_embeddings(images_directory):
    try:
        files = os.listdir(images_directory)
        image_files = [file for file in files if file.endswith(('.jpeg', '.jpg', '.png'))]
        
        for file in image_files:
            image_name = os.path.basename(file)
            image_path = os.path.join(images_directory, file)
        
            embeddings = get_image_embeddings(image_path)
            if embeddings is None:
                raise ValueError(f"Embeddings extraction failed for image: {image_name}. Skipping to the next image.")
            point_id = get_uuid() 
            if isinstance(embeddings, list) and all(isinstance(item, float) for item in embeddings):
                points = [
                    PointStruct(id=point_id, vector=embeddings, payload={"image_path": image_path, "image_name": image_name})
                ]
                operation_info = qdrant.insert_points(collection_name=collection_mapping["ImageSearchCollection"], points=points)
                print(operation_info)
            else:
                raise ValueError(f"Embeddings format error for image: {image_name}. Expected a list of floats.")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error occurred while reading the image directory: {str(e)}")

def create_pdf_embeddings(pdfs_directory):
    try:
        files = os.listdir(pdfs_directory)
        pdf_files = [file for file in files if file.endswith(('.pdf'))]
        for pdf in pdf_files:
            pdf_name = os.path.basename(pdf)
            pdf_path = os.path.join(pdfs_directory, pdf)

            pdfChunks = get_pdf_chunks(pdf_path)
            for chunk in pdfChunks:
                embeddings = get_text_embeddings(chunk)
                if embeddings is None:
                    raise ValueError(f"Embeddings extraction failed for pdf: {pdf_name}. Skipping to the next pdf.")
                
                point_id = get_uuid() 
                if isinstance(embeddings, list) and all(isinstance(item, float) for item in embeddings):
                    points = [
                        PointStruct(id=point_id, vector=embeddings, payload={ "content": chunk, "pdf_name": pdf_name })
                    ]
                    operation_info = qdrant.insert_points(collection_name=collection_mapping['PDFChatCollection'], points=points)
                    print(operation_info)
                else:
                    raise ValueError(f"Embeddings format error for pdf: {pdf_name}. Expected a list of floats.")
                    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error occurred while reading the pdf directory: {str(e)}")    

create_image_embeddings(images_directory=images_directory)

create_pdf_embeddings(pdfs_directory=pdfs_directory)