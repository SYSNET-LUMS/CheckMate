import subprocess
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import shutil

from config.config import(
    API_NAME,
)
from utils.utils import (
    copyFiles,
    Dprint
)
from utils.data_structures import (
    FixedSizePairList
)
from lib.lsp import(
    lsp_patcher
)

load_dotenv()

def queryGPT(chat, chat_history, files_list, error_message=""): 

    # Move the prompt to init file
    """
    Query GPT to generate a Makefile based on the given file list and error message.

    :param chat: ChatOpenAI instance for communication
    :param chat_history: History of chat messages
    :param files_list: List of files in the target directory
    :param error_message: Error message from the previous compilation attempt
    :return: Generated Makefile content
    """
    query_template = """
    Given a list of files in the directory, output a Makefile to compile the application.

    Files: files = {files_list}

    Output only the Makefile content without any additional text. Your exact output will be directly pasted into the Makefile (so do not include any formatting like "```").

    The command that will be run is simply make main. Do not include the -Werror or -Wall flags. Make sure to include -DLOCAL_RUN flag.
    """

    prompt = ChatPromptTemplate.from_messages(
        [("placeholder", "{conversation}"), ("human", "{next_prompt}")]
    )

    query = query_template.format(files_list=files_list) + "\n" + error_message

    chain = prompt | chat

    response = chain.invoke(
        input={"conversation": list(chat_history), "next_prompt": query}
    )

    chat_history.add(formatMessageForHistory(query, False))
    chat_history.add(formatMessageForHistory(response.content, True))

    return response.content

def formatMessageForHistory(content, is_ai):
    """
    Format a message for chat history.

    :param content: Content of the message
    :param is_ai: Boolean indicating if the message is from AI
    :return: Tuple representing the message
    """
    return ("ai" if is_ai else "human", content)

def getFilesList(directory):
    """
    Get a list of files in the specified directory.

    :param directory: Target directory path
    :return: List of filenames in the directory
    """
    files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(filename)
    return files

def compileAndLog(target_path):
    """
    Attempt to compile the project and log the output.

    :param target_path: Path to the target directory
    :return: Tuple indicating success (bool) and error message (str)
    """
    try:
        with open(os.path.join(target_path, "compiler_log.txt"), "w") as output_file:
            subprocess.run(
                "make main",
                shell=True,
                check=True,
                cwd=target_path,
                stdout=output_file,
                stderr=subprocess.STDOUT,
            )
        return True, ""
    except subprocess.CalledProcessError as e:
        with open(os.path.join(target_path, "compiler_log.txt"), "r") as output_file:
            return False, output_file.read()

def generateMakeFile(target_path):

    global API_NAME

    chat = None
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("LLM_MODEL")
    if API_NAME == "OpenAI":
        api_key = os.getenv("OPENAI_API_KEY")
        chat = ChatOpenAI(api_key=api_key, temperature=0.7, model=model)
    elif API_NAME == "Anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        chat = ChatAnthropic(api_key=api_key,model=model)

    if not api_key or not model:
        Dprint("Error: Missing OpenAI API key or model in environment variables.")
        return

    chat_history = FixedSizePairList(5)

    files_list = getFilesList(target_path)

    response = queryGPT(chat, chat_history, files_list)

    makefile_path = os.path.join(target_path, "Makefile")

    for _ in range(10):
        with open(makefile_path, "w") as file:
            file.write(response)

        success, error_message = compileAndLog(target_path)
        
        if success:
            Dprint("Compilation successful\n")
            return 0

        response = queryGPT(chat, chat_history, files_list, error_message)

    Dprint("Compilation failed after 10 attempts\n")
    return 1

def compileTest(function): 
    # Functions will patch and compile the approximated function.
    path1 = "target"
    path2 = f"compilation_testing/ApxFiles_{function}"

    # for each key in approximated_functions_dict make a new folder

    copyFiles(path1, path2)

    apx_josn_file = f"apx_{function}.json"
    destination_file_path = os.path.join(path2, apx_josn_file)

    # Copy the file
    file_path = f"approximated_functions/apx_{function}.json"
    shutil.copy2(file_path, destination_file_path)

    lsp_patcher(path2,apx_josn_file)

    # Generate and test make file
    
    error_code = generateMakeFile(target_path=path2)

    if error_code == 1:
        with open(os.path.join(path2,"compiler_log.txt"), "r") as file:
            return file.read()

    return ""