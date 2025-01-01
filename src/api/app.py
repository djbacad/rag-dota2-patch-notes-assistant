
# from src.utils.chain_builder import ChainBuilder
# from src.utils.strainer import FilterRetrievedDocuments
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS

# # Load chain objects:
# llm_obj =  ChatOpenAI(model="gpt-4o-mini", temperature=0)
# query = "What are the changes for sand king in 7.37d if there's any?"
# strainer_obj =  FilterRetrievedDocuments(query)
# chat_history= [] 
# vector_store = FAISS.load_local("./vectorstore_faiss", embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)

# # Initialize Chain
# chain_builder = ChainBuilder(llm_obj=llm_obj, strainer_obj=strainer_obj, query=query, chat_history=chat_history, vector_store=vector_store)

# # Build RAG chain
# rag_chain, retrieved_docs = chain_builder.build_rag_chain()
# # Print retrieved documents before invoking the chain
# print("Retrieved Documents (Final Check):")
# for doc in retrieved_docs:
#     print(f"- {doc.page_content} [Metadata: {doc.metadata}]")
# # Pass query to the chain
# result = rag_chain.invoke({"input": query, "chat_history": chat_history})
# print("\nAnswer:", result["answer"])


import gradio as gr
from src.utils.chain_builder import ChainBuilder
from src.utils.strainer import FilterRetrievedDocuments
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# --- Load Required Objects ---
# Initialize LLM and Vector Store
llm_obj = ChatOpenAI(model="gpt-4o-mini", temperature=0)
vector_store = FAISS.load_local(
    "./vectorstore_faiss",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)

# Chat history - Empty initially
chat_history = []


# --- Define the Gradio Function ---
def process_query(user_query):
    """
    Process user query and return the answer.
    """
    try:
        # 1. Apply filters to retrieved documents
        strainer_obj = FilterRetrievedDocuments(user_query)

        # 2. Build RAG chain
        chain_builder = ChainBuilder(
            llm_obj=llm_obj,
            strainer_obj=strainer_obj,
            query=user_query,
            chat_history=chat_history,
            vector_store=vector_store
        )
        rag_chain, retrieved_docs = chain_builder.build_rag_chain()

        # 3. Print retrieved documents (optional - useful for debugging)
        print("Retrieved Documents (Final Check):")
        for doc in retrieved_docs:
            print(f"- {doc.page_content} [Metadata: {doc.metadata}]")

        # 4. Get the final answer
        result = rag_chain.invoke({"input": user_query, "chat_history": chat_history})
        answer = result["answer"]

        # 5. Append the interaction to chat history
        chat_history.append({"user": user_query, "bot": answer})

        return answer

    except Exception as e:
        return f"Error: {str(e)}"


# --- Gradio Interface ---
iface = gr.Interface(
    fn=process_query,                     # The function to process user input
    inputs=gr.Textbox(placeholder="Ask about Dota 2 patch notes!"),  # User input
    outputs="text",                        # Output will be plain text
    title="Dota 2 Patch Notes Assistant",  # Title of the app
    description="Ask me about the latest Dota 2 patch notes, hero updates, and changes!"  # Description
)

# Launch the Gradio app
iface.launch(share=True)  # Use 'share=True' to get a public URL
