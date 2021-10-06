# -----------------------------------------------------------
# Configure DataBase (Document Store) communication for the 
# AI-based Document Retrieval and QA-System
# V 0.1
# (C) 2021 Christoph Hoppe, Germany
# Released under GNU Public License (GPL)
# -----------------------------------------------------------

import data_preprocessing
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore

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
            port=443,
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
    prep = data_preprocessing.Preprocessing()
    json_file = prep.load_json_long()
    data_dictionary = prep.load_json_long(json_file)
    data_preprocessed = prep.preprocess_data(data_dictionary)
    data_to_write = data_preprocessed

    doc_store = DocumentStore()
    document_store = doc_store.init_document_store()
    doc_store.write_documents(document_store, data_to_write)
    doc_store.count_documents(document_store)
