# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import os
from fastapi import FastAPI, APIRouter
import streamlit as st
from db_communication import DocumentStore
from haystack.nodes.retriever import ElasticsearchRetriever, EmbeddingRetriever
from haystack.nodes.reader import FARMReader
from haystack.pipelines import DocumentSearchPipeline, ExtractiveQAPipeline


class SearchEngine:
    '''
    Class implements the search engine with all components

    '''

    def __init__(self):
        # init Router
        self.router = APIRouter()
        # Define route
        self.router.add_api_route("/query", self.get_pipeline, methods=["GET"])
        self.document_store = self.get_document_store()
        self.retriever_bm25 = self.get_retriever_bm25()
        #self.retriever_emb = self.get_retriever_emb()
        self.reader = self.get_reader()
        self.document_search_pipeline = self.get_document_search_pipeline()
        self.qa_pipeline = self.get_qa_pipeline()

    #@st.cache(allow_output_mutation=True)
    @st.experimental_singleton
    def get_document_store(_self):
        '''
        Call init document_store from class DocumentStore

        return: connection to the document_store
        '''

        document_store = DocumentStore.init_document_store(_self)
        print(f"There are {document_store.get_document_count()} documents in the database")
    
        return document_store
    
    @st.experimental_singleton
    def get_retriever_bm25(_self):
        # Init BM25 retriever for document/passage retrieval

        retriever_bm25 = ElasticsearchRetriever(document_store=_self.document_store)
    
        return retriever_bm25
    
    # #TODO: Change to own emb. retriever
    # @st.experimental_singleton
    # def get_retriever_emb(_self):
    #     # Init emb retriever for document/passage retrieval

    #     retriever_emb = EmbeddingRetriever(document_store=_self.document_store,
    #                                         embedding_model=st.secrets.paths.retriever,
    #                                         )

    #     return retriever_emb

    @st.experimental_singleton
    def get_reader(_self):
        # Init FARM-Reader-model for QA

        reader = FARMReader(model_name_or_path="../models/GELECTRA-large-LegalQuAD",
                            context_window_size=300,
                            use_gpu=True)

        return reader


    def get_document_search_pipeline(self):
        # Init document search pipeline

        document_search_pipeline = DocumentSearchPipeline(self.retriever_bm25)

        return document_search_pipeline

    # TODO: Implement ensamble retriever
    def get_qa_pipeline(self):
        # Init Question answering pipeline
        qa_pipeline = ExtractiveQAPipeline(self.reader, self.retriever_bm25)

        return qa_pipeline
    

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