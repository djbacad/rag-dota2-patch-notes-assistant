import os
import pandas as pd
import re
import csv 
from langchain.schema import Document
from typing import Sequence
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from utils.storer import ConvertPatchNotesToDocuments
from uuid import uuid4

# Get all patch notes
list_patch_notes = os.listdir("patchnotes_modified")

# Load mappers
df_heroes = pd.read_csv("data/mappers/heroes_mapper.csv")
dict_heroes_map = df_heroes.set_index(df_heroes['id'].astype(str))['name'].to_dict()
df_heroes_abilities = pd.read_csv("data/mappers/heroes_abilities_mapper.csv")
dict_heroes_abilities_map = df_heroes_abilities.set_index(df_heroes_abilities['id'].astype(str))['name'].to_dict()
df_items = pd.read_csv("data/mappers/items_mapper.csv")
dict_items_map = df_items.set_index(df_items['id'].astype(str))['name'].to_dict()

# Convert patch notes to langchain docs via jsonloader
docs_all = []
for patch_note in list_patch_notes:
  try:
    print(f"Converting Patch Note {patch_note} to LangChainDoc via JSONLoader")
    converter_pns_to_docs = (
        ConvertPatchNotesToDocuments(
            patch_note=patch_note,
            dict_heroes_abilities_mapper=dict_heroes_abilities_map, 
            dict_heroes_mapper=dict_heroes_map, 
            dict_items_mapper=dict_items_map
        )
    )
    docs = converter_pns_to_docs.convert()
    docs_all.append(docs)
  except Exception as e:
    print(f"Error processing patch note {patch_note}: {e}")
    pass

docs_all = [doc for doc_list in docs_all for doc in doc_list]

# Replace None values in metadata with "N/A"
for doc in docs_all:
    # Iterate through metadata and replace None
    doc.metadata = {
        key: (value if value is not None else "N/A")  # Replace None with "N/A"
        for key, value in doc.metadata.items()
    }


### 1. Initialize LLM ###
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

### 2. Split Documents ### (Optional)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs_all)

# Add sequential ID to each document in splits # This is required for chroma
for idx, doc in enumerate(splits):
    # Create a new Document with id at the top level
    splits[idx] = Document(
        id=str(idx + 1),  # Add a unique ID
        page_content=doc.page_content,
        metadata=doc.metadata
    )

### 3. Create VectorStore ###
vectorstore = Chroma(
    collection_name="dota_patch_notes",
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./chroma_langchain_db", 
)
uuids = [str(uuid4()) for _ in range(len(splits))]


print("Adding docs to vectorstore")

print("\nValidating metadata before inserting into Chroma:")
for idx, doc in enumerate(splits):
    print(f"[{idx}] Metadata: {doc.metadata}")

print(f"Total splits: {len(splits)}, Total UUIDs: {len(uuids)}")
if len(splits) != len(uuids):
    raise ValueError("Mismatch between splits and UUIDs!")


### 4. Add docs to vectorstore ###
try:
    print("Adding docs to vectorstore...")
    vectorstore.add_documents(documents=splits, ids=uuids)
    print("Done adding docs to vectorstore.")
except Exception as e:
    print(f"Error adding documents to vectorstore: {e}")

print("Document count in vectorstore:", vectorstore._collection.count())

results = vectorstore.similarity_search(query="test query", k=5)
print("Retrieved documents:")
for res in results:
    print(res.page_content, res.metadata)

# ### 5. Set Up Retriever with Metadata Filtering ### 
# ### 5.1 Load Data Mappers ### 
# def load_set_from_csv(csv_path, key="name"):
#     """
#     Loads a set of names from a CSV file based on a specific column key.
#     """
#     data_set = set()
#     with open(csv_path, "r", encoding="utf-8") as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             data_set.add(row[key].strip().lower())
#     return data_set 

# # Load CSV mappers
# heroes_set = load_set_from_csv("data/mappers/heroes_mapper.csv")
# items_set = load_set_from_csv("data/mappers/items_mapper.csv")
# abilities_set = load_set_from_csv("data/mappers/heroes_abilities_mapper.csv")

# print("Done with the mappers logic")

# ### 5.2 Metadata Filter Function ###
# patch_pattern = re.compile(r"7\.\d+[a-z]?")

# def metadata_filter(query: str) -> dict:
#     """
#     Parses query to identify hero names, items, abilities, and patch numbers
#     for filtering metadata in the retriever.
#     """
#     query_lower = query.lower()
#     filter_dict = {}

#     # Match patch versions (e.g., 7.36, 7.36b)
#     patches = patch_pattern.findall(query_lower)
#     if patches:
#         filter_dict["patch"] = patches[0]

#     # Match heroes
#     for hero in heroes_set:
#         if hero in query_lower:
#             filter_dict["hero_id"] = hero
#             break

#     # Match items
#     for item in items_set:
#         if item in query_lower:
#             filter_dict["item_id"] = item
#             break

#     # Match abilities
#     for ability in abilities_set:
#         if ability in query_lower:
#             filter_dict["ability_id"] = ability
#             break

#     return filter_dict


# ### 5.3 Build Dynamic Retriever ###
# def build_retriever(query):
#     """
#     Builds a retriever with metadata filtering based on the query.
#     """
#     # Extract filters dynamically from the query
#     filter_params = metadata_filter(query)

#     # Apply filters in search_kwargs
#     retriever = vectorstore.as_retriever(search_kwargs={
#         "k": 100,  # Number of top documents to retrieve
#         "filter": filter_params  # Apply metadata filters
#     })
#     return retriever


# ### 6. Contextualize Question ### 
# contextualize_q_system_prompt = (
#     "Given a chat history and the latest user question "
#     "which might reference context in the chat history, "
#     "formulate a standalone question which can be understood "
#     "without the chat history. Do NOT answer the question, "
#     "just reformulate it if needed and otherwise return it as is."
# )
# contextualize_q_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )


# def build_rag_chain(user_query, chat_history):
#     """
#     Dynamically builds a RAG chain based on query and chat history.
#     """
#     # Create a retriever based on query
#     retriever = build_retriever(user_query)

#     # Retrieve documents
#     retrieved_docs = retriever.invoke(user_query)  # Retrieve documents directly
    
#     # Log retrieved documents
#     print("\nRetrieved Documents:")
#     for doc in retrieved_docs:
#         print(f"- {doc.page_content} [Metadata: {doc.metadata}]")
#     print("\n")

#     # Context-aware retriever for multi-turn queries
#     history_aware_retriever = create_history_aware_retriever(
#         llm, retriever, contextualize_q_prompt
#     )

#     # Define system prompt for answering questions
#     system_prompt = (
#         "You are an assistant for question-answering tasks about DOTA2 patch notes. "
#         "Use the following pieces of retrieved context to answer "
#         "the question. If you don't know the answer, say that you "
#         "don't know. Use three sentences maximum and keep the "
#         "answer concise."
#         "\n\n"
#         "{context}"
#     )
#     qa_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", system_prompt),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}"),
#         ]
#     )

#     # Create the chain
#     question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
#     rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

#     return rag_chain, retrieved_docs  # Return both the RAG chain and retrieved docs

# ### 7. Example Query ###
# user_query = "What updates were made in patch 7.36?"
# chat_history = []

# rag_chain, retrieved_docs = build_rag_chain(user_query, chat_history)

# # Print retrieved documents before invoking the chain
# print("Retrieved Documents (Final Check):")
# for doc in retrieved_docs:
#     print(f"- {doc.page_content} [Metadata: {doc.metadata}]")

# # Pass query to the chain
# result = rag_chain.invoke({"input": user_query, "chat_history": chat_history})
# print("\nAnswer:", result["answer"])