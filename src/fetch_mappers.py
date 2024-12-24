import requests
import pandas as pd
import csv
import os

def get_heroes_mapper():
    """
    Fetch the heroes list from OpenDota and return a dict mapping hero ID -> localized_name.
    """
    url_heroes = 'https://api.opendota.com/api/heroes'
    heroes_response = requests.get(url_heroes)
    heroes_response.raise_for_status()  # Raise an error if the request failed
    json_heroes_map = heroes_response.json()  # Expecting a list of hero dicts
    df_heroes = pd.DataFrame(json_heroes_map)
    dict_heroes_map = df_heroes.set_index(df_heroes['id'].astype(str))['localized_name'].to_dict()
    return dict_heroes_map


def get_heroes_abilities_mapper():
    """
    Fetch the hero abilities map from OpenDota constants and return a dict
    mapping ability_id (as string) -> replaced underscore name.
    """
    url_abilities = 'https://api.opendota.com/api/constants/ability_ids'
    abilities_response = requests.get(url_abilities)
    abilities_response.raise_for_status()
    json_abilities_map = abilities_response.json()
    dict_abilities_map = {
        key: value.replace('_', ' ') for key, value in json_abilities_map.items()
    }
    return dict_abilities_map


def get_items_mapper():
    """
    Fetch the items map from OpenDota constants and return a dict
    mapping item_id (as string) -> replaced underscore name.
    """
    url_items = 'https://api.opendota.com/api/constants/item_ids'
    items_response = requests.get(url_items)
    items_response.raise_for_status()
    json_items_map = items_response.json()
    dict_items_map = {
        key: value.replace('_', ' ') for key, value in json_items_map.items()
    }
    return dict_items_map


def save_mapper_as_csv(mapping: dict, filename: str):
    """
    Save the given dict `mapping` (id -> name) to a CSV file in the 'data' folder.
    The CSV will have two columns: id, name.
    """
    os.makedirs("../data/mappers", exist_ok=True)  # Ensure 'data' folder exists
    filepath = os.path.join("../data/mappers", filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name"])  # column headers
        for k, v in mapping.items():
            writer.writerow([k, v])
    print(f"Saved {filename} with {len(mapping)} entries to '{filepath}'.")


if __name__ == "__main__":
    # Fetch and save the heroes mapper
    print("Fetching heroes mapper...")
    heroes_mapper = get_heroes_mapper()
    print("Heroes mapper size:", len(heroes_mapper))
    save_mapper_as_csv(heroes_mapper, "heroes_mapper.csv")

    # Fetch and save the heroes abilities mapper
    print("Fetching heroes abilities mapper...")
    heroes_abilities_mapper = get_heroes_abilities_mapper()
    print("Heroes abilities mapper size:", len(heroes_abilities_mapper))
    save_mapper_as_csv(heroes_abilities_mapper, "heroes_abilities_mapper.csv")

    # Fetch and save the items mapper
    print("Fetching items mapper...")
    items_mapper = get_items_mapper()
    print("Items mapper size:", len(items_mapper))
    save_mapper_as_csv(items_mapper, "items_mapper.csv")
