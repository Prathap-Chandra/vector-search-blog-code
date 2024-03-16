from flask import request
from .service import chat_with_your_pdf, upload_your_pdf, search_visually_similar_images, generate_image_from_text

def init_routes(app):

    @app.route('/conversation')
    def get_conversations():
        return chat_with_your_pdf(request)
    
    @app.route('/conversation/attachment', methods=['POST'])
    def handle_attachements_in_conversations():
        return upload_your_pdf(request)    

    @app.route('/images/similar', methods=['POST'])
    def retrieve_similar_images():
        return search_visually_similar_images(request)

    @app.route('/images/generate', methods=['POST'])
    def generate_images():
        return generate_image_from_text(request)

    @app.route('/test', methods=['POST'])
    def test():
        query_params = request.args
        request_body = request.get_json()

        print('Query Params:', query_params)
        print('Request Body:', request_body)

        return 'Hello, World!'