from config.config import (
    REVERSED_PDG
)
from utils.utils import (
    getFilesList
)
from lib.llm import(
    generateExpandMakeFile
)

import subprocess
import pandas as pd
import numpy as np
import json
import shutil
import subprocess 
import os 
import sys
from collections import deque


# --- RTL File Generation --- 

def createRTLFile():
    dst_dir = "dependency_graphs/target"
    src_dir = "target/"
    log_file = "logs/rtl_chat_log.txt"
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # Copy the entire directory tree
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    target_path=dst_dir
    files_list = getFilesList(target_path)

    original = sys.stdout


    while True:
        
        with open(log_file, 'w') as file:
            file.write('')
        sys.stdout = open(log_file, 'w')
        try:
            response = ""
            if not os.path.exists(os.path.join(target_path, "compiler_log.txt")):
                with open(os.path.join(target_path, "compiler_log.txt"), "w") as f:
                    pass  # Just create the file
            with open(os.path.join(target_path, "compiler_log.txt"), "r") as output_file:
                response = generateExpandMakeFile(files_list, output_file.read())

            with open(os.path.join(target_path, "Makefile"), "w") as file:
                file.write(response)

            with open(os.path.join(target_path, "compiler_log.txt"), "w") as output_file:
                subprocess.run("make", shell=True, check=True, cwd=target_path, stdout=output_file, stderr=subprocess.STDOUT)

            subprocess.run("egypt *.expand | dot -ofile", shell=True, check=True, cwd=target_path)

            subprocess.run("make clean", shell=True, check=True, cwd=target_path)
            
            print('Success\n')
            break
            # return 0  # Successful compilation
        except Exception as e:
            print(e)

    sys.stdout = original
        

# --- PDG Generation ---

def parse_dot(dot_data):
    lines = dot_data.strip().splitlines()
    edges = []
    
    for line in lines:
        line = line.strip().strip(';')
        if '->' in line:
            parts = line.split('->')
            src = parts[0].strip()
            dst = parts[1].strip().split()[0]
            edges.append((dst, src))
    return edges

def create_adj_matrix(nodes, edges):
    nodes_list = list(nodes)
    node_index = {node: idx for idx, node in enumerate(nodes_list)}
    size = len(nodes_list)
    matrix = np.zeros((size, size), dtype=int)
    
    for src, dst in edges:
        src_index = node_index[src]
        dst_index = node_index[dst]
        matrix[src_index, dst_index] = 1
    
    return matrix, nodes_list
        
def createPDG():
    dst_dir = "dependency_graphs/target/file"

    dot_data = ""
    with open(dst_dir,'r') as file:
        dot_data = file.read()

    edges = parse_dot(dot_data)
    # print(edges)

    nodes = sorted({element for tup in edges for element in tup})
    # print(nodes)

    adj_matrix, nodes_list = create_adj_matrix(nodes, edges)

    df = pd.DataFrame(adj_matrix, index=nodes_list, columns=nodes_list)

    df_json = df.to_json()
    with open('dependency_graphs/adj_mat.json', 'w') as file:
        file.write(df_json)

    with open('dependency_graphs/nodes_list.json', 'w') as file:
        json.dump(nodes_list, file)


# --- Topological Sort Generation ---

def adj_matrix_to_adj_list(adj_matrix):
    adj_list = {}
    n = len(adj_matrix)
    for i in range(n):
        adj_list[i] = []
        for j in range(n):
            if adj_matrix[i][j] == 1:
                adj_list[i].append(j)
    return adj_list

def topological_sort_kahn(adj_matrix):
    adj_list = adj_matrix_to_adj_list(adj_matrix)
    n = len(adj_matrix)
    in_degree = [0] * n
    
    for i in range(n):
        for j in adj_list[i]:
            in_degree[j] += 1
    
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    topo_order = []
    
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for neighbor in adj_list[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(topo_order) == n:
        return topo_order
    else:
        return topo_order, [i for i in range(n) if in_degree[i] > 0]

def break_cycles(adj_matrix, remaining_nodes):
    for src in remaining_nodes:
        for dst in range(len(adj_matrix)):
            if adj_matrix[src][dst] == 1:
                adj_matrix[src][dst] = 0
                return

def executeTopoSort():
    # Load adjacency matrix and nodes list from JSON
    df = pd.read_json('dependency_graphs/adj_mat.json')
    nodes_list = []
    with open('dependency_graphs/nodes_list.json', 'r') as file:
        nodes_list = json.load(file)

    adj_matrix = df.values

    topo_order_result = topological_sort_kahn(adj_matrix)
    topo_order = []

    if isinstance(topo_order_result, tuple):
        topo_order, remaining_nodes = topo_order_result
        while remaining_nodes:
            break_cycles(adj_matrix, remaining_nodes)
            topo_order_result = topological_sort_kahn(adj_matrix)
            if isinstance(topo_order_result, tuple):
                topo_order, remaining_nodes = topo_order_result
            else:
                topo_order = topo_order_result
                break
    else:
        topo_order = topo_order_result

    topo_order_names = [nodes_list[i] for i in topo_order]

    with open("dependency_graphs/topological_order.json", "w") as file:
        json.dump(topo_order_names, file)


# --- main ---

def initPDGGen(): #Cat 5
    
    # if dependency_graphs folder exists then dont call functions.
    if not os.path.exists("dependency_graphs/"):
        createRTLFile()
        createPDG()
        executeTopoSort()
    else:
        print("PDG already exists - reading files only")    


    # Load PDG and sort

    PDG = pd.read_json("dependency_graphs/adj_mat.json")

    with open("dependency_graphs/topological_order.json", "r") as file:
        topological_order = json.load(file)

    try:
        topological_order.remove("main")
    except:
        pass

    return PDG, topological_order


def reverse_PDG(PDG, topological_order):
    # Reverse the topological order
    reversed_topological_order = topological_order[::-1]

    # Create a mapping from old indices to new indices
    index_mapping = {node: i for i, node in enumerate(topological_order)}
    reversed_index_mapping = {node: i for i, node in enumerate(reversed_topological_order)}

    # Reverse the adjacency matrix
    reversed_PDG = PDG.copy()
    reversed_PDG.index = reversed_PDG.index.map(reversed_index_mapping)
    reversed_PDG.columns = reversed_PDG.columns.map(reversed_index_mapping)
    reversed_PDG = reversed_PDG.sort_index().sort_index(axis=1)

    return reversed_PDG, reversed_topological_order

# Create PDG and run topological sort
print("PDG Generating...\n")
PDG, topological_order = initPDGGen()
print("PDG Generation Successful\n")

# Conditionally reverse the PDG and topological order
if REVERSED_PDG:
    PDG, topological_order = reverse_PDG(PDG, topological_order)

print(PDG)
print("Topological Order:", topological_order)

