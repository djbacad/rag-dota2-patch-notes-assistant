import re
import csv

class RetrieveFilteredDocuments:

  def load_set_from_csv(self, csv_path, key="name"):
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
  
  def dynamic_filter(self, query: str) -> dict:
      """
      Dynamically constructs metadata filters based on the query.
      Args:
          query (str): The user's query.
      Returns:
          dict: The metadata filter parameters.
      """
      query_lower = query.lower()
      filter_dict = {}

      patch_pattern = re.compile(r"7\.\d+[a-z]?")  # Matches patch versions like 7.37c, 7.35c, etc
      heroes_set = self.load_set_from_csv("../data/mappers/heroes_mapper.csv")
      items_set = self.load_set_from_csv("../data/mappers/items_mapper.csv")
      abilities_set = self.load_set_from_csv("../data/mappers/heroes_abilities_mapper.csv")

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

  def get_filtered_docs(self, query: str, retrieved_docs: list):
      """
      Filters the retrieved documents based on the query.
      Args:
          query (str): The user's query.
          retrieved_docs (list): The list of retrieved documents.
      Returns:
          list: The filtered documents.
      """
      # Generate filters dynamically based on the query
      filter_criteria = self.dynamic_filter(query)

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




