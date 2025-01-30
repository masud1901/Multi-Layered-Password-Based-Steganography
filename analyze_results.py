import cv2
import numpy as np
import pandas as pd
from math import log10
from scipy.stats import chi2_contingency


def calculate_psnr(original_path, stego_path):
    """Calculate PSNR between original and stego images"""
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)
    
    if original is None or stego is None:
        raise ValueError("Failed to load images")
    
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    
    PIXEL_MAX = 255.0
    return 20 * log10(PIXEL_MAX / np.sqrt(mse))


def calculate_chi_square(image_path):
    """Calculate Chi-Square statistic for image"""
    img = cv2.imread(image_path, 0)  # Read as grayscale
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Calculate histogram for observed frequencies
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    observed = hist.flatten()
    
    # Calculate expected frequencies (uniform distribution)
    total_pixels = sum(observed)
    expected = np.full_like(observed, total_pixels / len(observed))
    
    # Calculate chi-square statistic
    chi_square = np.sum((observed - expected) ** 2 / expected)
    return chi_square


def calculate_payload(image_path):
    """Estimate payload size in KB"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    total_pixels = img.shape[0] * img.shape[1]
    return round((total_pixels * 0.1) / 1024)  # Convert to KB


def create_comparison_table(original_image, methods_data):
    """Create comparison table for different methods"""
    results = []
    
    for method in methods_data:
        try:
            psnr = calculate_psnr(original_image, method['stego_path'])
            chi_square = calculate_chi_square(method['stego_path'])
            payload = calculate_payload(method['stego_path'])
            
            results.append({
                'Method': method['name'],
                'PSNR (dB)': round(psnr, 1),
                'Chi-Square': round(chi_square),
                'Layers': method['layers'],
                'Payload (KB)': payload,
                'Security': method['security']
            })
            
        except Exception as e:
            print(f"Error processing {method['name']}: {e}")
    
    df = pd.DataFrame(results)
    if not df.empty:
        df.to_csv('comparison_results.csv', index=False)
    return df


if __name__ == "__main__":
    try:
        methods = [
            {
                'name': 'Proposed Method',
                'stego_path': 'proposed_stego.png',
                'layers': 3,
                'security': 'Multi-password AES'
            },
            {
                'name': 'Shmueli et al. (2024)',
                'stego_path': 'shmueli_stego.png',
                'layers': 1,
                'security': 'Single-layer'
            },
            {
                'name': 'Sultan et al. (2023)',
                'stego_path': 'sultan_stego.png',
                'layers': 1,
                'security': 'AES-256'
            }
        ]
        
        original_image = "./Apple.png"
        
        print("\nAnalyzing steganography methods...")
        results_df = create_comparison_table(original_image, methods)
        print("\nGenerated Comparison Table:")
        print(results_df.to_string())
        print("\nResults saved to 'comparison_results.csv'")
        
    except Exception as e:
        print(f"An error occurred: {e}") 