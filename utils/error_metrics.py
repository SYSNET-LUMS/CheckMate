"""
This module contains different metrics that can be used to calculate error dependig on the domain.
"""

import math
import numpy as np
from scipy.signal import convolve2d
from scipy import signal


def euclidean_distance(approximated_output_list, actual_output_list):
    """
    This function calculates the Euclidean distance between two given lists of numbers

    Parameters:
    approximated_output_list (list of numbers) - the approximated output
    actual_output_list (list of numbers) - the actual accurate output

    Returns:
    Value Error | number
    """

    if len(approximated_output_list) != len(actual_output_list):
        raise ValueError("Lists must have the same length")

    squared_diff = [
        (a - b) ** 2 for a, b in zip(approximated_output_list, actual_output_list)
    ]
    distance = math.sqrt(sum(squared_diff))
    return distance


def manhattan_distance(approximated_output_list, actual_output_list):
    """
    This function calculates the Manhattan distance between two given lists of numbers

    Parameters:
    approximated_output_list (list of numbers) - the approximated output
    actual_output_list (list of numbers) - the actual accurate output

    Returns:
    Value Error | number
    """

    if len(approximated_output_list) != len(actual_output_list):
        raise ValueError("Lists must have the same length")

    distance = sum(
        abs(a - b) for a, b in zip(approximated_output_list, actual_output_list)
    )
    return distance


def rmse(approximated_output_list, actual_output_list):
    """
    This function calculates the Root Mean Squared Error between two given lists of numbers

    Parameters:
    approximated_output_list (list of numbers) - the approximated output
    actual_output_list (list of numbers) - the actual accurate output

    Returns:
    Value Error | number
    """

    if len(approximated_output_list) != len(actual_output_list):
        raise ValueError("Lists must have the same length")

    squared_diff = [
        (a - b) ** 2 for a, b in zip(approximated_output_list, actual_output_list)
    ]
    mean_squared_error = sum(squared_diff) / len(approximated_output_list)
    rmse_value = math.sqrt(mean_squared_error)
    return rmse_value


def calculate_ssim(img1, img2):
    """
    This function calculates the structural similarity index between two given 2d lists representing images

    Parameters:
    img1 (2d list of numbers) - the approximated matrix representation of the image
    img2 (2d list of numbers) - the actual matrix representation of the image

    Returns:
    number
    """

    K1 = 0.01
    K2 = 0.03
    L = 255  # Pixel depth

    def _ssim(img1, img2):
        img1 = np.array(img1, dtype=np.float64)
        img2 = np.array(img2, dtype=np.float64)
        img1_sq = img1**2
        img2_sq = img2**2
        img1_img2 = img1 * img2

        # Compute the mean values
        mu1 = convolve2d(img1, np.ones((11, 11)), mode="valid") / 121.0
        mu2 = convolve2d(img2, np.ones((11, 11)), mode="valid") / 121.0
        mu1_sq = mu1**2
        mu2_sq = mu2**2
        mu1_mu2 = mu1 * mu2

        # Compute the variances
        sigma1_sq = (
            convolve2d(img1_sq, np.ones((11, 11)), mode="valid") / 121.0 - mu1_sq
        )
        sigma2_sq = (
            convolve2d(img2_sq, np.ones((11, 11)), mode="valid") / 121.0 - mu2_sq
        )
        sigma12 = (
            convolve2d(img1_img2, np.ones((11, 11)), mode="valid") / 121.0 - mu1_mu2
        )

        # Compute SSIM
        ssim_map = ((2 * mu1_mu2 + K1) * (2 * sigma12 + K2)) / (
            (mu1_sq + mu2_sq + K1) * (sigma1_sq + sigma2_sq + K2)
        )
        return np.mean(ssim_map)

    img1 = np.array(img1)
    img2 = np.array(img2)

    return _ssim(img1, img2)
