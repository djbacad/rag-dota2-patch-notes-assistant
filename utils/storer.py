from langchain_community.document_loaders import JSONLoader
import pandas as pd
import requests

class ConvertPatchNotesToDocuments:

  def __init__(self, patch_note):
    self.patch_note=patch_note

  # For generating heroes mapper
  def get_heroes_mapper(self):
    url_heroes = 'https://api.opendota.com/api/heroes'
    heroes_response = requests.get(url_heroes)
    json_heroes_map = heroes_response.json()
    df_heroes = pd.DataFrame(json_heroes_map)
    dict_heroes_map = df_heroes.set_index('id')['localized_name'].to_dict()
    return dict_heroes_map

  # For generating heroes abilities mapper
  def get_heroes_abilities_mapper(self):
    url_abilities = 'https://api.opendota.com/api/constants/ability_ids'
    abilities_response = requests.get(url_abilities)
    json_abilities_map = abilities_response.json()
    dict_abilities_map = {key: value.replace('_', ' ') for key, value in json_abilities_map.items()}
    return dict_abilities_map
  
  # For generating items mapper
  def get_items_mapper(self):
    url_items = 'https://api.opendota.com/api/constants/item_ids'
    items_response = requests.get(url_items)
    json_items_map = items_response.json()
    dict_items_map = {key: value.replace('_', ' ') for key, value in json_items_map.items()}
    return dict_items_map

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
    except Exception as e:
      print(f"Error processing patch note {self.patch_note}: {e}")
      pass

    # Generate doc objects via JSONLoader
    docs_heroes_abilities = loader_heroes_abilities.load()
    # Append to docs_all
    docs_all.append(docs_heroes_abilities)

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
    except Exception as e:
      print(f"Error processing patch note {self.patch_note}: {e}")
      pass
  
    # Generate doc objects via JSONLoader
    docs_heroes_talents = loader_heroes_talents.load()
    # Append to docs_all
    docs_all.append(docs_heroes_talents)

    # (3) Heroes' base
    # Heroes Base
    def extract_metadata(record: dict, metadata: dict) -> dict:
      metadata["hero_id"] = record.get("hero_id")
      metadata["category"] = "heroes-base"
      return metadata

    try:
      loader_heroes_base = JSONLoader(
        file_path=f"patchnotes_modified/{self.patch_note}",
        jq_schema=".heroes[]",
        content_key="hero_notes",
        text_content=False,
        metadata_func=extract_metadata
      )
    except Exception as e:
      print(f"Error processing patch note {self.patch_note}: {e}")
      pass
  
    # Generate doc objects via JSONLoader
    docs_heroes_base = loader_heroes_base.load()
    # Append to docs_all
    docs_all.append(docs_heroes_base)

    # (4) Items
    # Items
    def extract_metadata(record: dict, metadata: dict) -> dict:
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
        metadata_func=extract_metadata
      )
    except Exception as e:
      print(f"Error processing patch note {self.patch_note}: {e}")
      pass
  
    # Generate doc objects via JSONLoader
    docs_items = loader_items.load()
    # Append to docs_all
    docs_all.append(docs_items)








    # Generate abilities mapper
    dict_abilities_map = self.get_heroes_abilities_mapper()
    # Generate heroes mapper
    dict_abilities_map = self.get_heroes_mapper()
    # Generate items mapper
    dict_abilities_map = self.get_items_mapper()


    # Replace ids with actual names
    docs_heroes_abilities = (
      self.replace_id_with_name(
        documents=docs, 
        dict_map=dict_abilities_map,
        field="ability_id",
        field_name="Ability")
    )
    docs_all.append(docs_heroes_abilities)
    return docs_all
