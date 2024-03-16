from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from qdrant_client.http.exceptions import ResponseHandlingException
from config import max_top_query_results

class QdrantDB:
    def __init__(self):
        self.client = QdrantClient(host="localhost", port=6333)
    
    def insert_points(self, collection_name, points):
        try:
            self.client.upsert(collection_name=collection_name, points=points, wait=True)
        except ResponseHandlingException as e:
            raise ResponseHandlingException(f"Error occurred during upsert: {e}")
    
    def search(self, collection_name, query_vector, limit=max_top_query_results, **kwargs):
        query_params = ['score_threshold', 'with_vectors', 'with_payload', 'search_params', 'query_filter']
        filtered_kwargs = {key: value for key, value in kwargs.items() if key in query_params}
        try:
            return self.client.search(collection_name=collection_name, query_vector=query_vector, limit=limit, **filtered_kwargs)
        except ResponseHandlingException as e:
            raise ResponseHandlingException(f"Error occurred during search: {e}")
    
    def create_collection(self, collection_name, dimension):
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )
        except ResponseHandlingException as e:
            raise ResponseHandlingException(f"Error occurred during collection creation: {e}")
