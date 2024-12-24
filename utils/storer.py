from langchain_community.document_loaders import JSONLoader
import pandas as pd
import requests

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

  def add_patch_metadata(self, documents):
    for doc in documents:
      # Extract the patch version from the source (assuming file path is in 'source')
      source = doc.metadata.get("source", "")
      if source:
        patch_version = source.split("\\")[-1].replace(".json", "")
        doc.metadata["patch"] = patch_version
    return documents

  # Main Logic
  def convert(self):
    # Initialize empty list for document objects storage
    docs_all = []

    # (1) Heroes' abilities
    def extract_hero_abilities_metadata(record: dict, metadata: dict) -> dict:
      metadata["hero_id"] = record.get("hero_id")
      abilities=record.get("abilities", [])
      if abilities:
        metadata["ability_id"] = abilities[0].get("ability_id")
      else:
        metadata["ability_id"] = None
      metadata["category"] = "heroes-abilities"
      return metadata

    try:
      loader_heroes_abilities = JSONLoader(
        file_path=f"./patchnotes_modified/{self.patch_note}",
        jq_schema=".heroes[]",
        content_key="abilities",
        text_content=False,
        metadata_func=extract_hero_abilities_metadata
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
      print(f"Error processing heroes' abilities patch note {self.patch_note}: {e}")
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
        metadata_func=extract_metadata_heroes_talents
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
      print(f"Error processing heroes' talents patch note {self.patch_note}: {e}")
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
        metadata_func=extract_metadata_heroes_base
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
        metadata_func=extract_metadata_items
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
  
    # (5) Get docs_all
    docs_all = [doc for doc_list in docs_all for doc in doc_list]
    # (6) Insert patch version as metadata
    docs_all = self.add_patch_metadata(docs_all)
    return docs_all