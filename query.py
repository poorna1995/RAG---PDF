from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores.pinecone import Pinecone
from embedding import get_embedding
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def query_rag(query_text: str):
    # Prepare the vectorstore.
    embedding_function = get_embedding()
    vector_store = Pinecone(index=index, embedding=embedding_function)

    # Search the vectorstore.
    results = vector_store.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
  
    # Create a prompt template.
    prompt_template = ChatPromptTemplate.from_template(TEMPLATE)
    
    # Create the prompt with the context and question.
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Instantiate the language model.
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        max_tokens=100,  # Specify max_tokens as per your requirement
        timeout=None,
        max_retries=2,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
  
    # Generate the response.
    response_text = llm.invoke(prompt)

    # Get the sources from results.
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    
    print(formatted_response)
    return response_text

def main():
    query_text = "what are the top skills"  # Replace with your query
    query_rag(query_text)

if __name__ == "__main__":
    main()
