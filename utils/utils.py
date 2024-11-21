import os
import subprocess
import json
import shutil
import re
import pandas as pd
import ast


from config.config import APPROXIMATION_CONTEXT, GIVE_FORMAT_EXAMPLES, GIVE_LOOP_PERF_EXMAPLES
from config.globals import (
    GLOBAL_CONTEXT,
    TARGET_FILES,
    ENTITIES,
    APPROXIMATION_FORMAT_EXAMPLES,
    CHAT_HISTORY,
    LOOP_PERF_EXAMPLES
)

''' 
    Functuion catagories

    1.  Innitalization tasks - Prompts
    2.  Innitalization tasks - Target Dir
    3.  JSON Handeling - 
    4.  Helper
    5.  PDG
    6.  Context handeling
'''


def loadTargetFiles(directory): #Cat 2 - 

    global TARGET_FILES

    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith((".c", ".cpp")):
                TARGET_FILES.append(os.path.join(filename))

    return TARGET_FILES


def loadGlobalContext(): #Cat 1 -

    global GLOBAL_CONTEXT

    system_prompt = ""
    with open("Prompts/system_prompt.txt", "r") as file:
        system_prompt = file.read()

    GLOBAL_CONTEXT.append(("system", system_prompt))

    if APPROXIMATION_CONTEXT != 0:

        apx_techniques_summary = ""
        with open("prompts/approximation_techniques.txt", "r") as file:
            apx_techniques_summary = file.read()

        summary_converstaion = [
            (
                "human",
                "Give me a list of code approximations techniques (approximate computing)",
            ),
            ("ai", apx_techniques_summary),
        ]
        GLOBAL_CONTEXT += summary_converstaion


def parseFunctions(): #Cat 2 -
    for file_name in TARGET_FILES:
        command = [
            "python3",
            "compilation_testing/Tools/LSPextractor_all_entities.py",
            "target/" + file_name,
        ]

        # Execute the command
        subprocess.run(command, capture_output=True, text=True)


def findFileOfFunc(func_name, files): #Cat 4
    for file_name in files:
        base_name = os.path.splitext(file_name)[0]
        json_file_path = f"functions/{base_name}_entities.json"

        try:
            with open(json_file_path, "r") as file:
                parse_function_data = json.load(file)
                # Now function_data contains the JSON data which you can process
        except:
            continue
        
        unique_functions = {
            function["functionName"] for function in parse_function_data
        }
        if func_name in unique_functions:
            return file_name


def copyFiles(source_path, destination_path): #Cat 4
    # Ensure the destination directory exists, if not, create it
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # Walk through all directories and files in the source directory
    for dirpath, dirnames, filenames in os.walk(source_path):
        # Calculate relative path to the destination
        relative_path = os.path.relpath(dirpath, source_path)
        dest_dir = os.path.join(destination_path, relative_path)

        # Ensure each directory exists in the destination path
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Copy each file
        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            dest_file = os.path.join(dest_dir, filename)
            shutil.copy2(src_file, dest_file)
            # print(f"Copied {src_file} to {dest_file}")


def writeFunctionsToJson(func_dict, file_path): #Cat 3  (Add base_file_path arg)
    # List to hold formatted data
    data = []

    # Base file path (assuming all functions go into the same directory and file type)
    base_file_path = "target/"
    file_extension = ".c"

    # Process each function name and its corresponding function code
    for function_name, results in func_dict.items():
        # Each function's data is a dictionary
        file_name = findFileOfFunc(function_name, TARGET_FILES)

        try:
            results["filePath"] = f"{base_file_path}{file_name}"
        except:
            pass

        func_data = [results]
        # data.append(func_data)

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        # Write the list of dictionaries to a JSON file
        with open(file_path + f"_{function_name}.json", "w") as file:
            json.dump(func_data, file, indent=4)


def loadEntities(): #Cat 3 -

    global ENTITIES

    function_folder = "functions"
    entries = os.listdir(function_folder)
    enitiestFiles = []

    for file in entries: # This check is not necessary but it is a safe guard if debugging flags are added to LSPextractor call
        if re.search("_entities.json", file):
            enitiestFiles.append(file)

            with open(os.path.join("functions/", file), "r") as openfile:
                thisFile = json.loads(openfile.read())

                ENTITIES += thisFile

    return ENTITIES


def createPDG(): #Cat 5 -
    # Generate PDG
    command = ["python3", "dependency_graphs/runAll.py"]

    subprocess.run(command)

    # Load PDG and sort

    PDG = pd.read_json("dependency_graphs/adj_mat.json")

    with open("dependency_graphs/topological_order.json", "r") as file:
        topological_order = json.load(file)

    try:
        topological_order.remove("main")
    except:
        pass

    return PDG, topological_order

# PDG Function needed
def getNodeParent(node, PDG): #Cat 5
    """
    Takes a Node a returns a list of parent node(functions)
    """
    edges = PDG[node]
    parent = []
    for i, edge in enumerate(edges):
        if edge:
            parent.append(edges.index[i])

    return parent


def getConversationHistory(function_list, chat_history): #Cat 6 -
    manufactured_history = []
    for function in function_list:
        try:
            manufactured_history += chat_history[function]
        except:
            print("A converstation that does not exist was attempted to be added")
            continue

    return manufactured_history


def formatMessageForHistory(content, isAI): #Cat 4
    if isAI:
        return ("ai", f"""{content}""")
    else:
        return ("human", f"""{content}""")


def getFunctionData(list_function_data, toFind): #Cat 4

    for function_data in list_function_data:

        if function_data["functionName"] == toFind:

            return function_data
    # Return None if no match is found
    return None


def loadFormatExamples(): #Cat 1 -

    global APPROXIMATION_FORMAT_EXAMPLES

    dummy_annotation = []
    dummy_approximation = []
    with open("prompts/FewShotExamples/annotationHuman.txt", "r") as file:
        dummy_annotation.append(formatMessageForHistory(file.read(), False))

    with open("prompts/FewShotExamples/annotationAi.txt", "r") as file:
        dummy_annotation.append(formatMessageForHistory(file.read(), True))

    with open("prompts/FewShotExamples/approximationHuman.txt", "r") as file:
        dummy_approximation.append(formatMessageForHistory(file.read(), False))

    with open("prompts/FewShotExamples/approximationAi.txt", "r") as file:
        dummy_approximation.append(formatMessageForHistory(file.read(), True))

    APPROXIMATION_FORMAT_EXAMPLES = dummy_annotation + dummy_approximation


def manufacturerContext(PDG, this_function): #Cat 6 -

    global APPROXIMATION_FORMAT_EXAMPLES
    global CHAT_HISTORY
    global GIVE_FORMAT_EXAMPLES

    parent_entities = getNodeParent(this_function, PDG)
    # print("\n\n\n\n\n\n\n")
    # print(parent_entities)
    parent_context = getConversationHistory(parent_entities, CHAT_HISTORY)
    # print("\n\n\n\n\n\n\n")
    # print(parent_context)
    this_context = GLOBAL_CONTEXT
    # print("\n\n\n\n\n\n\n")
    # print(this_context)

    if GIVE_LOOP_PERF_EXMAPLES:
        this_context += LOOP_PERF_EXAMPLES
    if GIVE_FORMAT_EXAMPLES:
        this_context += APPROXIMATION_FORMAT_EXAMPLES

    this_context +=  parent_context
    return this_context


def formatConversation(steps): #Cat 4
    """
    Format a list of conversation steps with the given values.

    Args:
    steps (list of tuples): List of (role, message) tuples.

    Returns:
    str: Formatted conversation.
    """

    # Define a mapping from role to label
    role_to_label = {"system": "System", "human": "Human", "ai": "AI"}

    # Initialize an empty list to hold formatted lines
    formatted_lines = []

    # Iterate over the steps
    for role, message in steps:
        # Append the formatted message with the role label
        formatted_lines.append(f"{role_to_label[role]}: {message}")

    # Join the formatted lines into a single string
    formatted_conversation = "\n".join(formatted_lines)

    return formatted_conversation


def printStructuredJson(json_obj): #Cat 4
    """
    Print a JSON object in a structured, indented manner.

    Args:
    json_obj (dict): JSON object to be printed.
    """
    structured_json = json.dumps(json_obj, indent=4)
    print(structured_json)


def joinJsonFiles(directory, name_template, output_filename): #Cat 3 -
    combined_data = []
    if not output_filename.endswith(".json"):
        print("Output file name must end with .json")
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

    print(f"Combined JSON file created at: {output_file}")


def loadAndProcessJsonApxFile(file_path): # Unused
    with open(file_path, "r") as file:
        data = json.load(file)

    # Process each item in the data list
    for item in data:
        item["knobVariables"] = json.loads(item["knobVariables"])
        item["knobRanges"] = json.loads(item["knobRanges"])
        item["knobStepSize"] = json.loads(item["knobStepSize"])

    return data


def getAppName(): #Cat 4
    """
    Retrieves the application name from the 'target/application.txt' file.

    Returns:
        str: The application name.
    """
    app_name = ""
    with open("target/application.txt", "r") as file:
        app_name = file.read()

    return app_name

def loadLoopPerfExamples(): #Cat 1 -
    with open("prompts/FewShotExamples/loopPerforationExamples.txt",'r') as file:
        LOOP_PERF_EXAMPLES.append(formatMessageForHistory(file.read(),False))
    
    ai_message = "Got it. When applying loop perforation, I'll add to the code in a truncation style approximation to the condition step of the loop."
    LOOP_PERF_EXAMPLES.append(formatMessageForHistory(ai_message,True))

def getFilesList(directory): #Cat 4 -
    files = []
    
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            files.append(filename)
    
    return 

def getCodeBase(): #Cat 4 -N
    all_files = ""
    
    for file in TARGET_FILES:
        file_path = os.path.join("target", file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_files += f.read() + "\n\n\n"  # Append file content and add a newline between files
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"An error occurred while reading {file_path}: {e}")
    
    return all_files

def parseTargetFunctions(text):
    
    pattern = re.compile(r'\{.*?\}', re.DOTALL)
    
    # Find the first match (the dictionary in the text)
    match = pattern.search(text)
    
    if match:
        dict_string = match.group(0)
        
        # Safely evaluate the string to convert it into a Python dictionary
        extracted_dict = ast.literal_eval(dict_string)
        return extracted_dict
    else:
        return None