class PatchNotesToDocumentLoader:

  def __init__():




  def replace_id_with_name(documents, dict_map, field):
    # Loop through each document and replace the item_id with its corresponding name
    for doc in documents:
      id = doc.metadata.get(field)
      # Convert the item_id to a string to match the dictionary keys
      str_id = str(id)
      # Replace item_id with corresponding value from the dictionary, if available
      if str_id in dict_map:
        doc.metadata['ability_id'] = dict_map[str_id]  # Replace with the item name4
      doc.page_content = f"Ability: {doc.metadata['ability_id']}. {doc.page_content}"  
    return documents
  
  # Extract metadata func for heroes' abilities
  def extract_metadata(record: dict, metadata: dict) -> dict:
    metadata["hero_id"] = record.get("hero_id")
    abilities=record.get("abilities", [])
    if abilities:
      metadata["ability_id"] = abilities[0].get("ability_id")
    else:
      metadata["ability_id"] = None
    metadata["category"] = "heroes-abilities"
    return metadata