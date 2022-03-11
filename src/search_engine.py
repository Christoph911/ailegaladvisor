# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import streamlit as st
from db_communication import DocumentStore
from haystack.nodes.retriever import ElasticsearchRetriever, DensePassageRetriever
from haystack.nodes.reader import FARMReader
from haystack.pipelines import DocumentSearchPipeline, ExtractiveQAPipeline


class SearchEngine:
    '''
    Class implements the search engine with all components

    '''

    def __init__(self):
        self.document_store = self.get_document_store()
        self.retriever_bm25 = self.get_retriever_bm25()
        self.retriever_dpr = self.get_retriever_dpr()
        self.reader = self.get_reader()
        self.document_search_pipeline = self.get_document_search_pipeline()
        self.qa_pipeline = self.get_qa_pipeline()

    @st.cache(allow_output_mutation=True)
    def get_document_store(self):
        '''
        Call init document_store from class DocumentStore

        return: connection to the document_store
        '''

        document_store = DocumentStore.init_document_store(self)
    
        return document_store
    

    def get_retriever_bm25(self):
        # Init BM25 retriever for document/passage retrieval

        retriever_bm25 = ElasticsearchRetriever(document_store=self.document_store)
    
        return retriever_bm25
    

    def get_retriever_dpr(self):
        # Init DPR retriever for document/passage retrieval

        retriever_dpr = DensePassageRetriever(document_store=self.document_store, 
                                                query_embedding_model='deepset/gbert-base-germandpr-question_encoder', 
                                                passage_embedding_model='deepset/gbert-base-germandpr-ctx_encoder', 
                                                use_gpu=True, 
                                                embed_title=True, 
                                                use_fast_tokenizers=True)

        return retriever_dpr


    def get_reader(self):
        # Init FARM-Reader-model for QA

        reader = FARMReader(model_name_or_path="deepset/gelectra-base-germanquad", 
                            context_window_size=300,
                            use_gpu=True)

        return reader


    def get_document_search_pipeline(self):
        # Init document search pipeline

        document_search_pipeline = DocumentSearchPipeline(self.retriever_bm25)

        return document_search_pipeline


    def get_qa_pipeline(self):
        # Init Question answering pipeline
        qa_pipeline = ExtractiveQAPipeline(self.reader, self.retriever_dpr)

        return qa_pipeline
    

    #@app.get('/query')
    # TODO: Filter not working
    async def get_pipeline(self, user_input, n_retriever_results=10, n_reader_results=3, filter={"file_type": ["Beschluss"]}):
        '''
        Classify unser-input and call specific pipeline.

        Args: 
            user_input: query provided by the user
            n_retriever_results: number of documents/passages returned by the retriever 
            n_reader_results: number of answers returned by the reader
            filter: query to filter results

        Returns: 
            List of dictionaries with documents or answers and metadata

        '''

        if "?" in user_input:
            results = self.qa_pipeline.run(query=user_input, top_k_retriever=n_retriever_results, top_k_reader=n_reader_results, filters=filter)
        else:
            results = self.document_search_pipeline.run(query=user_input, top_k_retriever=n_retriever_results)
        print(results)
        return results