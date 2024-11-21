# Language Server Protocol
import subprocess
import json
import urllib.parse
import sys
import os

# LSP init and api calls
def start_clangd():
    process = subprocess.Popen(
        ['clangd'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    return process

def send_request(process, request):
    message = json.dumps(request)
    content_length = len(message)
    process.stdin.write(f"Content-Length: {content_length}\r\n\r\n{message}")
    process.stdin.flush()

def read_response(process):
    headers = {}
    while True:
        line = process.stdout.readline().strip()
        if not line:
            break
        key, value = line.split(": ", 1)
        headers[key] = value
    if 'Content-Length' in headers:
        length = int(headers['Content-Length'])
        body = process.stdout.read(length)
        return json.loads(body)
    return None

def initialize_clangd(process):
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "processId": None,
            "rootUri": None,
            "capabilities": {}
        }
    }
    send_request(process, init_request)
    return read_response(process)

def did_open(process, file_path, content):
    uri = path_to_uri(file_path)
    open_request = {
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {
            "textDocument": {
                "uri": uri,
                "languageId": "c",
                "version": 1,
                "text": content
            }
        }
    }
    send_request(process, open_request)
    return read_response(process)

def get_document_symbols(process, uri):
    document_symbols_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "textDocument/documentSymbol",
        "params": {
            "textDocument": {
                "uri": uri
            }
        }
    }
    send_request(process, document_symbols_request)
    return read_response(process)

def path_to_uri(file_path):
    return 'file://' + urllib.parse.quote(file_path)


# LSP Extractor

def extract_function_content(file_path, functions):
    # Convert URI to a normal file path
    file_path = urllib.parse.unquote(file_path.replace('file://', ''))
    
    function_contents = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    for function in functions:
        start_line = function['location']['range']['start']['line']
        end_line = function['location']['range']['end']['line']
        
        # Extract the content from the start line to the end line
        content = ''.join(lines[start_line:end_line + 1]).strip()

        # Using the function name as the key in the dictionary to manage updates
        function_contents[function['name']] = {
            "filePath": function['location']['uri'],
            "functionName": function['name'],
            "completeFunction": content
        }
    
    # Convert the dictionary back to a list of dictionaries as the function output
    return list(function_contents.values())

def concatenate_functions(json_data):
    # Parse the JSON data if it's a string, otherwise assume it's already a Python object
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Extract 'completeFunction' from each entry and join them into one string
    concatenated_functions = "\n".join(entry['completeFunction'] for entry in data)
    
    return concatenated_functions

def lsp_extractor(file_path, positions_file_flag=False, print_flag=False):
    """
    Extracts information from a file using LSP (Language Server Protocol).
    
    Parameters:
    - file_path (str): The path to the file to be parsed.
    - positions_file_flag (bool): If True, creates an entity positions JSON file (documentSymbol dump).
    - print_flag (bool): If True, prints all LSP request outputs on the terminal.
    """
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    try:
        file_content = open(file_path, 'r').read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return 
    
    process = start_clangd() # Starts Connection with clangd server
    init_req = initialize_clangd(process)
    if print_flag:
        print("Initialization response:", init_req)
        print("\n\n ----------- \n\n")

    open_req = did_open(process, file_path, file_content)
    if print_flag:
        print("didOpen response: ", open_req) # did Open confirmation
        print("\n\n ----------- \n\n")

    symbols_response = get_document_symbols(process, path_to_uri(file_path))
    if print_flag:
        print("Symbols response: ",symbols_response)
        print("\n\n ----------- \n\n")

    symbols_response = [item for item in symbols_response["result"]] 

    # Create 'functions' directory if it does not exist
    if not os.path.exists("functions"):
        os.makedirs("functions")

    if positions_file_flag:
        with open(f"functions/{base_name}_entityPositions.json", "w") as outfile:
            json.dump(symbols_response, outfile, indent=2)
    
    # Terminate the clangd process
    process.terminate()
    process.wait()

    extracted_entities = extract_function_content(file_path, symbols_response)

    # Save extracted entities
    with open(f"functions/{base_name}_entities.json", "w") as outfile:
        json.dump(extracted_entities, outfile, indent=2)


# LSP Patcher

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def lsp_patcher(dir_path, json_file_name):
    """
    Patches files in a directory using approximated code provided in a JSON file.

    Parameters:
    - dir_path (str): The path of the directory containing the files.
    - json_file_name (str): The name of the JSON file with the approximated code.
    """
    json_file_path = os.path.join(dir_path, json_file_name)

    try:
        with open(json_file_path, 'r') as f:
            approximated_code = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return

    # Group approximated functions by file base name
    functions_by_file = {}
    for item in approximated_code:
        # Extract only the base name of the file from the filePath field
        base_name = os.path.basename(item['filePath'])
        file_path = os.path.join(dir_path, base_name)
        if file_path not in functions_by_file:
            functions_by_file[file_path] = []
        functions_by_file[file_path].append(item)

    # Start the LSP (clangd) process
    process = start_clangd()
    initialize_clangd(process)
    print("LSP Server initialized")

    for file_path, functions in functions_by_file.items():
        file_lines = read_file_content(file_path)
        if file_lines is None:
            continue

        did_open(process, file_path, ''.join(file_lines))
        print(f"LSP didOpen request for {file_path}")

        symbols_response = get_document_symbols(process, path_to_uri(file_path))
        print(f"LSP documentSymbols request for {file_path}")

        function_symbols = [item for item in symbols_response["result"] if item.get("kind") == 12]
        symbol_map = {item['name']: item['location']['range'] for item in function_symbols}

        # Sort the functions by their position in reverse order so replacements don't affect the positions of others
        for approx_function in reversed(sorted(functions, key=lambda x: symbol_map[x['functionName']]['start']['line'] if x['functionName'] in symbol_map else -1)):
            func_name = approx_function['functionName']
            if func_name in symbol_map:
                start_line = symbol_map[func_name]['start']['line']
                end_line = symbol_map[func_name]['end']['line']

                # Get the indentation of the original function
                original_indent = ''
                if file_lines[start_line].strip():
                    original_indent = file_lines[start_line][:file_lines[start_line].index(file_lines[start_line].strip())]

                # Prepare the replacement code with proper indentation
                replacement_code = [original_indent + line for line in list(map(lambda x: x + "\n", approx_function['completeFunction'].split('\n')))]

                # Replace the original function code with the approximated function
                file_lines[start_line:end_line + 1] = replacement_code

        # Write the updated content back to the file
        new_content = ''.join(file_lines)
        with open(file_path, 'w') as f:
            f.write(new_content)

        print(f"Updated file {file_path} with approximated functions.")

    # Terminate the LSP process
    process.terminate()
    process.wait()
