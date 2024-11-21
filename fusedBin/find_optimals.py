import os
import shutil
import subprocess

def generateConfigFile(trace, capacitor):

    # copy the generic config.yaml.in file from fusedBin/fusedConfig/ to fusedBin/config.yaml
    shutil.copy2("fusedConfig/config.yaml.in", "config.yaml")

    # append the trace and capacitor size at the end
    with open("config.yaml", "a") as f:
        f.write(f"VoltageTraceFile: \"{trace}\"\n")
        f.write(f"CapacitorValue: {capacitor}\n")

def buildObject(appName):
    # save the current working directory
    cwd = os.getcwd()

    # go to eval-apps directory
    os.chdir("../eval-apps")

    # check if "build" directory exists
    if not os.path.exists("build"):
        os.makedirs("build")

    # build the appName using cmake
    try:
        subprocess.run(
            f"cd build && cmake .. -DTARGET_ARCH=msp430 && make {appName}-MS-msp430",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while building the objects: {e}")

    # change back to the original working directory
    os.chdir(cwd)

    # return the path to the built hex file
    return f"eval-apps/build/{appName}/{appName}.hex"

def runFused(appName):
    binaryName = "./app.hex"

    # try:
        # copy the hex file to the current directory
    shutil.copy(f"../eval-apps/build/{appName}/{appName}-MS-msp430.hex", binaryName)

    # run the fused simulator, and return the exit code
    return subprocess.run(f"./fused", shell=True, stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode

def find_optimal_combinations(trace_files, capacitances, eval_apps, output_dir):
    # Dictionary to hold the ideal combinations for each app
    optimal_combos = {app: [] for app in eval_apps}
    
    # Loop through each eval app
    for app in eval_apps:
        print(f"[+] Evaluating app: {app}")
        # Build the object file for the current eval app
        buildObject(app)

        # Loop through each trace file and capacitance value
        for trace in trace_files:
            for cap in capacitances:
                print(f"[+] Trying trace: {trace}, capacitance: {cap}")
                
                # Generate the config file
                generateConfigFile(trace, cap)
                
                # Run the fused application and check the exit status
                exit_status = runFused(app)
                
                if not exit_status:
                    print(f"[✓] Simulation successful for Trace: {trace}, Capacitance: {cap} on {app}")
                    # Store the successful trace-capacitance combo
                    optimal_combos[app].append((trace, cap))
                else:
                    print(f"[✗] Failed for Trace: {trace}, Capacitance: {cap} on {app}")

    # Dump the results into files for each eval app
    for app, combos in optimal_combos.items():
        output_file = os.path.join(output_dir, f"{app}_optimal_combos.txt")
        with open(output_file, 'w') as f:
            for trace, cap in combos:
                f.write(f"Trace: {trace}, Capacitance: {cap}\n")
        print(f"[+] Optimal combinations for {app} saved to {output_file}")

# Example usage:
trace_files = [
    "../CapSimu/traces/RF-1.csv",
    "../CapSimu/traces/RF-2.csv",
    "../CapSimu/traces/RF-6.csv",
    "../CapSimu/traces/RF-7.csv",
    "../CapSimu/traces/RF-9.csv",
    "../CapSimu/traces/Solar_Indoor_Moving.csv",
]
capacitances = ["22.0e-6"
                ,"33.0e-6","47.0e-6","68.0e-6","100.0e-6","150.0e-6","220.0e-6","330.0e-6","470.0e-6","680.0e-6"]
eval_apps = ["lqi-iclib"
             , "stringsearch-iclib", "sobel-iclib"]  # List of eval apps
output_dir = "./combinations"  # Directory where results will be saved

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

print("[+] Finding optimal combinations for each eval app...")
# Call the function to find the optimal combinations
find_optimal_combinations(trace_files, capacitances, eval_apps, output_dir)