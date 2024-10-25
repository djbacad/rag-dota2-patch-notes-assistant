import requests

# Original script to download all patch notes <= 7.37d
list_patches = [
    "7.20", "7.20b", "7.20c", "7.20d", "7.20e", 
    "7.21", "7.21b", "7.21c", "7.21d", 
    "7.22", "7.22b", "7.22c", "7.22d", "7.22e", "7.22f", "7.22g", "7.22h",
    "7.23", "7.23a", "7.23b", "7.23c", "7.23d", "7.23e", "7.23f", 
    "7.24", "7.24b", 
    "7.25", "7.25a", "7.25b", "7.25c", 
    "7.26", "7.26a", "7.26b", "7.26c", 
    "7.27", "7.27a", "7.27b", "7.27c", "7.27d", 
    "7.28", "7.28a", "7.28b", "7.28c", 
    "7.29", "7.29b", "7.29c", "7.29d", 
    "7.30", "7.30b", "7.30c", "7.30d", "7.30e", 
    "7.31", "7.31b", "7.31c", "7.31d",
    "7.32", "7.32b", "7.32c", "7.32d", "7.32e",
    "7.33", "7.33b", "7.33c", "7.33d", "7.33e",
    "7.34", "7.34b", "7.34c", "7.34d", "7.34e",
    "7.35", "7.35b", "7.35c", "7.35d", 
    "7.36", "7.36a", "7.36b", "7.36c", 
    "7.37", "7.37b", "7.37c", "7.37d"
]

for p in list_patches:
# URL of the Dota2 API endpoint
    url = f'https://www.dota2.com/datafeed/patchnotes?version={p}&language=english'
    response = requests.get(url)
    data = response.json()
    # Save into a file
    # Save the JSON response to a file for JSONLoader to read
    with open(f"./patchnotes/{p}.json", "w") as f:
        import json
        json.dump(data, f)