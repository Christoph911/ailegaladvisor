# -----------------------------------------------------------
# Prototype of AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2022 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import os 
import spacy
import re
from bs4 import BeautifulSoup

# dictionary to color entities found
ENTITY_COLORS = ({ "GS":   "#00A5E3", 
            "GRT":  "#8DD7BF", 
            "MRK":  "#FF96C5",
            "VO":   "#FF5768",
            "RS":   "#FFBF65", 
            "LIT":  "#FC6238",
            "INN":  "#FFD872",
            "UN":   "#F2D4CC",
            "VS":   "#E77577",
            "PER":  "#6C88C4",
            "LD":   "#C05780",

            })


class LegalNER:
    '''
    Class performs legal NER on the search results. 
    '''
    def __init__(self) -> None:
        self.ner_model = spacy.load(os.path.join("..", "models", "Legal-NER"))

    

    def get_entities(self, context):
        '''
        Get context from QA and Doc-Retrieval pipeline, 
        call Spacy transformer-model, remove html tags and search for legal named entities

        Args: 
            context: passage or context in which an answer is located
        
        Returns: 
            DataFrame with Legal Named Entities
        '''

        cleantext = BeautifulSoup(context, "lxml").get_text("\n", strip=True)
        doc = self.ner_model(cleantext)
        params = {"text": doc.text,
          "ents": [{"start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_,
                    "kb_id": "[Link]",
                    "kb_url": f"https://www.google.de/search?q={ent.text}"}
                   for ent in doc.ents],
          "title": None}
        
        options = {"colors": ENTITY_COLORS}


        ner = spacy.displacy.render(params, style="ent", manual=True, options=options, page=True, jupyter=False)

        return ner