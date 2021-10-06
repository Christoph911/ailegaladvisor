# -----------------------------------------------------------
# Preprocess legal documents for the
# AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import unicodedata
import json
from bs4 import BeautifulSoup
from haystack.preprocessor import PreProcessor

class Preprocessing:
    '''
    Class loads and preprocess the raw data

    '''

    DATAPATH = 'PATH TO DATAFILE OR DATABASE'


    def load_json_long(self):
        '''
        Load JSON-long file from openlegaldata

        Returns:
            list with jsondata
        '''

        jsondata = []
        for line in open(self.DATAPATH, 'r'):
            jsondata.append(json.loads(line))
        
        return jsondata
    

    def create_dictionary_structure(self, jsondata):
        '''
        Restructure data into a dictionary meets the requirements of the database 
        and rename keys

        Returns: 
            dictionary with specific format 
        '''
        for data in jsondata:

            meta={    
            'file_id':               data["id"],
            'file_date':             data["date"],
            'file_created_date':     data["created_date"],
            'file_ecli':             data["ecli"],
            'file_number':           data["file_number"],
            'file_slug':             data["slug"],
            'file_type':             data["type"],
            'file_updated_date':     data["updated_date"],

            "court_city":             data['court']['city'],
            "court_id" :              data['court']['id'],
            "court_name" :            data['court']['name'],
            "court_slug" :            data['court']['slug'],
            "court_state" :           data['court']['state'],
            "court_jurisdiction"    : data['court']['jurisdiction'],
            "court_level_of_appeal" : data['court']['level_of_appeal'],  
            }                      

            data["meta"] = meta
            data["text"] = data["content"]


            del data['court']
            del data['content']
            del data["date"]
            del data["created_date"]
            del data["ecli"]
            del data["file_number"]
            del data["id"]
            del data["slug"]
            del data["type"]
            del data["updated_date"]
        
        return jsondata


    def clean_html(self, data):
        '''
        Remove HTML-entities and replace \n with whitespace
        
        Returns:
            text without html
        '''
        for content in data["content"]:
            cleantext = BeautifulSoup(content, "html.parser").get_text()
            cleantext = unicodedata.normalize("NFKD", cleantext).replace('\n', ' ')
            

        return cleantext


    # def load_data(self):
    #     '''
    #     Open and load JSON-file to python dictionary

    #     Returns: 
    #         dictionary with json-data

    #     '''
    #     json_file = open(self.DATAPATH, encoding="utf8")
    #     data_dict = json.load(json_file)

    #     return data_dict


    def preprocess_data(self, data):
        '''
        Call method process from PreProcessor class 
        and perform different preprocessing methods on data

        Args:
            data: dictionary with data to preprocess

        Returns:
            preprocessed and clean dictionary with data

        '''
        preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=False,
            split_by='word',
            split_length=300,
            split_overlap=2,
            split_respect_sentence_boundary=False
        )

        nested_docs = [preprocessor.process(d) for d in data]
        data_dict_clean = [d for x in nested_docs for d in x]
        print(f"n_files_input: {len(data)}\nn_docs_output: {len(data_dict_clean)}")
        print(data_dict_clean[0])

        return data_dict_clean
    
    
if __name__ == "__main__":
   prep = Preprocessing()