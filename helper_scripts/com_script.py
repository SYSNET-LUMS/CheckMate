import subprocess

app = "stringsearch"
# Define the working directory
working_dir = "/home/iot-lab/Approxify/eval-apps/build/"

# Step 1: Run cmake command
cmake_command = ["cmake", "..", "-DTARGET_ARCH=msp430"]
subprocess.run(cmake_command, cwd=working_dir, check=True)

# Step 2: Run make command
make_command = ["make", f"{app}-iclib-MS-msp430"]
subprocess.run(make_command, cwd=working_dir, check=True)

# Step 3: Copy and rename the generated hex file
copy_command = ["cp", f"{app}-iclib/{app}-iclib-MS-msp430.hex", f"../../fusedBin/app.hex"]
subprocess.run(copy_command, cwd=working_dir, check=True)

print("Build and copy operations completed successfully.")
