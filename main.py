from langchain_core.output_parsers import JsonOutputParser
import shutil
import os
import subprocess
import ast
import pandas as pd
import argparse
from colorama import Back, Fore, Style

from config.config import (
    TEXT_PLANING,
)

from utils.initialization import (
    loadTargetFiles,
    loadGlobalContext,
    parseFunctions,
    getPromptTemplates,
    loadFormatExamples,
    loadLoopPerfExamples,
    loadCodeBaseSummary,
)

from utils.context import (
    manufacturerContext
)

from utils.json_handling import (
    loadEntities,
    joinJsonFiles
)

from utils.utils import (
    formatMessageForHistory,
    copyFiles,
    getAppName,
    writeFunctionsToJson
)

from utils.compiler import(
    compileTest
)

from utils.validator import(
    validateFunction
)

parser = argparse.ArgumentParser()

parser.add_argument("--bm_name", type=str, help="Benchmark app/ Evaluation app name", required=False)
parser.add_argument("--no_llm", action="store_true", help="include if you do not want to run LLM", required=False)

args = parser.parse_args()

if args.bm_name:
    print(f"Runing Benchmark App: {args.bm_name}")
    app_name = args.bm_name

alreadyRun = False
if args.no_llm:
    print(f"Using LLM prerun outputs...")
    alreadyRun = True

    def copy_prerun_outputs(bm_name):
        source_dir = os.path.join("llm-prerun", bm_name)
        if not os.path.exists(source_dir):
            print(f"Source directory does not exist: {source_dir}")
            return

        for folder in os.listdir(source_dir):
            src_path = os.path.join(source_dir, folder)
            dest_path = os.path.join(".", folder)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                print(f"Copied {folder} to current directory.")
            else:
                print(f"Skipping non-folder item: {folder}")

    copy_prerun_outputs(args.bm_name)
    

copyFiles(f"benchmark_applications/{app_name}/",f"eval-apps/{app_name}/")
# copy only the Makefile, .c and .h files in eval_apps/{app_name}/ to target/
def copyEvalAppSource(app_name, target_dir):
    subprocess.run(f"cp eval-apps/{app_name}/*.c {target_dir}",shell=True)
    subprocess.run(f"cp eval-apps/{app_name}/*.h {target_dir}",shell=True)
    subprocess.run(f"cp eval-apps/{app_name}/Makefile {target_dir}",shell=True)
    subprocess.run(f"cp eval-apps/{app_name}/application.txt {target_dir}",shell=True)

copyEvalAppSource(app_name, "target/")

from lib.llm import (
    purposeIdentificationFunction,
    annotateFunction,
    planStepFunction,
    approximateFunction,
    convertJson,
    findTargetFunctions,
)

from lib.bo import runBayesOpt

from lib.pdg import (
    initPDGGen,
    PDG,
    topological_order
)
from utils.models import AnnotateData, ApproximatedData
from config.globals import CHAT_HISTORY, PLATFORM_ARCHITECTURE
from config.config import GIVE_FORMAT_EXAMPLES, GIVE_LOOP_PERF_EXMAPLES
from utils.error_analyzer import generateGroundTruth
from utils.checkpoints import checkpointOrchestration
import csv

# ----------- README FOLLOW ALONG START HERE -----------

# LLM API initialization and PDF generation have already been done in lib/llm.py and lib/pdf.py respectively.


# Load filenames of target files

loadTargetFiles("target/")
platform_archi = PLATFORM_ARCHITECTURE

# Load global context (System prompt, approximation summry, few shot examples)
loadGlobalContext()
loadFormatExamples()
loadLoopPerfExamples()

# Parse target files to extract entities (functions, structs, global variables) and load them.
parseFunctions()
loadEntities()

# alreadyRun = True

if not alreadyRun:

    # Load and create prompt templates.
    prompts = getPromptTemplates()

    # Load output scheama.
    annotatedDataParser = JsonOutputParser(pydantic_object=AnnotateData)
    approximatedDataParser = JsonOutputParser(pydantic_object=ApproximatedData)

    # Load output format instructions for LLM.
    output_format_instructions_anno = annotatedDataParser.get_format_instructions()
    output_format_instructions_apx = approximatedDataParser.get_format_instructions()


    # Intialize approximated functions dirctrionary
    approximated_functions_dict = {}
    
    # Get list of target functions and code base summary
    target_functions, code_summary = findTargetFunctions(prompts["targetFunctionsPrompt"])

    # Load code_base summary
    loadCodeBaseSummary(code_summary)

    # Filter topological_order to only contain functions to be targeted as told by LLM
    filtered_topological_order = [] # Making new varaibale because topological_order may be used else where.
    print(target_functions)
    for function in topological_order:
        try:
            if target_functions[function] == "approximate" or target_functions[function] == "Approximate":
                filtered_topological_order.append(function)
        except:
            pass
    # Iterate over all functions
    for this_function in filtered_topological_order:
        print(Back.WHITE)
        print(Fore.BLACK)
        print("APPROXIMATING FUNCTION: " + this_function + "\n")
        print(Style.RESET_ALL)
        """
            Step 0: Parent Entities (Functions) Context
        """

        this_context = manufacturerContext(PDG, this_function)
        print("\n\n\n\n --- start \n\n")
        print(this_context)

        """
            Step 1: Identify this_function's purpose
        """

        # chain = purposePrompt | llmLangChain

        this_purpose_convo = purposeIdentificationFunction(
            this_function,
            this_context,
            prompts["purposePrompt"]
        )

        # Add purpose identification convo to history(context) object
        this_context = this_context + this_purpose_convo
        print("\n\n\n\n --- Perpose \n\n")
        print(this_context)

        """
            Step 2: Annotate the function
        """

        this_plan_anno_convo = None
        function_code_annotated = ""
        if TEXT_PLANING:
            this_plan_anno_convo = planStepFunction(
                this_function=this_function,
                this_context=this_context,
                planningPrompt=prompts["planningPrompt"],
                platform_architecure=platform_archi,
            )
        else:
            function_code_annotated, this_plan_anno_convo = annotateFunction(
                this_function, 
                this_context, 
                prompts["annotationPrompt"], 
                output_format_instructions_anno,
                annotatedDataParser,
            )


        # Add annotation convo to history(context) object
        this_context = this_context + this_plan_anno_convo # Add the annotation conversation context for approximation prompt
        print("\n\n\n\n --- Planning \n\n")
        print(this_context)

        err_approximation = ""
        while True:
            """
                Step 3: Approximate the function and test Compilation and Validation
            """
            
            this_approx_convo = approximateFunction(
                this_function=this_function,
                this_context=this_context,
                approximation_prompt=prompts["approximationPrompt"],
                prev_err=err_approximation
            )

            this_context = this_context + this_approx_convo

            """
                Step 4: Convert approximation to JSON format and Compile and Validate
            """

            this_approx_json_convo, approximate_function  = convertJson(
                this_context = this_context,
                convert_json_prompt = prompts["convertJsonPrompt"],
                this_function=this_function,
                output_format_parser=approximatedDataParser
            )

            this_context = this_context + this_approx_json_convo

            approximated_functions_dict[this_function] = approximate_function
            writeFunctionsToJson(approximated_functions_dict, 'approximated_functions/apx')

            err_comp = compileTest(this_function)

            # err_val = validateFunction(approximated_functions_dict[this_function])

            # if err_comp or err_val:
            if err_comp:
                
                err_approximation = prompts['errorPrompt'].format(this_err = err_comp)
                continue

            break

        """
            Step 5: Save conversation history
        """
        CHAT_HISTORY[this_function] = (
            this_purpose_convo 
            + this_plan_anno_convo
            + this_approx_convo
            + this_approx_json_convo
        )

        with open("logs/conv1.txt","a") as file:
            file.write(f"Function {this_function}" + "\n")
            file.write(str(approximated_functions_dict) + "\n")
            file.write(str(CHAT_HISTORY) + "\n")

print("\nAll functions approximated! \n\n")

# Read application.txt file from target/ and read the function name
# app_names = ["lqi-iclib", "stringsearch-iclib"]
# app_name = getAppName()
# app_name = app_names[0]

# Generate the ground truth
generateGroundTruth(app_name)
# quit()
copyFiles("target", "knob_tuning")
# quit()
if not alreadyRun:
    print(Back.YELLOW)
    print("ALL FUNCTIONS APPROXIMATED\n")
    print(Style.RESET_ALL)

    # Join all validated approximations
    joinJsonFiles("approximated_functions/", "apx", "apx_all.json")

    # Creat copy of target folder and add apx json file
    # copyFiles("target", "knob_tuning")

    file_path = f"approximated_functions/apx_all.json"
    destination_file_path = "knob_tuning"
    shutil.copy2(file_path, destination_file_path)

    # Search for a Makefile in compilation_testing/ and copy it in knob_tuning/. The Makefile is in any of the subdirectories of compilation_testing/
    os.system("find compilation_testing/ -name Makefile -exec cp {} knob_tuning/ \;")
    os.system("find compilation_testing/ -name Makefile -exec cp {} target/ \;")

# quit()



# capacitors = ["22e-6"]
capacitors = ["68e-6","100e-6","150e-6"]
# capacitors = ["22e-6","33e-6","47e-6","68e-6","100e-6","150e-6","220e-6","330e-6","470e-6","680e-6"]
# capacitors = ["220e-6"]
# capacitors = [4.7e-6]
traces = [
    # "../traces/RF_1.csv",
    "../traces/RF_2.csv",
    # "../traces/RF_6.csv",
    # "../traces/RF_7.csv",
    # "../traces/RF_9.csv",
    # "../traces/Solar_Indoor_Moving.csv",
]
# traces = ["CapSimu/traces/RF_2.csv"]

# Create a DataFrame to store the best knobs and the error, checkpoints
columns = ["knobs_list", "error", "checkpoints", "trace", "capacitor"]
df = pd.DataFrame(columns=columns)

def generateConfigFile(trace, capacitor):

    # copy the generic config.yaml.in file from fusedBin/fusedConfig/ to fusedBin/config.yaml
    shutil.copy2("fusedBin/fusedConfig/config.yaml.in", "fusedBin/config.yaml")

    # append the trace and capacitor size at the end
    with open("fusedBin/config.yaml", "a") as f:
        f.write(f"VoltageTraceFile: \"{trace}\"\n")
        f.write(f"CapacitorValue: {capacitor}\n")

for trace in traces:
    for capacitor in capacitors:

        # generate the corresponding config file for fused
        generateConfigFile(trace, capacitor)

        # Get checkpoint of the original unapproximated code
        original_checkpoints = checkpointOrchestration('target/',app_name)

        # Write the original checkpoints to a file logs/original_checkpoints.txt
        with open("logs/original_checkpoints.txt", "w") as f:
            f.write(str(original_checkpoints))

        trace_name = trace.split("/")[-1].split(".")[0]
        capacitor_number = capacitor.split("e")[0]

        # Create a csv file logs/{appName}_{capacitor}_{trace}.csv
        with open(f"logs/{app_name}_{capacitor_number}_{trace_name}.csv", "w") as f:
            f.write("knobs_list,error,checkpoints\n")

        # Save the {trace,capacitor} pair in a file. Path = "logs/trace_capacitor.txt"
        with open("logs/trace_capacitor.txt", "w") as f:
            f.write(f"{trace},{capacitor}")

        best_score, best_knobs = runBayesOpt()

        print(f"Best knobs: {best_knobs}")
        print(f"Best score (E+C): {best_score}")

        # Find the error and checkpoints using the best knobs from logs/{appName}_{capacitor}_{trace}.csv
        best_error = None
        best_checkpoints = None
        with open(f"logs/{app_name}_{capacitor_number}_{trace_name}.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row

            # Match the best knobs with the knobs_list in the csv file
            for row in reader:
                checkpoints = row[-1]
                error = row[-2]
                knobs_list_str = row[:-2]  # Extract the knobs list as a string

                # Convert knobs_list_str (which is something like "[1','3','4]") to actual list
                # Remove unwanted characters and convert it to a proper list
                knobs_list_str = ','.join(knobs_list_str)  # Merge if knobs_list_str is split across multiple columns
                knobs_list = ast.literal_eval(knobs_list_str.replace("'", ""))  # Convert the string to a list of integers

                print(str(knobs_list) , str(best_knobs), str(knobs_list) == str(best_knobs))
                if str(knobs_list) == str(best_knobs):
                    best_error = error
                    best_checkpoints = checkpoints
                    break

        df = df._append(
            {
                columns[0]: best_knobs,
                columns[1]: best_error,
                columns[2]: best_checkpoints,
                columns[3]: trace,
                columns[4]: capacitor,
            },
            ignore_index=True,
        )

        with open(f"logs/original_checkpoints_{app_name}-{capacitor}_{trace_name}.txt", "w") as f:
            f.write(str(original_checkpoints))

# Save the DataFrame to a csv file
df.to_csv(f"logs/best_knobs_{app_name}.csv", index=False)
