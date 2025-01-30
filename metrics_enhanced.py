"""Enhanced metrics calculation for steganography analysis."""

import cv2
import numpy as np
import os

def calculate_mse(original, stego):
    """Calculate Mean Squared Error."""
    return np.mean((original - stego) ** 2)

def calculate_psnr(mse):
    """Calculate Peak Signal-to-Noise Ratio."""
    if mse == 0:
        return 100.0
    return 20 * np.log10(255 / np.sqrt(mse))

def calculate_chi_square(original, stego):
    """Calculate chi-square statistic between images."""
    chi2 = 0
    for i in range(3):  # BGR channels
        hist_orig = cv2.calcHist([original], [i], None, [256], [0, 256]).flatten()
        hist_stego = cv2.calcHist([stego], [i], None, [256], [0, 256]).flatten()
        # Add small constant to avoid division by zero
        chi2 += np.sum((hist_stego - hist_orig) ** 2 / (hist_orig + 1e-10))
    return chi2 / 3  # Average across channels

def calculate_metrics(original, stego, stego_path):
    """Calculate metrics between original and stego images."""
    try:
        # Basic metrics
        mse = calculate_mse(original, stego)
        psnr = calculate_psnr(mse)

        # Calculate chi-square statistic
        chi2 = calculate_chi_square(original, stego)

        # Calculate bit error rate (BER)
        diff = np.abs(original - stego)
        ber = np.sum(diff > 0) / (original.size)

        # Get file size in KB
        if os.path.exists(stego_path):
            stego_size = round(os.path.getsize(stego_path) / 1024.0, 2)  # KB
        else:
            print(f"File not found: {stego_path}")
            stego_size = 0

        return {
            'PSNR': psnr,
            'MSE': mse,
            'Chi-Square': chi2,
            'File Size (KB)': stego_size,
            'Bit Error Rate': ber
        }

    except Exception as e:
        print(f"Metric calculation error: {str(e)}")
        return {
            'PSNR': 0,
            'MSE': 0,
            'Chi-Square': 0,
            'File Size (KB)': 0,
            'Bit Error Rate': 0
        }