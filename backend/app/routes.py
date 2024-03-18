from flask import request
from .service import chat_with_your_pdf, upload_your_pdf, search_visually_similar_images, generate_image_from_text, send_image

def init_routes(app):

    @app.route('/conversation', methods=['POST'])
    def get_conversations():
        return chat_with_your_pdf(request)
    
    @app.route('/conversation/attachment', methods=['POST'])
    def handle_attachements_in_conversations():
        return upload_your_pdf(request)    

    @app.route('/images/similar', methods=['POST'])
    def retrieve_similar_images():
        return search_visually_similar_images(request)
    
    @app.route('/images')
    def retrieve_text_image_generated_by_text():
        image_name = request.args.get('image_name', None)
        image_type = request.args.get('image_type', None)
        return send_image(image_type, image_name)
    
    @app.route('/images/generate', methods=['POST'])
    def generate_images():
        return generate_image_from_text(request)