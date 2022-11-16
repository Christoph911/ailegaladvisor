from fastapi import FastAPI, APIRouter
import sys
sys.path.append("./")
from src import search_engine

class API:

    def __init__(self) -> None:
        # init Router
        self.router = APIRouter()
        # Define route
        self.router.add_api_route("/query", self.get_pipeline, methods=["GET"] )
        # init search engine
        self.qa = SearchEngine()
        self.qa_pipeline = qa.get_qa_pipeline()
        self.document_search_pipeline = qa.get_document_search_pipeline()


    async def get_pipeline(self, user_input: str, k_retriever=10, k_reader=5):
            '''
            Classify unser-input and call specific pipeline.

            Args: 
                user_input: query provided by the user
                Retriever: top_k: number of documents/passages returned by the retriever 
                Reader: top_k: number of answers returned by the reader
                filter: query to filter results

            Returns: 
                List of dictionaries with documents or answers and metadata

            '''

            if "?" in user_input:
                results = self.qa_pipeline.run(query=user_input, params={"Retriever": {"top_k": k_retriever}, "Reader": {"top_k": k_reader}})
            else:
                results = self.document_search_pipeline.run(query=user_input, params={"Retriever": {"top_k": k_retriever}})
            return results


# Init API
app = FastAPI()
qa = SearchEngine()
app.include_router(qa.router)
