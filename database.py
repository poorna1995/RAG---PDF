import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.document_loaders import PyPDFLoader
from embedding import get_embedding
from langchain_pinecone import PineconeVectorStore
from langchain.vectorstores.pinecone import Pinecone
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv


load_dotenv()
PINECONE_PATH = "pinecone"
DATA_PATH = "./data/resume_poorna_praneesha.pdf"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")





def pinecone_index():
    index_name = "langchain-rag"  # change if desired

    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    index = pc.Index(index_name)
    return index



def main():
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_pinecone(chunks)
    index =pinecone_index()


def load_documents():
    loader = PyPDFLoader()
    docs = loader.load()
    return docs

def split_documents(documents):
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size =300,
      chunk_overlap = 80,
      length_function = len,
      is_separator_regex= False,
  )
  return text_splitter.split_documents(documents)


def add_to_pinecone():
    vector_store = PineconeVectorStore(index=index, embedding=get_embedding())
    
    chunks_with_ids = calculate_chunk_ids(chunks)
    
    
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("No new documents to add")
    
 
 def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks
    
    
    
    
if __name__ == "__main__":
    main()