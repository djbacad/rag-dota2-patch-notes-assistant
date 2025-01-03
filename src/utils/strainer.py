import re
import csv
import os

class FilterRetrievedDocuments:

  def __init__(self, query, previous_query=None):    
    self.query = query
    self.previous_query = previous_query  # Store previous query for context inference

  def load_set_from_csv(self,csv_path, key="name"):
    """
    Loads a set of names from a CSV file based on a specific column key.
    """
    data_set = set()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_set.add(row[key].strip().lower())
    return data_set
  
  def get_latest_patch_version(self, folder_path):
    """
    Scans the folder for patch files and extracts the latest patch version.
    """
    # Regex to match valid patch versions
    patch_pattern = re.compile(r"7\.\d+[a-z]?")

    # List all files and extract versions
    patch_versions = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Only process JSON files
            match = patch_pattern.match(filename)
            if match:
                patch_versions.append(match.group())

    # Sort the versions in ascending order
    patch_versions.sort(key=lambda x: tuple(int(part) if part.isdigit() else part for part in re.split('(\d+)', x)))
    return patch_versions[-1] if patch_versions else None

  def dynamic_filter(self) -> dict:
      """
      Dynamically constructs metadata filters based on the query and previous context.
      Args:
          query (str): The user's query.
          previous_query (str, optional): The previous query to infer missing details.
      Returns:
          dict: The metadata filter parameters.
      """
      query_lower = self.query.lower()
      prev_query_lower = self.previous_query.lower() if self.previous_query else ""
      filter_dict = {}

      # Load CSV data sets
      patch_pattern = re.compile(r"7\.\d+[a-z]?")
      heroes_set = self.load_set_from_csv("./data/mappers/heroes_mapper.csv")
      items_set = self.load_set_from_csv("./data/mappers/items_mapper.csv")
      abilities_set = self.load_set_from_csv("./data/mappers/heroes_abilities_mapper.csv")

      # 1. Extract patch version or detect 'latest'
      if "latest" in query_lower:
          latest_patch = self.get_latest_patch_version("./patchnotes_modified")
          print(latest_patch)
          if latest_patch:
              filter_dict["patch_version"] = latest_patch
      else:
          patch_match = patch_pattern.findall(query_lower) or patch_pattern.findall(prev_query_lower)
          if patch_match:
              filter_dict["patch_version"] = patch_match[0]

      # 2. Determine category and relevant IDs
      hero_id = next((hero for hero in heroes_set if hero in query_lower), None)
      if not hero_id:
          hero_id = next((hero for hero in heroes_set if hero in prev_query_lower), None)
      if hero_id:
          filter_dict["hero_id"] = hero_id

          # Check for specific keywords to filter categories
          if "talent" in query_lower:
              filter_dict["category"] = ["heroes-talents"]
          elif "skill" in query_lower or "ability" in query_lower:
              filter_dict["category"] = ["heroes-abilities"]
          elif "base" in query_lower:
              filter_dict["category"] = ["heroes-base"]
          else:
              filter_dict["category"] = ["heroes", "heroes-abilities", "heroes-base", "heroes-talents"]

      elif any(item in query_lower for item in items_set):
          item_id = next(item for item in items_set if item in query_lower)
          filter_dict["item_id"] = item_id
          filter_dict["category"] = "items"

      elif any(ability in query_lower for ability in abilities_set):
          ability_id = next(ability for ability in abilities_set if ability in query_lower)
          filter_dict["ability_id"] = ability_id
          filter_dict["category"] = "heroes-abilities"

      elif "item" in query_lower:
          filter_dict["category"] = "items"

      elif "summarize" in query_lower or "updates" in query_lower:
          filter_dict.pop("category", None)  # Remove 'category' if it exists

      return filter_dict

  def get_filtered_docs(self, retrieved_docs: list):
      """
      Filters the retrieved documents based on the query.
      Args:
          retrieved_docs (list): The list of retrieved documents.
      Returns:
          list: The filtered documents.
      """
      # Generate filters dynamically based on the query
      filter_criteria = self.dynamic_filter()

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




