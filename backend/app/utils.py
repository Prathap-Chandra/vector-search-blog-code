import requests
import json
import os
from dotenv import load_dotenv
from transformers import ViTImageProcessor, ViTModel
from config import vision_transformer_models_config, pdf_chunk_size, VISION_TRANSFORMER_MODEL
from PIL import Image
import hashlib
import uuid
import pdfplumber
import time

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

feature_extractor = ViTImageProcessor.from_pretrained(VISION_TRANSFORMER_MODEL)
model = ViTModel.from_pretrained(VISION_TRANSFORMER_MODEL)

# Function to get unique id for an image file
def get_unique_id(image_file):
    return int(hashlib.sha256(image_file.encode('utf-8')).hexdigest(), 16) % (10 ** 8)  # Reduce to 8 digits

def get_uuid():
    return str(uuid.uuid4())

def get_pdf_chunks(file_stream):
    try:
        # read the pdf file
        pdfContent = ""
        with pdfplumber.open(file_stream) as pdf:
            # loop over all the pages
            for page in pdf.pages:
                pdfContent += page.extract_text()

        # split the pdf content into chunks
        pdfChunks = []
        while len(pdfContent) > pdf_chunk_size:
            last_period_index = pdfContent[:pdf_chunk_size].rfind('.')
            if last_period_index == -1:
                last_period_index = pdf_chunk_size
            pdfChunks.append(pdfContent[:last_period_index])
            pdfContent = pdfContent[last_period_index+1:]
        pdfChunks.append(pdfContent)

        return pdfChunks
    except Exception as e:
        raise ValueError(f"Error occurred while reading the PDF: {str(e)}")

def get_text_embeddings(text):
    url = 'https://api.openai.com/v1/embeddings'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}',
    }
    
    data = {
        'input': text,
        'model': 'text-embedding-3-small'
    }

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            embeddings = response.json()
            if 'data' in embeddings and embeddings['data']:
                return embeddings['data'][0]['embedding']
            else:
                return None
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt < max_attempts - 1:
                    wait_time = (2 ** attempt) * 10
                    print(f"Rate limit exceeded. Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    raise ValueError("Rate limit exceeded. Reached maximum retry attempts.")
            else:
                raise ValueError(f"An error occurred while fetching embeddings: {e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"An error occurred while fetching embeddings: {e}")
    
def prettifyVectorResultsWithLLM(prompt):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}',
    }

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "system",
            "content": "Given some context and a prompt/question, I want you to generate a response accordinhly. For example, Context: Christopher Nolan directed Interstellat which was released in 2014. Question: Who directed Interstellar? Answer: Christopher Nolan directed Interstellar"
        }, {
            "role": "user",
            "content": prompt
        }],
        "temperature": 1,
        "max_tokens": 256,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    })

    try:
        response = requests.post("POST", url, headers=headers, json=payload)
        response.raise_for_status()
        embeddings = response.json()
        return embeddings
    except requests.exceptions.RequestException as e:
        raise ValueError(f"An error occurred while fetching embeddings: {e}")    
    
def get_image_embeddings(image_path):
    try:
        model_dimensions = vision_transformer_models_config[VISION_TRANSFORMER_MODEL]["dimensions"]
        image = Image.open(image_path).convert("RGB")
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)

        embeddings = outputs.last_hidden_state.mean(dim=1) 
        
        if embeddings.size(1) != model_dimensions:
            raise ValueError(f"Embeddings dimension mismatch. Expected {model_dimensions}, got {embeddings.size(1)}")
        
        return embeddings.squeeze().tolist()
    except Exception as e:
        raise ValueError(f"Error occurred while extracting image embeddings: {str(e)}")