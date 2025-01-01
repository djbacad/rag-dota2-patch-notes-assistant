
from src.utils.chain_builder import ChainBuilder
from src.utils.strainer import FilterRetrievedDocuments
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load chain objects:
llm_obj =  ChatOpenAI(model="gpt-4o-mini", temperature=0)
query = "What are the changes for shadow shaman in 7.37e??"
strainer_obj =  FilterRetrievedDocuments(query)
chat_history= [] 
vector_store = FAISS.load_local("./vectorstore_faiss", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)

# Initialize Chain
chain_builder = ChainBuilder(llm_obj=llm_obj, strainer_obj=strainer_obj, query=query, chat_history=chat_history, vector_store=vector_store)

# Build RAG chain
rag_chain, retrieved_docs = chain_builder.build_rag_chain()
# Print retrieved documents before invoking the chain
print("Retrieved Documents (Final Check):")
for doc in retrieved_docs:
    print(f"- {doc.page_content} [Metadata: {doc.metadata}]")
# Pass query to the chain
result = rag_chain.invoke({"input": query, "chat_history": chat_history})
print("\nAnswer:", result["answer"])