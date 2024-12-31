from src.utils.storer import ConvertPatchNotesToDocuments, SanitizeDocuments
from langchain.schema import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph.message import add_messages
from uuid import uuid4
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
import pandas as pd
import faiss
import os

# Loadd the patch notes
list_patch_notes = os.listdir("./patchnotes_modified")

# Read the mappers
df_heroes = pd.read_csv("./data/mappers/heroes_mapper.csv")
dict_heroes_map = df_heroes.set_index(df_heroes['id'].astype(str))['name'].to_dict()
df_heroes_abilities = pd.read_csv("./data/mappers/heroes_abilities_mapper.csv")
dict_heroes_abilities_map = df_heroes_abilities.set_index(df_heroes_abilities['id'].astype(str))['name'].to_dict()
df_items = pd.read_csv("./data/mappers/items_mapper.csv")
dict_items_map = df_items.set_index(df_items['id'].astype(str))['name'].to_dict()

# Convert the patch notes to langchain docs
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


# Split Documents (Optional)
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

# Create VectorStore
print("Creating vectorstore")
embeddings = OpenAIEmbeddings()
sample_doc = docs_all[823].page_content
index = faiss.IndexFlatL2(len(embeddings.embed_query(sample_doc)))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

# Add docs to vectorstore
print("Adding docs to vectorstore")
uuids = [str(uuid4()) for _ in range(len(splits))]
vector_store.add_documents(documents=splits, ids=uuids)

# Save the vectorstore
print("Saving the vectorstore")
vector_store.save_local("./vectorstore_faiss")