from lib.lsp import lsp_patcher
import sys


target_dir= ""
apx_file= ""

if len(sys.argv) > 1:
    target_dir= sys.argv[1]
    apx_file= sys.argv[2]
else:
    print("Enter target dir and apx json file as commad line arguments. \n eg. python3 patcher.py target/ target/apx_all.json")

lsp_patcher(target_dir, apx_file)