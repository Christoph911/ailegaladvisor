# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2022 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import os
import json
import streamlit as st
import asyncio
from fastapi import FastAPI
from annotated_text import annotated_text
from search_engine import SearchEngine
from legal_ner import LegalNER
import time
import streamlit_modal as modal
import streamlit.components.v1 as components

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
        st.image(os.path.join("..", "data", "Logo_aila.png"), use_column_width='auto')
        #st.title('AI-based Legal Advisor :scales:')

        # sidebar
        st.sidebar.write("**Filter:**")
        #filter_court_name = st.sidebar.text_input("Gericht:")
        #filter_court_level_of_appeal = st.sidebar.multiselect("Status des Gericht:", ["Bundesgericht", "Landesgericht"])
        #filter_file_type = st.sidebar.multiselect("Art der Entscheidung:", ["Beschluss", "Urteil"])
        #filter_file_number = st.sidebar.text_input(label="Bezeichnung der Entscheidung:", value="VIII B 90/09")
        filter_n_retriever = st.sidebar.number_input(min_value=1, max_value=20, value=10, label="Anzahl auszugebender Passagen")
        filter_n_reader = st.sidebar.number_input(min_value=0, max_value=20, value=3, label="Anzahl extrahierter Antworten")
        #check_legal_ner = st.sidebar.checkbox("Show Legal Entities")
        open_modal = st.sidebar.button("Hilfe")

        # modal 
        if open_modal:
            modal.open()

        if modal.is_open():
            with modal.container():
                st.subheader("Stichwort-Suche:")
                st.text("Die Suche nach Passagen wird ausgel??st, wenn in der Suchleiste Stichw??rter angegeben werden.")
                st.text("Z.B. 'Losverfahren Universit??t'")
                st.subheader("Antwort-Extraktion:")
                st.text("Die Extraktion von konkreten Antworten wird ausgel??st, wenn die Eingabe in der Suchleite ein Fragezeichen ('?') enth??lt.")
                st.text("Z.B. 'Wann darf die Polizei ein Auto durchsuchen?'")
                st.text("Achtung: Der Prozess kann einige Zeit in Anspruch nehmen!")


        # searchbar
        user_input = st.text_input('Bitte geben sie einen Suchbegriff oder eine Frage ein:', value="Beispiel: Wer gilt als Halter eines KFZ?", placeholder="Zum Starten der Suche auf den Button 'Suche' klicken")
        run_query = st.button("Suche")

        # define action if search button is clicked
        if run_query:
            with st.spinner("???? &nbsp;&nbsp; F??hre semantische Suche aus...\n "
                "Dieser Prozess kann etwas Zeit in Anspruch nehmen. \n"
                "Bitte nicht abbrechen!"):
                
                # call pipeline with user input
                results = asyncio.run(qa.get_pipeline(user_input, filter_n_retriever, filter_n_reader))

                #if document-retrieval pipeline is called:
                if "answers" in results:
                    increment_button_key_answer = 0 
                    st.write("## Relevante Antworten:")
                    for result in results["answers"]:
                        # response to dict 
                        answer = result.to_dict()
                        st.write("**Relevanz:**", round(answer["score"],2)),
                        with st.expander(label=answer["meta"]["file_type"] + " | " + answer["meta"]["court_name"] + " | " + answer["meta"]["file_date"]):
                            st.write("**Titel:**", answer["meta"]["file_slug"]),
                            st.write("**Datum:**", answer["meta"]["file_date"]),
                            st.write("**Bez.:**", answer["meta"]["file_number"]),
                            st.write("**ECLI:**", answer["meta"]["file_ecli"]),
                            st.write("**Typ.:**", answer["meta"]["file_type"]),
                            st.write("**Gericht:**", answer["meta"]["court_name"]),
                            st.write("**Status Gericht:**", answer["meta"]["court_level_of_appeal"]),
                            st.markdown(self.annotate_answer(answer["answer"], answer["context"]), unsafe_allow_html=True),
                            st.markdown("""---""")
                            st.write("**War diese Antwort hilfreich?**")
                            feedback_btn_col1, feedback_btn_col2 = st.columns([1,7])
                            with feedback_btn_col1:
                                st.button("???? Ja", key=increment_button_key_answer), 
                            with feedback_btn_col2:
                                st.button("???? Nein", key=increment_button_key_answer)
                            increment_button_key_answer +=1
                            # if check_legal_ner:
                            #     st.write("**Legal Entities**")
                            #     st.write(ner.get_entities(answer["content"]), unsafe_allow_html=True)

                else:
                    increment_button_key_passage = 0 
                    st.write("## Relevante Passagen:")
                    st.markdown("""---""")
                    for result in results["documents"]:
                        document = result.to_dict()
                        st.write("**Relevanz:**", round(document["score"], 2)),
                        with st.expander(label=document["meta"]["file_type"] + " | " + document["meta"]["court_name"] + " | " + document["meta"]["file_date"]):
                            st.write("**Titel:**", document["meta"]["file_slug"]),
                            st.write("**Datum:**", document["meta"]["file_date"]),
                            st.write("**Bez.:**", document["meta"]["file_number"]),
                            st.write("**ECLI:**", document["meta"]["file_ecli"]),
                            st.write("**Typ.:**", document["meta"]["file_type"]),
                            st.write("**Gericht:**", document["meta"]["court_name"]),
                            st.write("**Gerichtbarkeit:**", document["meta"]["court_jurisdiction"]),
                            st.markdown(document["content"], unsafe_allow_html=True)
                            st.markdown("""---""")
                            st.write("**War diese Passage hilfreich?**")
                            feedback_btn_col1, feedback_btn_col2 = st.columns([1,7])
                            with feedback_btn_col1:
                                st.button("???? Ja", key=increment_button_key_passage)
                            with feedback_btn_col2:
                                st.button("???? Nein", key=increment_button_key_passage)
                            
                            increment_button_key_passage +=1
                        
                            # if check_legal_ner:
                            #     st.write("**Legal Entities**")
                            #     st.markdown(ner.get_entities(document["content"]), unsafe_allow_html=True)

                            
if __name__ == "__main__":
    # init SearchEngine
    qa = SearchEngine()
    # init legal NER
    ner = LegalNER()
    # init Streamlit
    ui = Streamlit()




