from flask import jsonify
from .db import QdrantDB
from dotenv import load_dotenv
import os
from PIL import Image
import io
from .config import allowed_image_extensions, collection_mapping, DIFFUSION_MODEL
import pdfplumber
from qdrant_client.models import PointStruct
from .utils import get_text_embeddings, get_image_embeddings, prettifyVectorResultsWithLLM, get_uuid, get_pdf_chunks
from diffusers import DiffusionPipeline
import os
import torch

load_dotenv()

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
    qdrant_response = QdrantDB.search(
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

    pdfChunks = get_pdf_chunks(file)
    
    points = []
    operation_info = None
    for chunk in pdfChunks:
        pointId = get_uuid()
        embeddings = get_text_embeddings(chunk)
        points.append(PointStruct(id=pointId, vector=embeddings, payload={ "content": chunk, "filename": file.filename }))
    
    operation_info = QdrantDB.insert_points(
        collection_name=collection_mapping['ImageSearchCollection'],
        wait=True,
        points=points
    )
    print("Operation info:", operation_info)

    if operation_info and 'status' in operation_info and operation_info['status'] == 'success':
        return jsonify({'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Failed to upload file'}), 500

def chat_with_your_pdf(request):
    query = request['query']
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    query_embeddings = get_text_embeddings(query)
    qdrant_response = QdrantDB.search(
        collection_name=collection_mapping['PDFChatCollection'],
        vector=query_embeddings,
        limit=2,
        with_payload=True
    )

    if qdrant_response.status_code != 200:
        return jsonify({'error': 'Failed to query Qdrant'}), qdrant_response
    
    results = qdrant_response.json().get('result', [])
    formatted_results = [{
        'id': result['id'],
        'score': result['score'],  # Extracting the similarity score
        'payload': result['payload']  # Extracting the payload
    } for result in results]

    prompt = "Context:\n"
    for result in results:
        prompt += result.payload['text'] + "\n---\n"
    prompt += "Question:" + query + "\n---\n" + "Answer:"

    # print("----PROMPT START----")
    # print(":", prompt)
    # print("----PROMPT END----")

    formatted_results = prettifyVectorResultsWithLLM(prompt)
    # print("formatted_results")
    # print(formatted_results)

    return jsonify({ 'message': 'Query successful', 'results': formatted_results }), 200