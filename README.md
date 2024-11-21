## **CheckMate: LLM-Powered Approximate Intermittent Computing**

CheckMate is a tool designed to analyze and approximate application codebases using LLMs, facilitating intermittent computing applications. The framework incorporates tools like `egypt`, `clangd`, and a customized version of the `fused` simulator.

---

## **Setup**

### **1. Install `egypt`**
`egypt` generates call graphs for C programs. Follow these steps to install it:

1. Download `egypt` from [this link](https://www.gson.org/egypt/).
2. Extract the downloaded tar file and navigate to the extracted folder:
   ```bash
   tar -xvf egypt.tar.gz
   cd egypt
   ```
3. Run the following commands to install:
   ```bash
   sudo apt install perl
   sudo apt install graphviz
   perl Makefile.PL
   make
   sudo make install
   ```
4. Verify installation:
   ```bash
   man egypt
   ```

---

### **2. Install `clangd`**
`clangd` is typically pre-installed on Linux distributions. To check:
```bash
clangd --version
```
If not installed, run:
```bash
sudo apt install clangd
```

---

### **3. Install and Build `fused-checkmate`**

The `fused` simulator is used to evaluate the performance of intermittent computing applications. To set up:

1. Clone the `fused-checkmate` repository:
   ```bash
   git clone https://github.com/rafayy769/fused-checkmate.git
   ```
2. Use the provided bash script to build and install:
   ```bash
   bash install_fused_script.sh
   ```
3. Once built, copy the `fused` binary from the `build` directory in the cloned repository to the `fusedBin` folder in the CheckMate repository.

---

### **4. Set Up the `.env` File**
Create a `.env` file in the root directory of CheckMate with the following configurations, depending on your preferred LLM API:

- For OpenAI's API:
  ```plaintext
  OPENAI_API_KEY="YOUR-API-KEY"
  LLM_MODEL="gpt-4o"
  ```
- For Anthropic's API:
  ```plaintext
  ANTHROPIC_API_KEY="YOUR-API-KEY"
  LLM_MODEL="claude-3-5-sonnet-latest"
  ```

---

### **5. Install Python Dependencies**

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv checkmate_env
   source checkmate_env/bin/activate
   ```
2. Install dependencies from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**

1. **Configure the Tool:**
   - Place your **API key** and **model name** in the `.env` file.
   - Place the application to be approximated (along with its required compilation files) in the `target` folder.
   - If using a checkpointing library other than `iclib ManageState`, include the necessary library files in the `target` folder as well (to be added).

2. **Define Inputs:**
   - Fill in the `error class` and `energy trace` variables in the `inputs.yml` file (to be added).

3. **Note:** 
   - The recommended LLM snapshot is `gpt-4o-2024-11-20`, as it has undergone the most testing and provides stable performance.

---

### **Additional Notes**

- Ensure that all dependencies, especially `clangd` and `egypt`, are installed correctly before proceeding with application analysis.
- Use of a virtual environment is highly encouraged to prevent conflicts with global Python installations.
