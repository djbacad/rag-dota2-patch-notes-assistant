from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class ChainBuilder:

  def __init__(self, llm_obj, strainer_obj, query, chat_history, vector_store):
    self.llm = llm_obj
    self.strainer = strainer_obj
    self.query = query
    self.chat_history = chat_history
    self.vector_store = vector_store

  def build_rag_chain(self):
      """
      Dynamically builds a RAG chain based on query and chat history.
      """
      # Generate filter parameters based on the user query
      filter_params = self.strainer.dynamic_filter()
      print(f"filter_params: {filter_params}")

      # Build Retriever
      retriever = self.vector_store.as_retriever(search_kwargs={"k": 1000})

      # Retrieve documents
      retrieved_docs = retriever.invoke(self.query)
      filtered_docs = self.strainer.get_filtered_docs(retrieved_docs)


      contextualize_q_system_prompt = (
          "Given a chat history and the latest user question "
          "which might reference context in the chat history, "
          "formulate a standalone question which can be understood "
          "without the chat history. Do NOT answer the question, "
          "just reformulate it if needed and otherwise return it as is."
      )
      contextualize_q_prompt = ChatPromptTemplate.from_messages(
          [
              ("system", contextualize_q_system_prompt),
              MessagesPlaceholder("chat_history"),
              ("human", "{input}"),
          ]
      )

      # Context-aware retriever for multi-turn queries
      history_aware_retriever = create_history_aware_retriever(
          self.llm, retriever, contextualize_q_prompt
      )

      # Define system prompt for answering questions
      system_prompt = (
          "You are an assistant for question-answering tasks about DOTA2 patch notes. "
          "Use the following pieces of retrieved context to answer "
          "the question. If you don't know the answer, say that you "
          "don't know. Use three sentences maximum and keep the "
          "answer concise."
          "\n\n"
          "{context}"
      )
      qa_prompt = ChatPromptTemplate.from_messages(
          [
              ("system", system_prompt),
              MessagesPlaceholder("chat_history"),
              ("human", "{input}"),
          ]
      )

      # Create the chain
      question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
      rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

      return rag_chain, filtered_docs  # Return both the RAG chain and retrieved docs
