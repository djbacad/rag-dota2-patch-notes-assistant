from langchain_community.document_loaders import JSONLoader
import json
import re

class ConvertPatchNotesToDocuments:

  def __init__(self, patch_note, dict_heroes_abilities_mapper, dict_heroes_mapper, dict_items_mapper):
    self.patch_note=patch_note
    self.dict_heroes_abilities_mapper = dict_heroes_abilities_mapper
    self.dict_heroes_mapper = dict_heroes_mapper
    self.dict_items_mapper = dict_items_mapper

  # Common
  # For replacing id vars with actual ability/hero/item names
  def replace_id_with_name(self, documents, dict_map, field_name, field):
    # Loop through each document and replace the item_id with its corresponding name
    for doc in documents:
      id = doc.metadata.get(field)
      # Convert the item_id to a string to match the dictionary keys
      str_id = str(id)
      # Replace item_id with corresponding value from the dictionary, if available
      if str_id in dict_map:
        doc.metadata[field] = dict_map[str_id]  # Replace with the item name4
      doc.page_content = f"{field_name}: {doc.metadata[field]}. {doc.page_content}"  
    return documents

  def add_patch_metadata(self):
     # Pre-load JSON file and extract timestamp
    with open(f"./patchnotes_modified/{self.patch_note}", "r") as f:
        patch_data = json.load(f)
        patch_timestamp = patch_data.get("patch_timestamp", "N/A")
        patch_number = patch_data.get("patch_number", "N/A")
    return patch_number, patch_timestamp

  # Main Logic
  def convert(self):
    # Initialize empty list for document objects storage
    docs_all = []
    patch_number, patch_timestamp = self.add_patch_metadata()

    # (1) Heroes' abilities
    def extract_hero_abilities_metadata(record: dict, metadata: dict) -> dict:
      metadata["hero_id"] = record.get("hero_id")
      abilities=record.get("abilities", [])
      if abilities:
        metadata["ability_id"] = abilities[0].get("ability_id")
      else:
        metadata["ability_id"] = "N/A"
      metadata["category"] = "heroes-abilities"
      return metadata

    try:
      loader_heroes_abilities = JSONLoader(
        file_path=f"./patchnotes_modified/{self.patch_note}",
        jq_schema=".heroes[]",
        content_key="abilities",
        text_content=False,
        metadata_func=lambda r, m: {**extract_hero_abilities_metadata(r, m), "patch_timestamp": patch_timestamp, "patch_version": patch_number}
      )

      # Generate doc objects via JSONLoader
      docs_heroes_abilities = loader_heroes_abilities.load()

      # Replace hero ids with actual names
      docs_heroes_abilities = (
        self.replace_id_with_name(
          documents=docs_heroes_abilities, 
          dict_map=self.dict_heroes_mapper,
          field="hero_id",
          field_name="Hero")
      )
      # Replace ability ids with actual names
      docs_heroes_abilities = (
        self.replace_id_with_name(
          documents=docs_heroes_abilities, 
          dict_map=self.dict_heroes_abilities_mapper,
          field="ability_id",
          field_name="Ability")
      )
      # Append to docs_all
      docs_all.append(docs_heroes_abilities)
    except Exception as e:
      print(f"Error processing heroes' abilities for patch note {self.patch_note}: {e}")
      pass

    # (2) Heroes' talents
    # Heroes Talents
    def extract_metadata_heroes_talents(record: dict, metadata: dict) -> dict:
      metadata["hero_id"] = record.get("hero_id")
      metadata["category"] = "heroes-talents"
      return metadata

    try:
      loader_heroes_talents = JSONLoader(
        file_path=f"patchnotes_modified/{self.patch_note}",
        jq_schema=".heroes[]",
        content_key="talent_notes",
        text_content=False,
        metadata_func=lambda r, m: {**extract_metadata_heroes_talents(r, m), "patch_timestamp": patch_timestamp, "patch_version": patch_number}
      )
      # Generate doc objects via JSONLoader
      docs_heroes_talents = loader_heroes_talents.load()
      # Replace hero ids with actual names
      docs_heroes_talents = (
        self.replace_id_with_name(
          documents=docs_heroes_talents, 
          dict_map=self.dict_heroes_mapper,
          field="hero_id",
          field_name="Hero")
      )
      # Append to docs_all
      docs_all.append(docs_heroes_talents)
    except Exception as e:
      print(f"Error processing heroes' talents for patch note {self.patch_note}: {e}")
      pass
  
    # (3) Heroes' base
    # Heroes Base
    def extract_metadata_heroes_base(record: dict, metadata: dict) -> dict:
      metadata["hero_id"] = record.get("hero_id")
      metadata["category"] = "heroes-base"
      return metadata

    try:
      loader_heroes_base = JSONLoader(
        file_path=f"patchnotes_modified/{self.patch_note}",
        jq_schema=".heroes[]",
        content_key="hero_notes",
        text_content=False,
        metadata_func=lambda r, m: {**extract_metadata_heroes_base(r, m), "patch_timestamp": patch_timestamp, "patch_version": patch_number}
      )
      # Generate doc objects via JSONLoader
      docs_heroes_base = loader_heroes_base.load()
      # Replace hero ids with actual names
      docs_heroes_base = (
        self.replace_id_with_name(
          documents=docs_heroes_base, 
          dict_map=self.dict_heroes_mapper,
          field="hero_id",
          field_name="Hero")
      )
      # Append to docs_all
      docs_all.append(docs_heroes_base)
    except Exception as e:
      print(f"Error processing heroes' bases for patch note {self.patch_note}: {e}")
      pass
  
    # (4) Items
    # Items
    def extract_metadata_items(record: dict, metadata: dict) -> dict:
      metadata["item_id"] = record.get("ability_id")
      metadata["category"] = "items"
      return metadata

    try:
      loader_items = JSONLoader(
        file_path=f"patchnotes_modified/{self.patch_note}",
        jq_schema=".items[]",
        content_key="ability_notes",
        is_content_key_jq_parsable=False,
        text_content=False,
        metadata_func=lambda r, m: {**extract_metadata_items(r, m), "patch_timestamp": patch_timestamp, "patch_version": patch_number}
      )
      # Generate doc objects via JSONLoader
      docs_items = loader_items.load()
      # Replace item ids with actual names
      docs_items = (
        self.replace_id_with_name(
          documents=docs_items, 
          dict_map=self.dict_items_mapper,
          field="item_id",
          field_name="Item")
      )
      # Append to docs_all
      docs_all.append(docs_items)
    except Exception as e:
      print(f"Error processing items for patch note {self.patch_note}: {e}")
      pass

    # (5) Generic patch updates
    # Pre-load JSON file and extract timestamp
    try:
      loader_generic_updates = JSONLoader(
        file_path=f"./patchnotes_modified/{self.patch_note}",
        jq_schema=".generic[]",
        content_key="note",
        text_content=False,
        metadata_func=lambda r, m: {**m, "category": "generic-updates", "patch_timestamp": patch_timestamp, "patch_version": patch_number}
      )

      # Generate doc objects via JSONLoader
      docs_generic_updates = loader_generic_updates.load()

      # Append to docs_all
      docs_all.append(docs_generic_updates)
    except Exception as e:
      print(f"Error processing generic updates for patch note {self.patch_note}: {e}")
      pass
  
    # (6) Get docs_all
    docs_all = [doc for doc_list in docs_all for doc in doc_list]

    

    return docs_all
  
class SanitizeDocuments:
  def __init__(self, documents):
    self.documents = documents

  def sanitize(self):
    # Replace None values in metadata with "N/A"
    for doc in self.documents:
      # Iterate through metadata and replace None
      doc.metadata = {
          key: (value if value is not None else "N/A")  # Replace None with "N/A"
          for key, value in doc.metadata.items()
      }

    # Add category & patch metadata to page content for improved vector search
    for doc in self.documents:
      # Append category and patch to the content
      category = doc.metadata.get("category", "N/A")
      patch_version = doc.metadata.get("patch_version", "N/A")
      patch_timestamp = doc.metadata.get("patch_timestamp", "N/A")  
      
      # Append this info to the text content
      doc.page_content = f"Patch-Version: {patch_version}. Category: {category}.  Patch-Timestamp: {patch_timestamp}. {doc.page_content}"

    # Remove unwanted content based on rules
    sanitized_docs = []
    for doc in self.documents:
      # Rule 1: Skip documents containing '<br>'
      if '<br>' in doc.page_content:
          continue

      # Rule 2: Remove unwanted characters from page content
      clean_content = re.sub(r'[\[\]<>]', '', doc.page_content)  # Remove [, ], <, >
      clean_content = re.sub(r'\bindent-level\b', '', clean_content)  # Remove 'indent-level'

      # Update the sanitized content
      doc.page_content = clean_content.strip()
      sanitized_docs.append(doc)

    return sanitized_docs