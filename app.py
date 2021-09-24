from spacy_streamlit.visualizer import visualize
import streamlit as st
from annotated_text import annotated_text
from db_communication import DocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.retriever.dense import DensePassageRetriever
from haystack.reader.farm import FARMReader
from haystack.pipeline import DocumentSearchPipeline, ExtractiveQAPipeline
from fastapi import FastAPI
import asyncio
import spacy
from spacy_streamlit import visualize_ner

# init api
app = FastAPI()


class Streamlit:

    def __init__(self):
        self.build_ui()
        
   
    def annotate_answer(self, answer, context):
        start_idx = context.find(answer)
        end_idx = start_idx + len(answer)
        text_annotated = annotated_text(context[:start_idx], (answer, "ANSWER", "#8ef"), context[end_idx:])

        return text_annotated
    

    def get_entities(self, context):
        nlp = spacy.load("spacy_models/model-best")
        doc = nlp(context)
        ner = visualize_ner(doc, labels=nlp.get_pipe("ner").labels)


        return ner 
        
   
    def build_ui(self):

        ### build UI ###
        # title
        st.title('AI-based Legal Advisor :scales:')
        # sidebar
        st.sidebar.write("**Filter:**")
        filter_court_name = st.sidebar.text_input("Gericht:")
        filter_court_level_of_appeal = st.sidebar.multiselect("Status des Gericht:", ["Bundesgericht", "Landesgericht"])
        filter_file_type = st.sidebar.multiselect("Art der Entscheidung:", ["Beschluss", "Urteil"])
        filter_file_number = st.sidebar.text_input(label="Bezeichnung der Entscheidung:", value="VIII B 90/09")
        # st.sidebar.write("**Retrieval Config:**")

        filter_number_retriever = st.sidebar.number_input(min_value=1, max_value=20, value=10, label="Anzahl Retriever results")
        filter_n_reader = st.sidebar.number_input(min_value=0, max_value=20, value=20, label="Anzahl Reader results")

        # searchbar
        st.subheader("Input")
        user_input = st.text_input('Bitte geben sie einen Suchbegriff oder eine Frage ein:', value="BGH Urteil Kläger")
        run_query = st.button("Search")

        if run_query:

            results = asyncio.run(qa.get_pipeline(user_input))

            st.write("## Answers:")
            
            if "documents" in results: 

                for i in range(len(results)-1):
                    st.write("**Titel:**", results["documents"][i]["meta"]["file_slug"]),
                    st.write("**Datum:**", results["documents"][i]["meta"]["file_date"]),
                    st.write("**Bez.:**", results["documents"][i]["meta"]["file_number"]),
                    st.write("**Typ.:**", results["documents"][i]["meta"]["file_type"]),
                    st.write("**Gericht:**", results["documents"][i]["meta"]["court_name"]),
                    st.write("**Status Gericht:**", results["documents"][i]["meta"]["court_level_of_appeal"]),
                    st.write("**Gerichtbarkeit:**", results["documents"][i]["meta"]["court_jurisdiction"]),
                    st.write("**Score:**", round(results["documents"][i]["score"], 2)),

                    st.write("**Text:**"),
                    st.markdown(results["documents"][i]["text"], unsafe_allow_html=True)
                    st.write("**Entities:**")
                    st.write(self.get_entities(results["documents"][i]["text"]), unsafe_allow_html=True)
                    st.markdown("""---""")
            else:

                for i in range(len(results)-1):
                    st.write("**Titel:**", results["answers"][i]["meta"]["file_slug"]),
                    st.write("**Datum:**", results["answers"][i]["meta"]["file_date"]),
                    st.write("**Bez.:**", results["answers"][i]["meta"]["file_number"]),
                    st.write("**Typ.:**", results["answers"][i]["meta"]["file_type"]),
                    st.write("**Gericht:**", results["answers"][i]["meta"]["court_name"]),
                    st.write("**Status Gericht:**", results["answers"][i]["meta"]["court_level_of_appeal"]),
                    st.write("**Gerichtbarkeit:**", results["answers"][i]["meta"]["court_jurisdiction"]),
                    st.write("**Score:**", round(results["answers"][i]["score"], 2)),

                    st.write("**Text:**"),
                    st.markdown(self.annotate_answer(results["answers"][i]["answer"], results["answers"][i]["context"]), unsafe_allow_html=True)
                    st.write("**Entities:**")
                    st.write(self.get_entities(results["documents"][i]["text"]), unsafe_allow_html=True)
                    st.markdown("""---""")

            
                

class SearchEngine:

    def __init__(self):
        self.document_store = DocumentStore.init_document_store(self)
        self.retriever_bm25 = ElasticsearchRetriever(document_store=self.document_store)
        self.retriever_dpr = DensePassageRetriever(document_store=self.document_store, 
                                                    query_embedding_model='deepset/gbert-base-germandpr-question_encoder', 
                                                    passage_embedding_model='deepset/gbert-base-germandpr-ctx_encoder', 
                                                    use_gpu=True, 
                                                    embed_title=True, 
                                                    use_fast_tokenizers=True)
        self.reader = FARMReader(model_name_or_path="deepset/gelectra-base-germanquad", context_window_size=300 ,use_gpu=True)
        #self.query_classifier = SklearnQueryClassifier()
        self.document_pipeline = DocumentSearchPipeline(self.retriever_bm25)
        self.qa_pipeline = ExtractiveQAPipeline(self.reader, self.retriever_dpr)
        #self.pipeline = Pipeline()
        #self.pipeline.add_node(component=self.query_classifier, name="QueryClassifier", inputs=["Query"])
        #self.pipeline.add_node(component=self.retriever_dpr, name="DPR", inputs=["QueryClassifier.output_1"])
        #self.pipeline.add_node(component=self.reader, name="QAReader", inputs=["DPR"])
        #self.pipeline.add_node(component=self.retriever_bm25, name="BM25Retriever", inputs=["QueryClassifier.output_2"])



        #self.pipeline = ExtractiveQAPipeline(self.reader, self.retriever)

    # def get_document_store(self):
    #     document_store = DocumentStore.init_document_store(self)
    #
    #     return document_store
    #
    # def get_retriever(self, document_store):
    #     retriever = ElasticsearchRetriever(document_store=document_store)
    #
    #     return retriever
    #
    # def get_pipeline(self, retriever):
    #     #TODO: Implement Query classifier
    #     return DocumentSearchPipeline(retriever)

    @app.get('/query')
    # TODO: Filter not working
    async def get_pipeline(self, user_input, n_retriever_results=10, n_reader_results=3, filter={"file_type": ["Beschluss"]}):

        if "?" in user_input:
            results = self.qa_pipeline.run(query=user_input, top_k_retriever=n_retriever_results, top_k_reader=n_reader_results, filters=filter)
        else:
            results = self.document_pipeline.run(query=user_input, top_k_retriever=n_retriever_results)
        print(results)
        return results
        

if __name__ == "__main__":
    # run class SearchEngine from search_engine.py
    qa = SearchEngine()
    # streamlit
    ui = Streamlit()




