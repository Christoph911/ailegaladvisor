# -----------------------------------------------------------
# Configure DataBase (Document Store) communication for the 
# AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import json
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.preprocessor import PreProcessor

# TODO: Implement final preprocessing Pipeline and split in seperate file

class Preprocessing:
    '''
    Class load and preprocess the raw data

    '''
    DATAPATH = 'PATH TO DATAFILE OR DATABASE'


    def load_data(self):
        '''
        Open and load JSON-file to python dictionary

        Returns: 
            dictionary with json-data

        '''
        json_file = open(self.DATAPATH, encoding="utf8")
        data_dict = json.load(json_file)

        return data_dict

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




class DocumentStore:
    '''
    Class ensures the database(document store) communication
    and stores different methods for database operations

    '''

    def __init__(self):
        self.document_store = self.init_document_store()

    def init_document_store(self):
        '''
        Init the document store and perform connection

        Returns: 
            document store
        '''
        document_store = ElasticsearchDocumentStore(
            host='hostname',
            port='port',
            scheme='https',
            username="", 
            password="", 
            index="document"
        )

        return document_store


    def count_documents(self):
        # Count all documents in specified index

        return print(self.document_store.get_document_count())

    def write_documents(self, data, batch_size=200):
        # Write all documents in batches to the document store

        self.document_store.write_documents(data, batch_size)

        return print("Successfully write documents into the document store")
    
    def update_embeddings(self, update_existing_embeddings=False):
        # Update Passage/Embeddings in document store 

        # TODO: Call DPR from class SearchEngine in file app.py

        self.document_store.update_embeddings(update_existing_embeddings)

        return print("Sucessfully updated existing passage embeddings")


    def delete_all_documents(self):
        # Delete all documents inside the specified index

        self.document_store.delete_documents()

        return print("Successfully deleted all documents in the document store")

if __name__ == "__main__":
   prep = Preprocessing()
   data = prep.load_data()
   data_clean = prep.preprocess_data(data)
   data_to_write = data_clean

   doc_store = DocumentStore()
   document_store = doc_store.init_document_store()
   doc_store.write_documents(document_store, data_to_write)
   doc_store.count_documents(document_store)
