from haystack.document_store.elasticsearch import OpenSearchDocumentStore
import json
from haystack.preprocessor import PreProcessor



class Preprocessing:
    DATAPATH = r'C:\Users\Chris\Python_Projects\legalAdvisorWebapp\data\cases_test_with_html_all.json'


    def load_data(self):
        a = open(self.DATAPATH, encoding="utf8")
        jsondata = json.load(a)

        return jsondata[0:1001]

    def preprocess_data(self, data):

        preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=False,
            split_by='word',
            split_length=100,
            split_overlap=2,
            split_respect_sentence_boundary=False
        )

        nested_docs = [preprocessor.process(d) for d in data]
        data_clean = [d for x in nested_docs for d in x]
        print(f"n_files_input: {len(data)}\nn_docs_output: {len(data_clean)}")
        print(data_clean[0])

        return data_clean


# TODO: Implement preprocessing Pipeline

class DocumentStore:

    def init_document_store(self):
        document_store = OpenSearchDocumentStore(
            host='search-legaladvisor-im5qzgka52dnlybybg27eiy34y.us-east-2.es.amazonaws.com',
            port=443,
            scheme='https',
            username='legaladvisor',
            password='i6@@Stx2U2waYh',
            embedding_field=None
        )

        return document_store

# just update new embeddings
#update_embeddings(update_existing_embeddings=False')

    def count_documents(self, document_store):
        return print(document_store.get_document_count())

    def write_documents(self, document_store, data, batch_size=200):

        document_store.write_documents(data, batch_size)

        return print("Sucessfull write documents")

    def delete_all_documents(self, document_store):
        document_store.delete_documents()
        return print("Sucessfull deleted all documents")

#if __name__ == "__main__":
#    prep = Preprocessing()
#    data = prep.load_data()
#    data_clean = prep.preprocess_data(data)
#    data_to_write = data_clean
#
#    doc_store = DocumentStore()
#    document_store = doc_store.init_document_store()
#    doc_store.write_documents(document_store, data_to_write)
#    doc_store.count_documents(document_store)
