import os
import shutil
import fnmatch


def delete_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted folder: {path}")
    else:
        print(f"Folder not found: {path}")


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted file: {path}")
    else:
        print(f"File not found: {path}")


def delete_files_in_folder_with_extensions(folder, extensions):
    for root, _, files in os.walk(folder):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                delete_file(file_path)


def delete_folders_with_prefix(folder, prefix):
    for root, dirs, _ in os.walk(folder):
        for dir in dirs:
            if dir.startswith(prefix):
                dir_path = os.path.join(root, dir)
                delete_folder(dir_path)


def run_make_clean_and_delete_makefile(target_dir):
    makefile_path = os.path.join(target_dir, "Makefile")
    os.chdir(target_dir)
    os.system("make clean")
    delete_file(makefile_path)
    os.chdir("..")


def main():
    # Delete folders "functions" and "approximated_function"
    delete_folder("functions")
    delete_folder("approximated_functions")
    delete_folder("knob_tuning")

    # Delete folder "dependency_graphs/target"
    delete_folder("dependency_graphs")
    
    # Delete folder "compilation_testing/"
    delete_folder("compilation_testing")

    # Delete all txt, json, and csv files in the "log" folder
    delete_files_in_folder_with_extensions("logs", [".txt", ".json"])

    # Remove .elf files from remondBin
    delete_files_in_folder_with_extensions("renodeBin", [".elf"])

    # Remove "ground_truth.csv" from target dir, run make clean, then delete the Makefile
    delete_file("target/ground_truth.csv")
    run_make_clean_and_delete_makefile("target")

    print("Cleanup completed.")


if __name__ == "__main__":
    main()
