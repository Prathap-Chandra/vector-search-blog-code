from flask import jsonify
from .db import QdrantDB
from dotenv import load_dotenv
import os
from PIL import Image
import io
from .config import allowed_image_extensions, collection_mapping, DIFFUSION_MODEL, file_upload_max_size
from qdrant_client.models import PointStruct
from .utils import get_text_embeddings, get_image_embeddings, prettifyVectorResultsWithLLM, get_uuid, get_pdf_chunks
from diffusers import DiffusionPipeline
import os
import torch
import json

load_dotenv()

qdrant = QdrantDB()

def generate_image_from_text(request):
    try:
        image_description = request.get_json().get('image-description')
        pipeline = DiffusionPipeline.from_pretrained(DIFFUSION_MODEL, torch_dtype=torch.float32)
        image = pipeline(image_description).images[0]
        image_unique_id = get_uuid()
        image_filename = f"{image_unique_id}.png"

        # Define the directory to save images
        image_directory = "user-generated-images"
        
        # Check if the directory exists, and if not, create it
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)

        # current_directory = os.path.dirname(os.path.abspath(__file__))
        # image_directory = os.path.join(current_directory, 'user-generated-images')
        image_path = os.path.join(image_directory, image_filename)
        absolute_image_path = os.path.abspath(image_path)

        print('absolute_image_path')
        print(absolute_image_path)
        image.save(absolute_image_path)  # Save the image
        return jsonify({
            'image_path': image_path,
            'absolute_image_path': absolute_image_path,
            'image_filename': image_filename
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

    # Convert file storage to PIL Image
    image = Image.open(io.BytesIO(file.read()))

    embeddings = get_image_embeddings(image)

    # Query Qdrant with embeddings to get top 5 results
    qdrant_response = qdrant.search(
        collection_name=collection_mapping['ImageSearchCollection'],
        vector=embeddings,
        limit=5,
        with_payload=True
    )

    if qdrant_response.status_code == 200:
        results = qdrant_response.json().get('result', [])
        formatted_results = [{
            'id': result['id'],
            'score': result['score'],  # Extracting the similarity score
            'payload': result['payload']  # Extracting the payload
        } for result in results]
    
        return jsonify({'message': 'Query successful', 'results': formatted_results}), 200
    else:
        return jsonify({'error': 'Failed to query Qdrant'}), qdrant_response.status_code

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
        print("Operation info:", operation_info)
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
        limit=6,
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
    prompt += "Question: " + prompt + "\n---\n" + "Answer: "

    formatted_results = prettifyVectorResultsWithLLM(prompt)

    return jsonify({'message': 'Query successful', 'results': formatted_results}), 200