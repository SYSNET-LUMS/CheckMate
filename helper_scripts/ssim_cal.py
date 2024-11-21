import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.io import imread
import sys

def compute_ssim(image1_path, image2_path):
    # Read the PGM images
    image1 = imread(image1_path, as_gray=True)
    image2 = imread(image2_path, as_gray=True)
    
    # Ensure that the images are the same size
    if image1.shape != image2.shape:
        print("Error: The input images must have the same dimensions.")
        return

    # Compute the SSIM between the two images
    ssim_index, ssim_map = ssim(image1, image2, full=True)
    
    # Print SSIM index (a single value to represent similarity)
    print(f"SSIM: {ssim_index:.4f}")
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ssim_pgm.py <path_to_image1.pgm> <path_to_image2.pgm>")
    else:
        image1_path = sys.argv[1]
        image2_path = sys.argv[2]
        compute_ssim(image1_path, image2_path)
