
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

def get_embedding():
  embeddings = HuggingFaceEmbeddings(
      model_name="sentence-transformers/all-mpnet-base-v2")
  return embedding
