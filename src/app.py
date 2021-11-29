# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import streamlit as st
import asyncio
from fastapi import FastAPI
from annotated_text import annotated_text
from search_engine import SearchEngine
from legal_ner import LegalNER


# TODO: Implement FastAPI
# init api
#app = FastAPI()


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
        
   
    def build_ui(self):
        '''
        Building the stremlit user-interface,
        get user input, call doc-retrieval or qa-pipeline
        and return represented answers 

        '''

        ### build UI ###

        # title
        st.image('../data/Logo_aila.png', use_column_width='auto')
        #st.title('AI-based Legal Advisor :scales:')

        # sidebar
        st.sidebar.write("**Filter:**")
        #filter_court_name = st.sidebar.text_input("Gericht:")
        #filter_court_level_of_appeal = st.sidebar.multiselect("Status des Gericht:", ["Bundesgericht", "Landesgericht"])
        #filter_file_type = st.sidebar.multiselect("Art der Entscheidung:", ["Beschluss", "Urteil"])
        #filter_file_number = st.sidebar.text_input(label="Bezeichnung der Entscheidung:", value="VIII B 90/09")
        filter_number_retriever = st.sidebar.number_input(min_value=1, max_value=20, value=10, label="Number Retriever results")
        filter_n_reader = st.sidebar.number_input(min_value=0, max_value=20, value=3, label="Number Reader results")
        check_legal_ner = st.sidebar.checkbox("Show Legal Entities")

        # searchbar
        user_input = st.text_input('Bitte geben sie einen Suchbegriff oder eine Frage ein:', value="Losverfahren Universität")
        run_query = st.button("Search")

        # define action if search button is clicked
        if run_query:
            # call pipeline with user input
            results = asyncio.run(qa.get_pipeline(user_input, filter_number_retriever, filter_n_reader))
            

            # if document-retrieval pipeline is called:
            if "documents" in results: 
                st.write("## Retrieved Documents:")
                st.markdown("""---""")
                for result in results["documents"]:
                    st.write("**Score:**", round(result["score"], 2)),
                    with st.expander(label=result["meta"]["file_slug"]):
                        st.write("**Titel:**", result["meta"]["file_slug"]),
                        st.write("**Datum:**", result["meta"]["file_date"]),
                        st.write("**Bez.:**", result["meta"]["file_number"]),
                        st.write("**Typ.:**", result["meta"]["file_type"]),
                        st.write("**Gericht:**", result["meta"]["court_name"]),
                        st.write("**Status Gericht:**", result["meta"]["court_level_of_appeal"]),
                        st.write("**Gerichtbarkeit:**", result["meta"]["court_jurisdiction"]),
                        st.write("**Score:**", round(result["score"], 2)),
                        st.markdown(result["text"], unsafe_allow_html=True)
                        if check_legal_ner:
                            st.write("**Legal Entities**")
                            st.write(ner.get_entities(result["text"]), unsafe_allow_html=True)
                    
            else:
                st.write("## Retrieved Answers:")
                for result in results["answers"]:
                    st.write("**Score:**", round(result["score"]/10, 2)),
                    with st.expander(label=result["meta"]["file_slug"]):
                        st.write("**Titel:**", result["meta"]["file_slug"]),
                        st.write("**Datum:**", result["meta"]["file_date"]),
                        st.write("**Bez.:**", result["meta"]["file_number"]),
                        st.write("**Typ.:**", result["meta"]["file_type"]),
                        st.write("**Gericht:**", result["meta"]["court_name"]),
                        st.write("**Status Gericht:**", result["meta"]["court_level_of_appeal"]),
                        st.write("**Gerichtbarkeit:**", result["meta"]["court_jurisdiction"]),
                        st.write("**Score:**", round(result["score"]/10, 2)),
                        st.markdown(self.annotate_answer(result["answer"], result["context"]), unsafe_allow_html=True)
                        if check_legal_ner:
                            st.write("**Legal Entities**")
                            st.write(ner.get_entities(result["text"]), unsafe_allow_html=True)

        

if __name__ == "__main__":
    # init SearchEngine
    qa = SearchEngine()
    # init legal NER
    ner = LegalNER()
    # init Streamlit
    ui = Streamlit()




