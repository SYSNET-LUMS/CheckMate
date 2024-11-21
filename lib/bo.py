import json
import random
import subprocess
import copy
from skopt import gp_minimize
from skopt.space import Integer, Real
import ast


from utils.utils import getAppName
from utils.validator import updateKnobValue
from config.globals import TARGET_FILES
from config.config import ERROR_BOUND
from utils.error_analyzer import susanError, lqiError, stringSearchError, fftError, sobelError, arError, bitcountError
from utils.checkpoints import checkpointOrchestration
from lib.lsp import lsp_patcher


def createSearchSpace(pathToJson):

    with open(pathToJson, "r") as file:
        json_content = file.read()

    # Parse the JSON content
    approximation_data = json.loads(json_content)

    space = []
    for approximation_dict in approximation_data:
        knob_ranges = ast.literal_eval(approximation_dict["knobRanges"])
        knob_step_size = ast.literal_eval(approximation_dict["knobStepSize"])

        for i, knob_range in enumerate(knob_ranges):
            for knob_name, range_values in knob_range.items():
                if knob_step_size[i][knob_name] == "Integer":
                    space.append(
                        Integer(range_values[0], range_values[1], name=knob_name)
                    )
                if knob_step_size[i][knob_name] == "Real":
                    space.append(Real(range_values[0], range_values[1], name=knob_name))

    return space


def runBayesOpt():
    tuning_folder = "knob_tuning/apx_all.json"
    random_state = random.randint(0, 100)

    res = gp_minimize(
        evaluateKnobs,
        createSearchSpace(tuning_folder),
        n_calls=120,
        random_state=random_state,
    )
    best_score = res.fun

    return best_score, res.x

    # print(best_score)
    # print(res.x)


def evaluateKnobs(*params):

    global TARGET_FILES

    knobs_list = copy.copy(params[0])

    # knobs_list = [1, 1.0]

    # print(knobs_list)

    with open("knob_tuning/apx_all.json", "r") as file:
        json_content = file.read()

    # Parse the JSON content
    approximation_data = json.loads(json_content)

    for approximation_dict in approximation_data:
        knob_variables = ast.literal_eval(approximation_dict["knobVariables"])
        # print(knob_variables)

        for var in knob_variables:
            new_value = knobs_list.pop(0)
            # print(var)
            # print(new_value)
            updateKnobValue(approximation_dict, new_value, var)

    # json.dump(approximation_data, fp="knob_tuning/apx_all.json")

    # Save approximation_data in knob_tuning/apx_all.json, write your own logic here
    # open("knob_tuning/apx_all.json", "w").write(json.dumps(approximation_data))
    open("knob_tuning/apx_all.json", "w").write(json.dumps(approximation_data, indent=2))

    lsp_patcher("knob_tuning/", "apx_all.json")

    app_name = getAppName()

    # Get the Error
    if app_name == "susan":
        error = susanError("knob_tuning")
    elif app_name == "sobel-iclib":
        error = sobelError("knob_tuning")
    elif app_name == "lqi-iclib":
        error = lqiError("knob_tuning")
    elif app_name == "stringsearch-iclib":
        error = stringSearchError("knob_tuning")
    elif app_name == "fft-iclib":
        error = fftError("knob_tuning")
    elif app_name == "ar-iclib":
        error = arError("knob_tuning")
    elif app_name == "bc-iclib":
        error = bitcountError("knob_tuning")

    print(f"Error Returned from Eval Func: {error}")

    if error > 0.3:
        error = 1

    print(f"DEBUG: {error > ERROR_BOUND}")
    print(f"Error After Bound Check: {error}")

    # logs/trace_capacitor.txt contains the trace and capacitor size
    with open("logs/trace_capacitor.txt", "r") as f:
        trace, capacitor = f.read().split(",")

    # Read the original checkpoints from logs/original_checkpoints.txt
    with open("logs/original_checkpoints.txt", "r") as f:
        original_checkpoints = int(f.read())

    # Get the Checkpoints
    checkpoints = checkpointOrchestration("knob_tuning/",app_name)

    checkpoints_reduction = checkpoints / original_checkpoints

    print("Checkpoint Reduction: ",checkpoints_reduction)

    trace_name = trace.split("/")[-1].split(".")[0]
    capacitor_number = capacitor.split("e")[0]
    # Appends the knobs_list, error and checkpoints to the file, logs/{appName}_{capacitor}_{trace}.csv
    with open(f"logs/{app_name}_{capacitor_number}_{trace_name}.csv", "a") as f:
        f.write(f"{params[0]},{error},{checkpoints}\n")
        # f.write(f"{str([1,1.0])},{error},{checkpoints}\n")

    print(f"------------------------ iteration done ------------------------")

    optimization_metric = error + checkpoints_reduction

    return optimization_metric
