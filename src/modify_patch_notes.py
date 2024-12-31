import os
import json
import numpy as np

folder_path = '../patchnotes'
list_patch_notes = os.listdir(folder_path)

def add_default_hero_values(data):
    for hero in data.get("heroes", []):
        # Add default talent_notes if not present
        if "talent_notes" not in hero:
            hero["talent_notes"] = ["No updates/changes in talents"]
        else:
            for talent in hero["talent_notes"]:
                if "note" in talent:
                    talent["note"] = "Changes in talent: " + talent["note"]

        if "hero_notes" not in hero:
            hero["hero_notes"] = ["No updates/changes in base stats"]
        else:
            for hero_note in hero["hero_notes"]:
                if "note" in hero_note:
                    hero_note["note"] = "Changes in hero's base or general stats: " + hero_note["note"]

        if "abilities" not in hero:
            hero["abilities"] = []
        else:
            for ability in hero.get("abilities", []):
                for ability_note in ability.get("ability_notes", []):
                    if "note" in ability_note:
                        ability_note["note"] = "Changes in ability: " + ability_note["note"]



        # Handle subsections for facets
        if "subsections" in hero:
            for subsection in hero["subsections"]:
                facet_title = subsection.get("title", "")

                # Handle abilities if present
                for ability in subsection.get("abilities", []):
                    hero["abilities"].append({
                        "ability_id": ability.get("ability_id", np.nan),
                        "ability_notes": [
                            {**note, "facet": facet_title} for note in ability.get("ability_notes", [])
                        ]
                    })

                # Handle general_notes if present
                for note in subsection.get("general_notes", []):
                    hero["hero_notes"].append({**note, "facet": facet_title})

            # Remove subsections after processing
            del hero["subsections"]

for patch_note in list_patch_notes:
    # Load original
    with open(f"../patchnotes/{patch_note}", 'r') as file:
        json_data = json.load(file)
    add_default_hero_values(json_data)
    # Save the modified
    with open(f"../patchnotes_modified/{patch_note}", 'w') as f:
        json.dump(json_data, f)
        print(f"Modified {patch_note}")
