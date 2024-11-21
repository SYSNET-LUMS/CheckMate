from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import (
    ChatPromptTemplate,
)

import dotenv
import os
import json
from colorama import Fore, Back, Style

from config.globals import (
    ENTITIES,
    GLOBAL_CONTEXT
)

from config.config import (
    PRINT_LLM_CONVO,
    API_NAME,
)

from utils.utils import(
    getFunctionData,
    formatMessageForHistory,
    formatConversation,
    writeFunctionsToJson,
    printStructuredJson,
    getCodeBase,
    parseTargetFunctions,
)

from utils.compiler import(
    compileTest
)

#  Load the API key and model from the .env file
dotenv.load_dotenv()
model = os.getenv("LLM_MODEL")

# Initialize the language model
llmLangChain = None
if API_NAME == "OpenAI":
    api_key = os.getenv("OPENAI_API_KEY")
    llmLangChain = ChatOpenAI(api_key=api_key, temperature=0, model=model)
elif API_NAME == "Anthropic":
    api_key = os.getenv("ANTHROPIC_API_KEY")
    llmLangChain = ChatAnthropic(api_key=api_key,model=model, temperature=0)

print(model)

if llmLangChain == None:
    print("Error no API NAME specified in config.py. Exiting")
    quit()

def purposeIdentificationFunction(
        this_function, 
        this_context, 
        purposePrompt                              
    ):

    global PRINT_LLM_CONVO

    chain = llmLangChain
    function_data = getFunctionData(ENTITIES, this_function)['completeFunction']

    def get_human_prompt_purpose():
        common_prompt = {
            'function_name': this_function,
            'function_code': function_data
        }
        context_prompt = purposePrompt.format(context=this_context, **common_prompt)
        no_context_prompt = purposePrompt.format(**common_prompt)
        return context_prompt, no_context_prompt

    def log_conversation(human_prompt):
        if PRINT_LLM_CONVO:
            print(f"\n\n ---------------------- Purpose Identification Prompt ---------------------- \n\n{human_prompt}\n\n")

    function_purpose = ""
    output_purpose = ""

    while True:
        try:    

            human_prompt_purpose, no_context_human_prompt = get_human_prompt_purpose()
            log_conversation(human_prompt_purpose)

            output_purpose = chain.invoke(input=human_prompt_purpose)

            if PRINT_LLM_CONVO:
                print(Fore.CYAN + str(output_purpose.content))
                print(Style.RESET_ALL)

            function_purpose = output_purpose.content
            break
        except Exception as error:
            if PRINT_LLM_CONVO:
                print(Fore.RED + str(output_purpose))
                print(Style.RESET_ALL)
            
            print(error)

    this_purpose_convo = [
        formatMessageForHistory(no_context_human_prompt, False),
        formatMessageForHistory(output_purpose, True)
    ]
    return this_purpose_convo


def annotateFunction(
        this_function, 
        this_context, 
        annotationPrompt,
        output_format_instructions,
        output_format,
    ):

    global PRINT_LLM_CONVO
    # global ANNOTATION_SCRIPT

    chain = annotationPrompt | llmLangChain | output_format
    function_data = getFunctionData(ENTITIES, this_function)['completeFunction']

    def get_human_prompt_anno():        
        # Shared parameters
        common_prompt = {
            'function_name': this_function,
            'function_code': function_data,
            'add_error': this_error,
            'output_format': output_format_instructions,
        }

        # Generate the prompts
        context_prompt = annotationPrompt.format(context=context, **common_prompt)
        no_context_prompt = annotationPrompt.format(**common_prompt)

        return context_prompt, no_context_prompt

    def log_conversation(human_prompt):
        if PRINT_LLM_CONVO:
            print(f"\n\n ----------------------  Annotation Prompt  ---------------------- \n\n{human_prompt}\n\n")

    output_annotation = ""
    this_error = ""
    last_error_convo = []

    while True:
        try:    

            # Generate input prompt
            context = this_context + last_error_convo
            human_prompt_anno, no_context_human_prompt = get_human_prompt_anno()
            log_conversation(no_context_human_prompt)

            # Send API call for Annotation
            output_annotation = chain.invoke(input=human_prompt_anno)

            if PRINT_LLM_CONVO:
                print(Fore.YELLOW + str(output_annotation))
                print(Style.RESET_ALL)

            break
        except Exception as error:
            if PRINT_LLM_CONVO:
                print(Fore.RED + str(output_annotation))
                print(Style.RESET_ALL)

            last_error_convo = [
                formatMessageForHistory(no_context_human_prompt, False),
                formatMessageForHistory(output_annotation, True)
            ]
            this_error = f"There was a format error in your previous response. {error}. Make sure to follow the JSON format stated.\n\n"
            print(error)

    this_annotation_convo = [
        formatMessageForHistory(no_context_human_prompt, False),
        formatMessageForHistory(output_annotation, True)
    ]
    return this_annotation_convo


def planStepFunction(
        this_function, 
        this_context, 
        planningPrompt,
        platform_architecure
    ):

    global PRINT_LLM_CONVO

    chain = llmLangChain

    this_error = ""

    def get_human_prompt_planing(context):
        # Cache function data

        # Shared parameters
        common_prompt = {
            'function_name': this_function,
            'platform_architecture': platform_architecure,
            'add_error': this_error,
        }

        # Generate the prompts
        context_prompt = planningPrompt.format(context=context, **common_prompt)
        no_context_prompt = planningPrompt.format(**common_prompt)

        return context_prompt, no_context_prompt

    def log_conversation(human_prompt):
        if PRINT_LLM_CONVO:
            print(f"\n\n ----------------------  Planning Prompt  ---------------------- \n\n{human_prompt}\n\n")

    output_plan = ""
    last_error_convo = []

    while True:
        try:    

            # Generate input prompt
            context = this_context + last_error_convo
            human_prompt, no_context_human_prompt = get_human_prompt_planing(context)
            log_conversation(no_context_human_prompt)

            # Send API call for Planning step
            output_plan = chain.invoke(input=human_prompt)

            if PRINT_LLM_CONVO:
                print(Fore.YELLOW + str(output_plan.content))
                print(Style.RESET_ALL)

            break
        except Exception as error:
            if PRINT_LLM_CONVO:
                print(Fore.RED + str(output_plan.content))
                print(Style.RESET_ALL)

            last_error_convo = [
                formatMessageForHistory(no_context_human_prompt, False),
                formatMessageForHistory(output_plan, True)
            ]
            this_error = f"There was a format error in your previous response. {error}. Make sure to follow the JSON format stated.\n\n"
            print(error)

    this_convo = [
        formatMessageForHistory(no_context_human_prompt, False),
        formatMessageForHistory(output_plan, True)
    ]
    return this_convo

def approximateFunction(
        this_function,
        this_context, 
        approximation_prompt,
        prev_err
    ):

    global PRINT_LLM_CONVO
    print("LLL: ",PRINT_LLM_CONVO)
    # global APPROXIMATION_SCRIPT
    chain = llmLangChain

    def get_human_prompt_approx(context):
        common_prompt = {
            "function_name": this_function,
            "add_error": this_error,
        }
        context_prompt = approximation_prompt.format(context=context, **common_prompt)
        no_context_prompt = approximation_prompt.format(**common_prompt)
        return context_prompt, no_context_prompt

    def log_conversation(human_prompt):
        if PRINT_LLM_CONVO:
            print(f"\n\n ---------------------- Approximation Prompt ---------------------- \n\n{human_prompt}\n\n")


    last_error = []
    this_error = prev_err
    output_approximated = ""

    while True:
        try:
            context = this_context + last_error
            human_prompt_approx, no_context_human_prompt = get_human_prompt_approx(context)
            log_conversation(human_prompt_approx)

            output_approximated = chain.invoke(input=human_prompt_approx)

            if PRINT_LLM_CONVO:
                print(Fore.GREEN + str(output_approximated.content))
                print(Style.RESET_ALL)

            # Compilation error check handeling
            break

        except Exception as error:
            if PRINT_LLM_CONVO:
                print(Fore.YELLOW + str(output_approximated))
                print(Style.RESET_ALL)

            last_error = [
                formatMessageForHistory(no_context_human_prompt, False),
                formatMessageForHistory(output_approximated.content, True)
            ]
            this_error = f"There was a format error in your previous response. {error}. Make sure to follow the JSON format stated.\n\n"
            print(error)

    this_convo = [
        formatMessageForHistory(no_context_human_prompt, False),
        formatMessageForHistory(output_approximated.content, True)
    ]
    return this_convo


def convertJson(
        this_function,
        this_context,
        convert_json_prompt,
        output_format_parser
    ):

    global PRINT_LLM_CONVO
    chain = llmLangChain | output_format_parser
    this_error = ""

    def get_human_prompt_json(context):
        common_prompt = {
            'add_error': this_error,
            'output_instuctions': output_format_parser.get_format_instructions()
        }

        context_prompt = convert_json_prompt.format(context=context, **common_prompt)
        no_context_prompt = convert_json_prompt.format(**common_prompt)

        return context_prompt, no_context_prompt
    
    def log_conversation(human_prompt):
        if PRINT_LLM_CONVO:
            print(f"\n\n ---------------------- JSON Conversion Prompt ---------------------- \n\n{human_prompt}\n\n")

    def extract_or_default(output, key, default='[]'):
        return output.get(key, default)

    last_error = []
    this_error = ""
    output_approximated = ""

    while True:
        try:
            context = this_context + last_error
            human_prompt_json, no_context_prompt = get_human_prompt_json(context)
            log_conversation(no_context_prompt)

            output_approximated = chain.invoke(input=human_prompt_json)

            if PRINT_LLM_CONVO:
                print(Fore.GREEN + str(output_approximated))
                print(Style.RESET_ALL)

            function_code_approximated = output_approximated['approxmated_code']
            knobs_variables_list = extract_or_default(output_approximated, 'knob_variables')
            knobs_variables_ranges = extract_or_default(output_approximated, 'knob_ranges')
            knobs_variables_step_size = extract_or_default(output_approximated, 'knob_increments')

            approximate_function = {
                "functionName": this_function,
                "completeFunction": function_code_approximated,
                "knobVariables": knobs_variables_list,
                "knobRanges": knobs_variables_ranges,
                "knobStepSize": knobs_variables_step_size,
            }

            break

        except Exception as error:
            if PRINT_LLM_CONVO:
                print(Fore.YELLOW + str(output_approximated))
                print(Style.RESET_ALL)

            last_error = [
                formatMessageForHistory(no_context_prompt, False),
                formatMessageForHistory(output_approximated, True)
            ]
            this_error = f"There was a format error in your previous response. {error}. Make sure to follow the JSON format stated.\n\n"
            print(error)

    this_convo = [
        formatMessageForHistory(no_context_prompt, False),
        formatMessageForHistory(output_approximated, True)
    ]
    return this_convo, approximate_function

def approximateFunctionOLD(
        approximated_functions_dict, 
        this_function, 
        this_context, 
        approximation_prompt,
        output_parser, 
        function_code_annotated, 
        output_format_instructions_apx
    ):

    global PRINT_LLM_CONVO
    # global APPROXIMATION_SCRIPT
    chain = approximation_prompt | llmLangChain | output_parser

    def get_human_prompt_approx():
        return approximation_prompt.format(
            annotated_code=function_code_annotated,
            add_error=this_error,
            output_format=output_format_instructions_apx
        )

    def log_conversation(context, human_prompt):
        if PRINT_LLM_CONVO:
            to_print_prompt = formatConversation(context + [formatMessageForHistory(human_prompt, False)])
            print(f"\n\n ---------------------- Approximation Prompt ---------------------- \n\n{to_print_prompt}\n\n")

    def extract_or_default(output, key, default='[]'):
        return output.get(key, default)

    last_error = []
    this_error = ""
    output_approximated = ""

    while True:
        try:
            context = this_context + last_error
            human_prompt_approx = get_human_prompt_approx()
            log_conversation(context, human_prompt_approx)

            output_approximated = chain.invoke(input={
                'output_format': "\n The output format should be in JSON \n" + output_format_instructions_apx,
                'annotated_code': function_code_annotated,
                'add_error': this_error,
                'context': context
            })

            if PRINT_LLM_CONVO:
                print(Fore.GREEN)
                printStructuredJson(output_approximated)
                print(Style.RESET_ALL)

            function_code_approximated = output_approximated['approxmated_code']
            knobs_variables_list = extract_or_default(output_approximated, 'knob_variables')
            knobs_variables_ranges = extract_or_default(output_approximated, 'knob_ranges')
            knobs_variables_step_size = extract_or_default(output_approximated, 'knob_increments')

            approximated_functions_dict[this_function] = {
                "functionName": this_function,
                "completeFunction": function_code_approximated,
                "knobVariables": knobs_variables_list,
                "knobRanges": knobs_variables_ranges,
                "knobStepSize": knobs_variables_step_size,
            }

            writeFunctionsToJson(approximated_functions_dict, 'approximated_functions/apx')

            compile_error = compileTest(function=this_function)
            if compile_error:
                last_error = [
                    formatMessageForHistory(human_prompt_approx, False),
                    formatMessageForHistory(output_approximated, True)
                ]
                this_error = f"This error occurred at compile time: \n{compile_error}\n"
                continue

            break

        except Exception as error:
            if PRINT_LLM_CONVO:
                print(Fore.YELLOW + str(output_approximated))
                print(Style.RESET_ALL)

            last_error = [
                formatMessageForHistory(human_prompt_approx, False),
                formatMessageForHistory(output_approximated, True)
            ]
            this_error = f"There was a format error in your previous response. {error}. Make sure to follow the JSON format stated.\n\n"
            print(error)

    return output_approximated, human_prompt_approx




rtl_chat_histroy = []

def generateExpandMakeFile(
        files,
        compiler_error=""
    ):
    

    print("Sending PDG Makefile prompt...")


    next_prompt = ""
    with open('prompts/compilerRTL.txt','r') as file: # Move reading file to init file
        next_prompt = file.read()

    prompt = ChatPromptTemplate.from_messages([
    ('placeholder', '{conversation}'),
    ('human', next_prompt)
    ])
    
    print("Sending PDG Makefile prompt...")
    chain = prompt | llmLangChain
    output = chain.invoke(input={'conversation':rtl_chat_histroy,'compiler_error':compiler_error,'files_list':files})
    print("Generated PDG Makefile")


    rtl_chat_histroy.append(formatMessageForHistory(prompt.format(files_list=files,compiler_error=compiler_error),False))
    rtl_chat_histroy.append(formatMessageForHistory(output.content,True))
    
    print("\n\n\n ------ Prompt: ------ \n\n")
    print(prompt.format(files_list=files,compiler_error=compiler_error,conversation=rtl_chat_histroy))
    print("\n\n\n ------ LLM Responce: ------ \n\n")
    print(output.content)
    return output.content

def findTargetFunctions(function_target_prompt):

    global PRINT_LLM_CONVO
    global GLOBAL_CONTEXT

    # Step 0: Check if 'code_summary' and 'target_functions' are present in 'logs/somefile.txt'
    file_path = 'logs/code_base_info.txt'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            if 'code_summary' in data and 'target_functions' in data:
                print("Loading cached data from logs/code_base_info.txt")
                return data['target_functions'], data['code_summary']


    # Step 1: Gather context and codebase
    context = GLOBAL_CONTEXT.copy()
    code_base = getCodeBase()

    # Step 2: Format the initial prompt with the provided context and codebase
    formatted_prompt = function_target_prompt.format(
        context=context,
        code_base=code_base,
    )

    # Step 3: Invoke LLM for target functions
    output = invokeLLM(formatted_prompt, llmLangChain)
    if PRINT_LLM_CONVO:
        print("--- Target_function: ---\n \n")
        print(output)   

    # Step 4: Parse the target functions from the LLM's output
    target_functions = parseTargetFunctions(output)

    # Step 5: Update context with the function target prompt and LLM's output
    context += formatMessageForHistory(function_target_prompt.format(code_base=code_base), False)
    context += formatMessageForHistory(output, True)

    # Step 6: Read the code summary prompt from an external file
    with open('prompts/code_summary.txt', 'r') as file: # Move read to init file
        summary_prompt = file.read()

    # Step 7: Create a chat prompt template using the updated context and code summary prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        ('placeholder', '{context}'),
        ('human', summary_prompt)
    ])

    # Step 8: Format the prompt with the current context
    final_prompt = chat_prompt.format(
        context=context
    )

    # Step 9: Invoke LLM to get a code summary
    code_summary = invokeLLM(final_prompt, llmLangChain)
    if PRINT_LLM_CONVO:
        print("--- code_summary: ---\n \n")
        print(code_summary)

    # Step 10: Save 'code_summary' and 'target_functions' to 'logs/code_base_info.txt'
    data_to_save = {
        'code_summary': code_summary,
        'target_functions': target_functions
    }
    with open(file_path, 'w') as file:
        json.dump(data_to_save, file)

    # Step 11: Return the parsed target functions and code summary
    return target_functions, code_summary


def invokeLLM(input, invoking_obj):

    output = ""
    try:
        output = invoking_obj.invoke(input=(input))
    except Exception as error:
        print("While attempting to invoke LLM encoundered error: ",error)
        return None
    
    return output.content
