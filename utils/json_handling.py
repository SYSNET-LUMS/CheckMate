import os 
import re
import json

from config.globals import ENTITIES
from utils.utils import Dprint


def loadEntities(): #Cat 3

    global ENTITIES

    function_folder = "functions"
    entries = os.listdir(function_folder)
    enitiestFiles = []

    for file in entries:
        if re.search("_entities.json", file): #This check just to make sure that the we dont full json objects form non _entites files that may exist in the functions folder.
            enitiestFiles.append(file)

            with open(os.path.join("functions/", file), "r") as openfile:
                thisFile = json.loads(openfile.read())

                ENTITIES += thisFile

    return ENTITIES

def joinJsonFiles(directory, name_template, output_filename): #Cat 3
    combined_data = []
    if not output_filename.endswith(".json"):
        Dprint("Output file name must end with .json")
        return None

    # List all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is a JSON file and contains the name_template
        if filename.endswith(".json") and name_template in filename:
            file_path = os.path.join(directory, filename)

            # Open and read the JSON file
            with open(file_path, "r") as file:
                data = json.load(file)
                # Ensure that the JSON data is a list
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)

    # Define the output file path
    output_file = os.path.join(directory, output_filename)

    # Write the combined data to a new JSON file
    with open(output_file, "w") as file:
        json.dump(combined_data, file, indent=4)

    Dprint(f"Combined JSON file created at: {output_file}")