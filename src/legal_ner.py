# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import streamlit as st
import spacy
from spacy_streamlit import visualize_ner


class LegalNER:
    '''
    Class performs legal NER on the search results. 
    '''
    

    def get_entities(self, context):
        '''
        Get context from QA and Doc-Retrieval pipeline, 
        call Spacy transformer-model and search for legal named entities

        Args: 
            context: passage or context in which an answer is located
        
        Returns: 
            DataFrame with Legal Named Entities
        '''

        nlp = spacy.load(st.secrets.paths.ner_model)
        doc = nlp(context)
        ner = visualize_ner(doc, labels=nlp.get_pipe("ner").labels)


        return ner