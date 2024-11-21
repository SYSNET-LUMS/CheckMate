import os
import numpy as np
import cv2
import pandas as pd
from skimage.metrics import structural_similarity as ssim
import subprocess


def generateGroundTruth(appName):

    # Preserve the current working directory
    cwd = os.getcwd()

    # Change directory to the target/ directory
    os.chdir("target")

    if appName == "susan":

        # Make clean and make main
        subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

        cmd = f"./main > out.pgm"
        subprocess.run(cmd, shell=True)

    elif appName == "sobel-iclib":

        # Make clean and make main
        subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

        cmd = f"./main && mv img.pgm out.pgm"
        subprocess.run(cmd, shell=True)

    elif appName == "stringsearch" or appName == "stringsearch-iclib" or appName == "ar-iclib" or appName == "fft-iclib" or appName == "bc-iclib":
        # Make clean and make main
        subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

        # Run the program and save the output to a output.csv file
        subprocess.run("./main > ground_truth.csv", shell=True)

    elif appName == "fft" or appName == "lqi" or appName == "lqi-iclib":
        # Make clean and make main
        subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

        # Run the program and save the output to a output.txt file
        subprocess.run("./main > ground_truth.txt", shell=True)

    else:
        raise ValueError("Invalid application name")

    # Restore the original working directory
    os.chdir(cwd)


def load_pgm_opencv(file_path):
    # Load PGM image using OpenCV
    image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    return image

def sobelError(pathToCodebase):

    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    ground_truth = "out.pgm"
    predicted = "predicted.pgm"

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    cmd = f"./main && mv img.pgm {predicted}"
    subprocess.run(cmd, shell=True)

    # Calculate the F1-score
    # original_image = load_pgm_opencv(ground_truth)
    # approximated_image = load_pgm_opencv(predicted)

    # true_positives = np.sum((original_image == 255) & (approximated_image == 255))
    # false_positives = np.sum((original_image == 0) & (approximated_image == 255))
    # false_negatives = np.sum((original_image == 255) & (approximated_image == 0))

    # precision = true_positives / (true_positives + false_positives + 1e-10)
    # recall = true_positives / (true_positives + false_negatives + 1e-10)
    # f1_score = 2 * (precision * recall) / (precision + recall + 1e-10)

    original_image = load_pgm_opencv(ground_truth)
    approximated_image = load_pgm_opencv(predicted)
    ssim_score = ssim(original_image, approximated_image)

    # # Change back to the original working directory
    os.chdir(cwd)

    # print(f"Debug: SSIM Score (Accuracy): {ssim_score}")
    # print(f"Debug: Error: {(1 - ssim_score) / 2}")

    print(f"Debug: F1 Score: {ssim_score}")
    print(f"Debug: Error: {1 - ssim_score}")

    # Return
    return (1 - ssim_score) / 2

    # return 1 - ssim_score


def susanError(pathToCodebase):

    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    ground_truth = "out.pgm"
    predicted = "predicted.pgm"

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    cmd = f"./main > {predicted}"
    subprocess.run(cmd, shell=True)

    # Calculate the F1-score
    original_image = load_pgm_opencv(ground_truth)
    approximated_image = load_pgm_opencv(predicted)

    true_positives = np.sum((original_image == 255) & (approximated_image == 255))
    false_positives = np.sum((original_image == 0) & (approximated_image == 255))
    false_negatives = np.sum((original_image == 255) & (approximated_image == 0))

    precision = true_positives / (true_positives + false_positives + 1e-10)
    recall = true_positives / (true_positives + false_negatives + 1e-10)
    f1_score = 2 * (precision * recall) / (precision + recall + 1e-10)

    # original_image = load_pgm_opencv(ground_truth)
    # approximated_image = load_pgm_opencv(predicted)
    # ssim_score = ssim(original_image, approximated_image)

    # # Change back to the original working directory
    os.chdir(cwd)

    # print(f"Debug: SSIM Score (Accuracy): {ssim_score}")
    # print(f"Debug: Error: {(1 - ssim_score) / 2}")

    print(f"Debug: F1 Score: {f1_score}")
    print(f"Debug: Error: {1 - f1_score}")

    # Return
    # return (1 - ssim_score) / 2

    return 1 - f1_score


def stringSearchError(pathToCodebase):

    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    # Run the program and save the output to a output.csv file
    subprocess.run("./main > output.csv", shell=True)

    # Load the ground truth
    with open("ground_truth.csv", "r") as file:
        ground_truth = file.read().splitlines()

    # Load the output
    with open("output.csv", "r") as file:
        predictions = file.read().splitlines()

    # Ensure the DataFrames have the same length
    if len(ground_truth) != len(predictions):
        raise ValueError(
            "The number of rows in ground_truth and output must be the same."
        )

    # Calculate the F1-score
    tp = 0
    fp = 0
    fn = 0

    for i in range(len(ground_truth)):

        if ground_truth[i] == "1" and predictions[i] == "1":
            tp += 1
        elif ground_truth[i] == "0" and predictions[i] == "1":
            fp += 1
        elif ground_truth[i] == "1" and predictions[i] == "0":
            fn += 1

    print(f"TP: {tp}, FP: {fp}, FN: {fn}")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (fn + tp) if (fn + tp) > 0 else 0
    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    # Change back to the original working directory
    os.chdir(cwd)

    print(f"F1 Score: {f1_score}")

    return 1 - f1_score

def fftError(pathToCodebase):
    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    # Run the program and save the output to a output.txt file
    subprocess.run("./main > output.csv", shell=True)

    # # Make sure the arrays are of the same length
    # if len(ground_truth_fft) != len(approximate_fft):
    #     # Truncate both to the shorter length
    #     min_length = min(len(ground_truth_fft), len(approximate_fft))
    #     ground_truth_fft = ground_truth_fft[:min_length]
    #     approximate_fft = approximate_fft[:min_length]

    # # Calculate the magnitude of both the accurate and approximate FFT results
    # original_magnitude = np.abs(ground_truth_fft)  # Magnitude of the ground truth
    # approximate_magnitude = np.abs(approximate_fft)  # Magnitude of the approximate FFT

    # # Calculate R2-score using magnitudes
    # residual_sum_of_squares = np.sum((original_magnitude - approximate_magnitude) ** 2)
    # total_sum_of_squares = np.sum((original_magnitude - np.mean(original_magnitude)) ** 2)

    # print(original_magnitude , np.mean(original_magnitude))
    # print(residual_sum_of_squares )

    # r_squared = 1 - (residual_sum_of_squares / total_sum_of_squares)

    import csv

    def read_fft_from_csv(filename):
        """
        Reads FFT data from a CSV file where each row contains two values: 
        the real part and the imaginary part.
        """
        fft_results = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                real_part = float(row[0])
                imag_part = float(row[1])
                fft_results.append(complex(real_part, imag_part))
        return np.array(fft_results)

    def relative_error(fft_accurate, fft_inaccurate):
        """
        Computes the relative error between the accurate and inaccurate FFT results.
        Error is computed as |X_accurate - X_approx| / |X_accurate|.
        """
        # Ensure the two FFT arrays have the same length
        if len(fft_accurate) != len(fft_inaccurate):
            raise ValueError("FFT result arrays must be of the same length.")

        # Compute the relative error
        relative_errors = np.abs(fft_accurate - fft_inaccurate) / np.abs(fft_accurate)

        # Replace NaN values (which can happen if accurate value is 0) with 0
        relative_errors = np.nan_to_num(relative_errors)

        # Return the mean relative error
        return np.mean(relative_errors)


    # Load the ground truth FFT results (real, imaginary pairs)
    ground_truth_fft = read_fft_from_csv("ground_truth.csv")

    # Load the approximate FFT results (real, imaginary pairs)
    approximate_fft = read_fft_from_csv("output.csv")


    # Example usage
    error = relative_error(ground_truth_fft, approximate_fft)


    # Change back to the original working directory
    os.chdir(cwd)

    return error


def lqiError(pathToCodebase):

    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    # Run the program and save the output to a output.txt file
    subprocess.run("./main > output.txt", shell=True)

    ground_truth = 0
    approximate = 0

    with open("ground_truth.txt", "r") as file:
        ground_truth = float(file.read())

    with open("output.txt", "r") as file:
        approximate = float(file.read())

    error = abs(ground_truth - approximate) / ground_truth

    # Change back to the original working directory
    os.chdir(cwd)

    return error

def arError(pathToCodebase):
    def calculate_mape_from_csv(pred_file_path, gt_file_path):
        # Read the predicted CSV file into a DataFrame
        pred_df = pd.read_csv(pred_file_path, header=None, names=['still', 'moving'])
        
        # Read the ground truth CSV file into a DataFrame
        ground_truth_df = pd.read_csv(gt_file_path, header=None, names=['still', 'moving'])
        
        # Calculate the total of still and moving points from both the prediction and ground truth
        total_pred_still = pred_df['still'].sum()
        total_pred_moving = pred_df['moving'].sum()
        
        total_gt_still = ground_truth_df['still'].sum()
        total_gt_moving = ground_truth_df['moving'].sum()
        
        # Calculate the Mean Absolute Percentage Error (MAPE)
        mape_still = abs((total_gt_still - total_pred_still) / total_gt_still)
        mape_moving = abs((total_gt_moving - total_pred_moving) / total_gt_moving)
        
        # Combine the MAPE for still and moving states
        overall_mape = (mape_still + mape_moving) / 2
        
        return overall_mape


    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    # Run the program and save the output to a output.txt file
    subprocess.run("./main > output.csv", shell=True)


    os.chdir(cwd)
    error = calculate_mape_from_csv(f"{pathToCodebase}/output.csv",f"{pathToCodebase}/ground_truth.csv")

    return error

def bitcountError(pathToCodebase):
    def calculate_mape_from_csv(pred_file_path, gt_file_path):
        """
        Calculate the Mean Absolute Percentage Error (MAPE) from predicted and ground truth CSV files.

        Parameters:
        pred_file_path (str): Path to the CSV file containing the predicted values.
        gt_file_path (str): Path to the CSV file containing the ground truth values.

        Returns:
        float: The overall MAPE value.
        """
        # Read the predicted CSV file into a DataFrame
        pred_df = pd.read_csv(pred_file_path, header=None)
        
        # Read the ground truth CSV file into a DataFrame
        ground_truth_df = pd.read_csv(gt_file_path, header=None)
        
        # Calculate the absolute percentage error for each value
        # Adding a small epsilon (1e-10) to avoid division by zero in edge cases
        epsilon = 1e-10
        mape_values = np.abs((pred_df - ground_truth_df) / (ground_truth_df + epsilon))
        
        # Calculate the overall MAPE as the mean of individual MAPE values
        overall_mape = mape_values.mean().mean()  # Mean of means to get a single overall value
        
        return overall_mape

    # Save the current working directory
    cwd = os.getcwd()

    # Change directory to the codebase
    os.chdir(pathToCodebase)

    # Make clean and make main
    subprocess.run("make clean", shell=True, stdout=subprocess.DEVNULL)
    subprocess.run("make main", shell=True, stdout=subprocess.DEVNULL)

    # Run the program and save the output to a output.csv file
    subprocess.run("./main > output.csv", shell=True)

    # Return to the original directory
    os.chdir(cwd)

    # Calculate RMSE using the output.csv and ground_truth.csv files
    error = calculate_mape_from_csv(f"{pathToCodebase}/output.csv", f"{pathToCodebase}/ground_truth.csv")

    return error
