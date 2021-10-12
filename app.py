# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import streamlit as st
import spacy
import asyncio
from spacy_streamlit.visualizer import visualize
from spacy_streamlit import visualize_ner
from annotated_text import annotated_text
from db_communication import DocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.retriever.dense import DensePassageRetriever
from haystack.reader.farm import FARMReader
from haystack.pipeline import DocumentSearchPipeline, ExtractiveQAPipeline
from fastapi import FastAPI
import time


# init api
app = FastAPI()


class Streamlit:
    '''
    Class builds the Streamlit user-interface and represent
    retrieved documents to the user

    '''

    def __init__(self):
        self.build_ui()
        
   
    def annotate_answer(self, answer, context):
        '''
        Called in QA-Pipeline: 
            Gets answer and context, colors and annotate answer 

        Args: 
            answer: Answer to provided question returned by QA-Pipeline
            context: Context in which an answer is located
        
        Returns: 
            Annotated and colored answer for user-representation
        '''

        start_idx = context.find(answer)
        end_idx = start_idx + len(answer)
        text_annotated = annotated_text(context[:start_idx], (answer, "ANSWER", "#8ef"), context[end_idx:])

        return text_annotated
    

    def get_entities(self, context):
        '''
        Get context from QA and Doc-Retrieval pipeline, 
        call Spacy transformer-model and search for legal named entities

        Args: 
            context: passage or context in which an answer is located
        
        Returns: 
            DataFrame with Legal Named Entities
        '''

        nlp = spacy.load("spacy_models/model-best")
        doc = nlp(context)
        ner = visualize_ner(doc, labels=nlp.get_pipe("ner").labels)


        return ner
        
   
    def build_ui(self):
        '''
        Building the stremlit user-interface,
        get user input, call doc-retrieval or qa-pipeline
        and return represented answers 

        '''

        ### build UI ###

        # title
        st.image('data/Logo_aila.png', use_column_width='auto')
        #st.title('AI-based Legal Advisor :scales:')

        # sidebar
        st.sidebar.write("**Filter:**")
        filter_court_name = st.sidebar.text_input("Gericht:")
        filter_court_level_of_appeal = st.sidebar.multiselect("Status des Gericht:", ["Bundesgericht", "Landesgericht"])
        filter_file_type = st.sidebar.multiselect("Art der Entscheidung:", ["Beschluss", "Urteil"])
        filter_file_number = st.sidebar.text_input(label="Bezeichnung der Entscheidung:", value="VIII B 90/09")
        filter_number_retriever = st.sidebar.number_input(min_value=1, max_value=20, value=10, label="Anzahl Retriever results")
        filter_n_reader = st.sidebar.number_input(min_value=0, max_value=20, value=20, label="Anzahl Reader results")

        # searchbar
        user_input = st.text_input('Bitte geben sie einen Suchbegriff oder eine Frage ein:', value="Losverfahren Universität")
        run_query = st.button("Search")

        # define action if search button is clicked
        if run_query:
            # call pipeline with user input
            results = asyncio.run(qa.get_pipeline(user_input))
            

            # if document-retrieval pipeline is called:
            if "documents" in results: 
                st.write("## Retrieved Documents:")
                st.markdown("""---""")

                for i in range(len(results)-1):
                    st.write("**Score:**", round(results["documents"][i]["score"], 2)),
                    with st.expander(label=results["documents"][i]["meta"]["file_slug"]):
                        st.write("**Titel:**", results["documents"][i]["meta"]["file_slug"]),
                        st.write("**Datum:**", results["documents"][i]["meta"]["file_date"]),
                        st.write("**Bez.:**", results["documents"][i]["meta"]["file_number"]),
                        st.write("**Typ.:**", results["documents"][i]["meta"]["file_type"]),
                        st.write("**Gericht:**", results["documents"][i]["meta"]["court_name"]),
                        st.write("**Status Gericht:**", results["documents"][i]["meta"]["court_level_of_appeal"]),
                        st.write("**Gerichtbarkeit:**", results["documents"][i]["meta"]["court_jurisdiction"]),
                        st.write("**Score:**", round(results["documents"][i]["score"], 2)),
                        st.markdown(results["documents"][i]["text"], unsafe_allow_html=True)
                        st.write("**Legal Entities**")
                        st.write(self.get_entities(results["documents"][i]["text"]), unsafe_allow_html=True)
            else:
                st.write("## Retrieved Answers:")
                # if qa-pipeline is called:
                for i in range(len(results)-1):
                    st.write("**Score:**", round(results["answers"][i]["score"]/10, 2)),
                    with st.expander(label=results["answers"][i]["meta"]["file_slug"]):
                        st.write("**Titel:**", results["answers"][i]["meta"]["file_slug"]),
                        st.write("**Datum:**", results["answers"][i]["meta"]["file_date"]),
                        st.write("**Bez.:**", results["answers"][i]["meta"]["file_number"]),
                        st.write("**Typ.:**", results["answers"][i]["meta"]["file_type"]),
                        st.write("**Gericht:**", results["answers"][i]["meta"]["court_name"]),
                        st.write("**Status Gericht:**", results["answers"][i]["meta"]["court_level_of_appeal"]),
                        st.write("**Gerichtbarkeit:**", results["answers"][i]["meta"]["court_jurisdiction"]),
                        st.write("**Score:**", round(results["answers"][i]["score"]/10, 2)),

                        st.markdown(self.annotate_answer(results["answers"][i]["answer"], results["answers"][i]["context"]), unsafe_allow_html=True)
                    #with st.expander("Legal Entities:"):
                    #    st.write(self.get_entities(results["answers"][i]["context"]), unsafe_allow_html=True)
 

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
    

    @app.get('/query')
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
        

if __name__ == "__main__":
    # run class SearchEngine from search_engine.py
    qa = SearchEngine()
    # streamlit
    ui = Streamlit()




