from flask import jsonify, send_file
from .db import QdrantDB
from dotenv import load_dotenv
import os
from PIL import Image
import io
from .config import allowed_image_extensions, collection_mapping, DIFFUSION_MODEL, file_upload_max_size, BASE_URL
from qdrant_client.models import PointStruct
from .utils import get_text_embeddings, get_image_embeddings, prettifyVectorResultsWithLLM, get_uuid, get_pdf_chunks
from diffusers import DiffusionPipeline
import os
import torch
import json

load_dotenv()

qdrant = QdrantDB()

def send_image(image_type, image_name):
    if image_name is None:
        return jsonify({'error': 'No image name provided'}), 400
    
    if image_type is None:
        return jsonify({'error': 'No image type provided'}), 400
    
    if image_type not in ["text-based", "image-based"]:
        return jsonify({'error': 'Invalid image type. Only "text-based" or "image-based" are allowed'}), 400

    
    if image_type == "text-based": 
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "user-generated-images", image_name)
        return send_file(image_path)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(base_dir, "app", "seed_data", "images", image_name)
    return send_file(image_path)

def generate_image_from_text(request):
    try:
        image_description = request.get_json().get('image-description')
        pipeline = DiffusionPipeline.from_pretrained(DIFFUSION_MODEL, torch_dtype=torch.float32)
        image = pipeline(image_description).images[0]
        image_unique_id = get_uuid()
        image_name = f"{image_unique_id}.png"

        image_directory = "user-generated-images"        
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)

        image_path = os.path.join(image_directory, image_name)
        absolute_image_path = os.path.abspath(image_path)
        image.save(absolute_image_path)

        return jsonify({
            "image_name": image_name,
            "image_url": f"{BASE_URL}/images?image_name={image_name}&image_type=text-based",
        })
    except Exception as e:
        return jsonify({'Error generating an image': str(e)}), 500

def search_visually_similar_images(request):
    # Validate if the request has the file part and the file is of allowed type
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file.filename.split('.')[-1] not in allowed_image_extensions:
        return jsonify({'error': 'Invalid file type. Only .png, .jpg, .jpeg files are allowed'}), 400

    try:
        image_embeddings = get_image_embeddings(file)

        qdrant_response = qdrant.search(
            collection_name=collection_mapping['ImageSearchCollection'],
            query_vector=image_embeddings,
            limit=5,
            with_payload=True
        )
        
        formatted_results = []
        for record in qdrant_response:
            response = json.loads(record.model_dump_json())
            image_url = f"{BASE_URL}/images?image_name={response['payload']['image_name']}&image_type=image-based"
            formatted_result = {
                "image_url": image_url,
                "image_name": response['payload']['image_name'],
            }
            formatted_results.append(formatted_result)
        return jsonify({'message': 'Query successful', 'results': formatted_results}), 200
    except Exception as e:
        return jsonify({'error': f"Error occurred while processing image: {str(e)}"}), 500

def upload_your_pdf(request):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file.filename.split('.')[-1] != 'pdf':
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    if len(file.read()) > file_upload_max_size:
        return jsonify({'error': 'File size exceeds 2 MB limit'}), 400

    try:
        pdfChunks = get_pdf_chunks(file)
        
        points = []
        operation_info = None
        for chunk in pdfChunks:
            embeddings = get_text_embeddings(chunk)
            if embeddings is None:
                raise ValueError(f"Embeddings extraction failed for pdf: {file.filename}. Skipping to the next pdf.")
            
            pointId = get_uuid()
            points.append(PointStruct(id=pointId, vector=embeddings, payload={ "content": chunk, "pdf_name": file.filename }))
        
        operation_info = qdrant.insert_points(
            collection_name=collection_mapping['PDFChatCollection'],
            points=points
        )
    except Exception as e:
        return jsonify({'error': f"Error occurred while processing PDF: {str(e)}"}), 500

    if operation_info and 'status' in operation_info and operation_info['status'] == 'success':
        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Failed to upload file'}), 500

def chat_with_your_pdf(request):
    query = request.get_json().get('query')
    if not query:
        return jsonify({'error': 'query is required'}), 400
    
    query_embeddings = get_text_embeddings(query)
    if query_embeddings is None:
        raise ValueError(f"Embeddings extraction failed for query: {query}.")
    
    qdrant_response = qdrant.search(
        collection_name=collection_mapping['PDFChatCollection'],
        query_vector=query_embeddings,
        limit=5,
        with_payload=True
    )
    
    formatted_results = []
    for record in qdrant_response:
        response = json.loads(record.json())
        formatted_result = {
            'id': response['id'],
            'score': response['score'],
            'payload': response['payload']
        }
        formatted_results.append(formatted_result)

    prompt = "Context:\n"
    for result in formatted_results:
        prompt += result['payload']['content'] + "\n---\n"
    prompt += "Question: " + query + "\n---\n" + "Answer: "

    answer = prettifyVectorResultsWithLLM(prompt)

    return jsonify({'message': 'Query successful', 'answer': answer}), 200