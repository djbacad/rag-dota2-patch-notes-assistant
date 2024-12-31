from langchain_community.document_loaders import JSONLoader
from utils.storer import ConvertPatchNotesToDocuments, SanitizeDocuments
import requests
import os
import re
import pandas as pd
from langchain.schema import Document

from typing import Sequence
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from uuid import uuid4
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
import faiss
import re
import csv

df_heroes = pd.read_csv("data/mappers/heroes_mapper.csv")
dict_heroes_map = df_heroes.set_index(df_heroes['id'].astype(str))['name'].to_dict()

df_heroes_abilities = pd.read_csv("data/mappers/heroes_abilities_mapper.csv")
dict_heroes_abilities_map = df_heroes_abilities.set_index(df_heroes_abilities['id'].astype(str))['name'].to_dict()

df_items = pd.read_csv("data/mappers/items_mapper.csv")
dict_items_map = df_items.set_index(df_items['id'].astype(str))['name'].to_dict()

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
sanitizer = SanitizeDocuments(docs_all)
docs_all = sanitizer.sanitize()


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
embeddings = OpenAIEmbeddings()
sample_doc = docs_all[823].page_content
index = faiss.IndexFlatL2(len(embeddings.embed_query(sample_doc)))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


### 4. Add docs to vectorstore ###
uuids = [str(uuid4()) for _ in range(len(splits))]
vector_store.add_documents(documents=splits, ids=uuids)


### 5. Set Up Retriever with Metadata Filtering ###
### 5.1 Load Data Mappers ###
def load_set_from_csv(csv_path, key="name"):
    """
    Loads a set of names from a CSV file based on a specific column key.
    """
    data_set = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_set.add(row[key].strip().lower())
    return data_set


# Define regex patterns
patch_pattern = re.compile(r"7\.\d+[a-z]?")  # Matches patch versions like 7.37c
heroes_set = load_set_from_csv("data/mappers/heroes_mapper.csv")
items_set = load_set_from_csv("data/mappers/items_mapper.csv")
abilities_set = load_set_from_csv("data/mappers/heroes_abilities_mapper.csv")

def dynamic_filter(query: str) -> dict:
    """
    Dynamically constructs metadata filters based on the query.
    Args:
        query (str): The user's query.
    Returns:
        dict: The metadata filter parameters.
    """
    query_lower = query.lower()
    filter_dict = {}

    # 1. Extract patch version
    patch_match = patch_pattern.findall(query_lower)
    if patch_match:
        filter_dict["patch_version"] = patch_match[0]

    # 2. Determine category and relevant IDs
    if any(hero in query_lower for hero in heroes_set):
        # If the query is about a hero
        hero_id = next(hero for hero in heroes_set if hero in query_lower)
        filter_dict["hero_id"] = hero_id

        # Check for specific keywords to filter categories
        if "talent" in query_lower:
            filter_dict["category"] = ["heroes-talents"]
        elif "skill" in query_lower or "ability" in query_lower:
            filter_dict["category"] = ["heroes-abilities"]
        elif "base" in query_lower:
            filter_dict["category"] = ["heroes-base"]
        else:
            # Default categories if no specific keyword is found
            filter_dict["category"] = ["heroes", "heroes-abilities", "heroes-base", "heroes-talents"]

    elif any(item in query_lower for item in items_set):
        # If the query is about an item
        item_id = next(item for item in items_set if item in query_lower)
        filter_dict["item_id"] = item_id
        filter_dict["category"] = "items"

    elif any(ability in query_lower for ability in abilities_set):
        # If the query is about a specific skill
        ability_id = next(ability for ability in abilities_set if ability in query_lower)
        filter_dict["ability_id"] = ability_id
        filter_dict["category"] = "heroes-abilities"

    elif "summarize" in query_lower or "updates" in query_lower:
        # If the query is about general patch updates, exclude 'category' from filters
        filter_dict.pop("category", None)  # Remove 'category' if it exists

    return filter_dict

def get_filtered_docs(query: str, retrieved_docs: list):
    """
    Filters the retrieved documents based on the query.
    Args:
        query (str): The user's query.
        retrieved_docs (list): The list of retrieved documents.
    Returns:
        list: The filtered documents.
    """
    # Generate filters dynamically based on the query
    filter_criteria = dynamic_filter(query)

    def matches_criteria(doc):
        for key, values in filter_criteria.items():
            # Ensure values is a list for comparison
            if not isinstance(values, list):
                values = [values]

            # Normalize values for case-insensitive comparison
            values = [str(val).lower() for val in values]
            doc_value = str(doc.metadata.get(key, '')).lower()

            # Check if metadata key exists and matches any value in the list
            if key == 'category':
                # Handle 'category' as a string and check if it matches any value
                if doc_value not in values:
                    return False
            else:
                # Handle other fields
                if doc_value not in values:
                    return False
        return True

    # Apply filtering
    filtered_docs = [doc for doc in retrieved_docs if matches_criteria(doc)]
    return filtered_docs

### 5.3 Build Dynamic Retriever ###
def build_retriever():
    """
    Builds a retriever with metadata filtering based on the query.
    """
    # Apply filters in search_kwargs
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1000})
    return retriever


### 5. Contextualize Question ###
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


def build_rag_chain(user_query, chat_history):
    """
    Dynamically builds a RAG chain based on query and chat history.
    """
    # Generate filter parameters based on the user query
    filter_params = dynamic_filter(user_query)
    print(f"filter_params: {filter_params}")

    # Build Retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 1000})

    # Retrieve documents
    retrieved_docs = retriever.invoke(user_query)
    filtered_docs = get_filtered_docs(user_query, retrieved_docs)

    # Context-aware retriever for multi-turn queries
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
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
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain, filtered_docs  # Return both the RAG chain and retrieved docs



### 7. Example Query ###
user_query = "What are the changes for shadow shaman in 7.37e??"
chat_history = []

rag_chain, retrieved_docs = build_rag_chain(user_query, chat_history)

# Print retrieved documents before invoking the chain
print("Retrieved Documents (Final Check):")
for doc in retrieved_docs:
    print(f"- {doc.page_content} [Metadata: {doc.metadata}]")

# Pass query to the chain
result = rag_chain.invoke({"input": user_query, "chat_history": chat_history})
print("\nAnswer:", result["answer"])