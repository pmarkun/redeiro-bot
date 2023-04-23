from haystack.document_stores import InMemoryDocumentStore
from haystack.utils import convert_files_to_docs
from haystack.nodes import TfidfRetriever

# Set up the document store
document_store = InMemoryDocumentStore()

def index_documents_from_folder(folder_path: str):
    # Read text files from the folder and convert them to dictionaries
    documents = convert_files_to_docs(dir_path=folder_path, clean_func=None, split_paragraphs=True)
    
    # Index the documents in the document store
    document_store.write_documents(documents)

def get_memory_snippets(query: str, top_n: int):
    # Set up the retriever
    retriever = TfidfRetriever(document_store)
    
    # Retrieve top_n documents
    retrieved_docs = retriever.retrieve(query, top_k=top_n)

    # Extract text snippets from the retrieved documents
    memory_snippets = [doc.content for doc in retrieved_docs]
    return memory_snippets
