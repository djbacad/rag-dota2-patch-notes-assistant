from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class ChainBuilder:

  def __init__(self, llm_obj, strainer_obj, query, chat_history, vector_store):
    self.llm = llm_obj
    self.strainer = strainer_obj
    self.query = query
    self.chat_history = chat_history
    self.vector_store = vector_store

  def build_rag_chain(self):
      template = """
      You are an assistant for DOTA2 patch notes queries.
      ONLY use the provided context below to answer the question.
      If the answer is not in the context, say 'I can't find anything in my knowledge base.'
      NEVER make up an answer.

      Context:
      {context}

      Question: {question}
      """
      prompt = PromptTemplate(
          template=template,
          input_variables=["context", "question"]
      )
      # Create the chain
      rag_chain = LLMChain(
          llm=self.llm,
          prompt=prompt
      )
      return rag_chain
  
  def invoke(self):
      retriever = self.vector_store.as_retriever(search_kwargs={"k": 1000})
      retrieved_docs = retriever.invoke(self.query)
      filtered_retrieved_docs =  self.strainer.get_filtered_docs(retrieved_docs)
      print(f"Filtered Retrieved Docs: {filtered_retrieved_docs}")
      context = "\n\n".join(doc.page_content for doc in filtered_retrieved_docs)
      rag_chain = self.build_rag_chain()
      result = rag_chain.invoke({
          "context": context,
          "question": self.query,
          "chat_history": []
      })

      return result
  
