# Original script to download all patch notes <= 7.37e
import requests
import json
import pandas as pd

df = pd.read_csv("data/patchnotes/list_patchnotes.csv")
list_patches = df["patch"].tolist()

for p in list_patches:
# URL of the Dota2 API endpoint
    url = f'https://www.dota2.com/datafeed/patchnotes?version={p}&language=english'
    response = requests.get(url)
    data = response.json()
    # Save into a file
    # Save the JSON response to a file for JSONLoader to read
    with open(f"patchnotes/{p}.json", "w") as f:
        json.dump(data, f)
        print(f"Saved {p}.json")
    