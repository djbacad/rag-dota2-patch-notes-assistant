# Original script to modify the patch notes and get them ready for LangChain's JSONLoader

import os
import json
import numpy as np

folder_path = '../patchnotes'
list_patch_notes = os.listdir(folder_path)

def add_default_hero_values(data):
  for hero in data.get("heroes", []):
    # Add default talent_notes if not present
    if "talent_notes" not in hero:
      hero["talent_notes"] = ["No updates/changes"]
    if "hero_notes" not in hero:
      hero["hero_notes"] = ["No updates/changes"]
    if "abilities" not in hero:
      hero["abilities"] = [{'ability_id': np.nan}, {"ability_notes":["No updates/changes"]}]

for patch_note in list_patch_notes:
  # Load original
  with open(f"../patchnotes/{patch_note}", 'r') as file:
    json_data = json.load(file)
  add_default_hero_values(json_data)
  # Save the modified
  with open(f"../patchnotes_modified/{patch_note}", 'w') as f:
    json.dump(json_data, f)
    print(f"Modified {patch_note}.json")
