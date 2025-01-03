import gradio as gr
import tiktoken
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import SQLChatMessageHistory

from src.utils.chain_builder import ChainBuilder
from src.utils.strainer import FilterRetrievedDocuments


# --- Initialize Components ---

# LLM and Vector Store
llm_obj = ChatOpenAI(model="gpt-4o-mini", temperature=0)
vector_store = FAISS.load_local(
    "./vectorstore_faiss",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)

# Persistent Chat History
chat_message_history = SQLChatMessageHistory(
    session_id="single-user", connection_string="sqlite:///chat_history.db"
)


# --- Context Truncator ---

MAX_TOKENS = 120000  # Leave buffer under OpenAI's 128k limit
def truncate_context(context, max_tokens=MAX_TOKENS):
    """
    Truncates the context to fit within the max token limit.
    """
    # Initialize tiktoken tokenizer for GPT-4
    tokenizer = tiktoken.encoding_for_model("gpt-4")

    # Tokenize the context
    tokens = tokenizer.encode(context)

    # Truncate older parts if limit exceeds
    if len(tokens) > max_tokens:
        tokens = tokens[-max_tokens:]

    # Decode back to string
    truncated_context = tokenizer.decode(tokens)
    return truncated_context


# --- RAG Chain Builder ---

def build_chain(user_query, chat_history):
    """
    Dynamically builds a RAG chain based on query and chat history.
    """
    # Apply filters
    strainer_obj = FilterRetrievedDocuments(user_query)
    print(f"Filters: {strainer_obj.dynamic_filter()}")
    # Build RAG chain
    chain_builder = ChainBuilder(
        llm_obj=llm_obj,
        strainer_obj=strainer_obj,
        query=user_query,
        chat_history=chat_history,
        vector_store=vector_store
    )

    # Build the RAG chain and invoke results
    invoked_results = chain_builder.invoke()
    return invoked_results



# --- Chat Function ---

def chat_with_rag(user_query, chat_history):
    """
    Handles user query and interacts with the RAG pipeline.
    """
    try:
        # # Append user's query to the persistent chat history
        # chat_message_history.add_user_message(user_query)

        # # Retrieve previous chat history
        # chat_history = chat_message_history.messages

        # --- CLEAR CHAT HISTORY BEFORE PROCESSING --- #
        chat_message_history.clear()  # Clear persistent chat history

        # Retrieve fresh history (empty now since we just cleared it)
        chat_history = []

        # --- TRUNCATE CHAT HISTORY ---
        MAX_HISTORY = 2
        if len(chat_history) > MAX_HISTORY * 2:
            chat_history = chat_history[-MAX_HISTORY * 2:]

        # --- INFER PREVIOUS QUERY ---
        previous_query = None
        if len(chat_history) >= 2:
            previous_query = chat_history[-2].content  # Use the last user query as fallback

        # --- BUILD RAG CHAIN ---
        strainer_obj = FilterRetrievedDocuments(user_query, previous_query)
        print(f"Filters: {strainer_obj.dynamic_filter()}")

        chain_builder = ChainBuilder(
            llm_obj=llm_obj,
            strainer_obj=strainer_obj,
            query=user_query,
            chat_history=chat_history,
            vector_store=vector_store
        )

        # --- GET RESULTS ---
        invoked_results = chain_builder.invoke()
        print(invoked_results)
        answer = invoked_results["text"]

        # Append AI's response to the persistent chat history
        chat_message_history.add_ai_message(answer)

        return answer

    except Exception as e:
        return f"Error: {str(e)}"


# --- Gradio Chat UI ---

chat_interface = gr.ChatInterface(
    fn=chat_with_rag,  # Function to handle the chat
    title="🌠 Dota 2 Patch Notes Assistant",
    description="🚀Ask me about the latest Dota 2 patch notes, hero updates, and changes!",
)

# Launch Gradio app
chat_interface.launch(share=True)