"""Benchmark script for comparing steganography methods."""

import cv2
import time
import os
import pandas as pd
from proposed_method import MultiLayerAES
from proposed_method_variant import MultiLayerAESVariant
from shmueli_method import MaxEnergySeam
from sultan_method import SimpleAESLSB
from metrics_enhanced import calculate_metrics


def analyze_method(
    method_name: str,
    original_path: str,
    stego_path: str,
    layers: int,
    msg_size: int,
    encode_time: float,
    decode_time: float,
    security: str
) -> dict:
    """Calculate metrics for a steganography method."""
    try:
        original = cv2.imread(original_path)
        stego = cv2.imread(stego_path)
        if original is None or stego is None:
            raise ValueError("Could not read images")

        metrics = calculate_metrics(original, stego, stego_path)

        return {
            'Method': method_name,
            'Message Size (Bytes)': msg_size,
            'PSNR (dB)': round(metrics.get('PSNR', 0), 2),
            'File Size (KB)': metrics.get('File Size (KB)', 0),
            'Encoding Time (s)': round(encode_time, 3),
            'Decoding Time (s)': round(decode_time, 3),
            'MSE': round(metrics.get('MSE', 0), 4),
            'Chi-Square': round(metrics.get('Chi-Square', 0), 2),
            'Bit Error Rate': round(metrics.get('Bit Error Rate', 0), 6),
            'Layers': layers,
            'Security': security
        }
    except Exception as e:
        print(f"Error in {method_name} analysis: {str(e)}")
        return None


def generate_test_message(size: int) -> str:
    """Generate a test message of specified size."""
    return 'TestMessage123_' * (size // 13 + 1)


def test_method_with_payload(
    method_name: str,
    msg_size: int,
    test_image: str,
    layers: int = 1
) -> dict:
    """Test a steganography method with specific payload size."""
    try:
        output_path = (
            f"{method_name.lower().replace(' ', '_')}"
            f"_{msg_size}bytes.png"
        )
        
        # Get image dimensions for capacity calculation
        img = cv2.imread(test_image)
        if img is None:
            raise ValueError("Could not read test image")
        
        height, width = img.shape[:2]
        
        # Calculate theoretical capacity for each method
        if "Shmueli" in method_name:
            # Shmueli's method uses one bit per pixel along seam
            max_capacity = min(width, 235)  # Limited by seam length
            if msg_size > max_capacity:
                print(
                    f"\nWarning: {method_name} - Message size ({msg_size} bytes) "
                    f"exceeds capacity ({max_capacity} bytes). "
                    f"Message will be truncated."
                )
                msg_size = max_capacity
        else:
            # LSB methods can use 3 bits per pixel
            overhead = 48 if "Variant" in method_name else 32  # Account for headers
            max_capacity = ((height * width * 3) // 8) - (overhead * layers)
            if msg_size > max_capacity:
                print(
                    f"\nWarning: {method_name} - Message size ({msg_size} bytes) "
                    f"exceeds capacity ({max_capacity} bytes). "
                    f"Message will be truncated."
                )
                msg_size = max_capacity
        
        if "Proposed Method" in method_name:
            passwords = [f"pwd{i+1}" for i in range(layers)]
            method = MultiLayerAES(passwords)
            
            # Calculate size per layer
            size_per_layer = msg_size // layers
            messages = [
                generate_test_message(size_per_layer)[:size_per_layer] 
                for _ in range(layers)
            ]
            
            start_time = time.time()
            method.encode(test_image, messages, output_path)
            encode_time = time.time() - start_time
            
            start_time = time.time()
            decoded = method.decode(output_path, passwords)
            decode_time = time.time() - start_time
            
            total_decoded = sum(len(d) for d in decoded)
            print(
                f"{method_name} ({msg_size} bytes) result: "
                f"{total_decoded} bytes total "
                f"[Capacity: {max_capacity} bytes]"
            )
            
        elif "Proposed Variant" in method_name:
            # Similar code for variant method
            passwords = [f"pwd{i+1}" for i in range(layers)]
            method = MultiLayerAESVariant(passwords)
            
            size_per_layer = msg_size // layers
            messages = [
                generate_test_message(size_per_layer)[:size_per_layer] 
                for _ in range(layers)
            ]
            
            start_time = time.time()
            method.encode(test_image, messages, output_path)
            encode_time = time.time() - start_time
            
            start_time = time.time()
            decoded = method.decode(output_path, passwords)
            decode_time = time.time() - start_time
            
            total_decoded = sum(len(d) for d in decoded)
            print(
                f"{method_name} ({msg_size} bytes) result: "
                f"{total_decoded} bytes total "
                f"[Capacity: {max_capacity} bytes]"
            )
            
        elif "Shmueli" in method_name:
            method = MaxEnergySeam()
            msg = generate_test_message(msg_size)[:msg_size]
            
            start_time = time.time()
            method.encode(test_image, msg, output_path)
            encode_time = time.time() - start_time
            
            start_time = time.time()
            decoded = method.decode(output_path)
            decode_time = time.time() - start_time
            
            print(
                f"{method_name} ({msg_size} bytes) result: "
                f"{len(decoded)} bytes "
                f"[Capacity: {max_capacity} bytes]"
            )
            
        else:  # Sultan's method
            method = SimpleAESLSB("mypassword")
            msg = generate_test_message(msg_size)[:msg_size]
            
            start_time = time.time()
            method.encode(test_image, msg, output_path)
            encode_time = time.time() - start_time
            
            start_time = time.time()
            decoded = method.decode(output_path)
            decode_time = time.time() - start_time
            
            print(
                f"{method_name} ({msg_size} bytes) result: "
                f"{len(decoded)} bytes "
                f"[Capacity: {max_capacity} bytes]"
            )

        return analyze_method(
            method_name,
            test_image,
            output_path,
            layers,
            msg_size,
            encode_time,
            decode_time,
            "Multi-password AES" if "Proposed" in method_name
            else "Single-layer" if "Shmueli" in method_name
            else "AES-256"
        )
        
    except Exception as e:
        print(f"{method_name} ({msg_size} bytes) Error: {str(e)}")
        return None


def main() -> None:
    """Run the benchmark tests and generate comparison table."""
    test_image = "Apple.png"
    results = []
    
    # Test different message sizes (in bytes)
    # msg_sizes = [256, 512, 1024, 10240]  # 1KB to 1MB
    msg_sizes = [32, 256, 1024, 8192]  # 1KB to 1MB
    
    # Test each method with different message sizes
    for msg_size in msg_sizes:
        # Test Original Proposed Method with different layers
        for layers in [1, 2, 3]:
            method_name = f"Proposed Method ({layers} layer)"
            result = test_method_with_payload(
                method_name,
                msg_size,
                test_image,
                layers
            )
            if result:
                results.append(result)
                
        # Test Variant Proposed Method with different layers
        for layers in [1, 2, 3]:
            method_name = f"Proposed Variant ({layers} layer)"
            result = test_method_with_payload(
                method_name,
                msg_size,
                test_image,
                layers
            )
            if result:
                results.append(result)
        
        # Test Shmueli's Method
        result = test_method_with_payload(
            "Shmueli et al. (2024)",
            msg_size,
            test_image
        )
        if result:
            results.append(result)
        
        # Test Sultan's Method
        result = test_method_with_payload(
            "Sultan et al. (2023)",
            msg_size,
            test_image
        )
        if result:
            results.append(result)

    # Generate comparison table
    df = pd.DataFrame([r for r in results if r is not None])
    if not df.empty:
        # Sort by Method and Message Size
        df = df.sort_values(['Method', 'Message Size (Bytes)'])
        
        # Reorder columns
        columns = [
            'Method',
            'Message Size (Bytes)',
            'PSNR (dB)',
            'File Size (KB)',
            'Encoding Time (s)',
            'Decoding Time (s)',
            'MSE',
            'Chi-Square',
            'Bit Error Rate',
            'Layers',
            'Security'
        ]
        df = df[columns]
        
        print("\nGenerated Comparison Table:")
        # print(df.to_string())
        df.to_csv("comparison_results.csv", index=False)
        print("\nResults saved to 'comparison_results.csv'")
    else:
        print("\nNo valid results to display")


if __name__ == "__main__":
    main()