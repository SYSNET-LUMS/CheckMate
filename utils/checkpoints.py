import os
import shutil
import subprocess
import json
from ruamel.yaml import YAML

def buildObjects(appName):

    # save the current working directory
    cwd = os.getcwd()

    # go to eval-apps directory
    os.chdir("eval-apps")

    # check if "build" directory exists
    if not os.path.exists("build"):
        os.makedirs("build")

    # change the directory to the "build" directory
    os.chdir("build")

    # build the appName using cmake
    try:
        subprocess.run(
            f"cmake .. -DTARGET_ARCH=msp430 && make {appName}-MS-msp430",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while building the objects: {e}")

    # change back to the original working directory
    os.chdir(cwd)

    # return the path to the built hex file
    return f"eval-apps/build/{appName}/{appName}-MS-msp430.hex"

def runFused(pathToHex: str):
    # copy the hex file to the fused directory, and rename it to "app.hex"

    binaryName = "fusedBin/app.hex"

    shutil.copy(pathToHex, binaryName)
    cwd = os.getcwd()

    # change the directory to the fused directory
    os.chdir("fusedBin")

    # run the fused simulator, wait for it to finish
    try:
        subprocess.run(
            "./fused",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the fused simulator: {e}")

    # change back to the original working directory
    os.chdir(cwd)

    # remove the copied hex file
    os.remove(binaryName)

def getCyclesFromFused():
    
    dump_file = "fusedBin/cycles.dump"

    # read the cycles from the dump file
    with open(dump_file, "r") as f:
        cycles = f.read().strip()

    # subprocess.run(f"rm -f {dump_file}")
    os.remove(dump_file)

    return int(cycles)


def copyNonMakefiles(targetDir, appName):
    # Define the destination directory path
    destinationDir = f"eval-apps/{appName}/"
    
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destinationDir):
        os.makedirs(destinationDir)
    
    # Loop through all the files in the targetDir
    for root, dirs, files in os.walk(targetDir):
        for file in files:
            # Ignore files that are makefiles (case-insensitive)
            if file.lower() == "makefile":
                continue
            
            # Construct full file path
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destinationDir, file)
            
            # Copy file from source to destination
            shutil.copy2(source_file, destination_file)
            # print(f"Copied {source_file} to {destination_file}")

def updateYamlFile(new_voltage_trace_file, new_capacitor_value, file_path="fusedBin/config.yaml"):
    # Initialize the ruamel.yaml YAML instance
    yaml = YAML()
    yaml.preserve_quotes = True  # Optional: if you want to preserve quotes around strings

    # Read the YAML file with comments
    with open(file_path, 'r') as file:
        yaml_data = yaml.load(file)

    # Update the values
    yaml_data['VoltageTraceFile'] = new_voltage_trace_file
    yaml_data['CapacitorValue'] = new_capacitor_value

    # Write the updated YAML back to the file, preserving comments
    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file)

    print(f"Updated VoltageTraceFile to '{new_voltage_trace_file}' and CapacitorValue to {new_capacitor_value}.")



def checkpointOrchestration(targetDir, appName): # Fused intigration need.
    """
    Orchestrates the checkpointing process.

    Args:
        appName (str): The name of the application.
        capacitorSize (str): The size of the capacitor.
        trace (str): The trace file.
    """
    # For Rafay
    # In old system:
    #     We get take the code files form the knob_tuning folder and move it into app_runtime Source dir 
    #     to compile and generate .elf file. Then we copy the .elf binary to renodeBin and run renode to 
    #     get the number of cycles. We then feed the number of cycles to Capsimo along with capacitor
    #     size, energy and capacitor size (we get capsize from getCheckpointSize function by using the 
    #     /usr/bin/time -v command ). Capsimo will return the number of checkpoints.
    # New system:
    #     from my understanding we still would need the .elf for fused (it was in a diagram in the paper
    #     that showed them using .elf). The app_runtime folder it what we using before to compile for these
    #     files, but they are for stm32 controler and idk exactly what would need to change for other 
    #     board like msp, ect but I think you probability know about this better then me. 
    #     But other than that there isn't much i think that can be reused for fused.
    # 
    # Hope this helped :) 

    # Generate the ELF file
    # generateELF(targetDir)

    # Copy files form target/ to eval-apps/{appName}/
    copyNonMakefiles(targetDir, appName)

    hexDir = buildObjects(appName)

    runFused(hexDir)
    # Run Renode
    # runRenode()

    cycles = getCyclesFromFused()

    # Get the number of checkpoints
    # Fused: Calculates number of checkpoints using capsimo and cycles form renode. Now with fused neither are needed.
    # checkpoints = getCheckpoints(appName, capacitorSize, trace, targetDir) 

    return cycles