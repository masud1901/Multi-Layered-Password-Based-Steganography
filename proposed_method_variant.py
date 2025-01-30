"""Alternative implementation of multi-layer steganography."""

import os
import cv2
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from stegano import lsb


class MultiLayerAESVariant:
    """Variant of MultiLayerAES with different block size and iterations."""
    
    def __init__(self, passwords, iterations=50000):
        self.passwords = passwords
        self.iterations = iterations
        self.block_size = 32  # Larger block size
        
    def pad_data(self, data: bytes) -> bytes:
        """Add PKCS7 padding to the data."""
        padding_length = self.block_size - (len(data) % self.block_size)
        padding = bytes([padding_length]) * padding_length
        return data + padding
        
    def unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
        
    def encode(self, image_path, messages, output_path):
        """Multi-layer AES-CBC + LSB embedding with larger blocks."""
        if len(messages) != len(self.passwords):
            raise ValueError("Messages must match passwords count")

        # Calculate maximum capacity
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")
        max_bytes = (img.shape[0] * img.shape[1] * 3) // 8
            
        embedded_data = b""
        for pwd, msg in zip(self.passwords, messages):
            # Key derivation with different salt size
            salt = os.urandom(32)  # Larger salt
            key = PBKDF2(pwd, salt, dkLen=32, count=self.iterations)
            
            # AES-CBC encryption
            iv = os.urandom(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # Convert message to bytes and add size
            msg_bytes = msg.encode('utf-8')
            msg_size = len(msg_bytes)
            size_block = msg_size.to_bytes(4, 'big')
            
            # Pad and encrypt message
            data_to_encrypt = size_block + msg_bytes
            padded_data = self.pad_data(data_to_encrypt)
            ciphertext = cipher.encrypt(padded_data)
            
            # Layer packaging
            layer_data = salt + iv + ciphertext
            if len(embedded_data) + len(layer_data) > max_bytes:
                raise ValueError(
                    f"Message too long for image capacity: {len(layer_data)}"
                )
            embedded_data += layer_data
            
        # LSB embedding
        lsb.hide(image_path, embedded_data.hex()).save(output_path)
        
    def decode(self, stego_path, passwords):
        """Extract and decrypt layers with larger blocks."""
        if len(passwords) != len(self.passwords):
            raise ValueError("Passwords count mismatch")
            
        hex_data = lsb.reveal(stego_path)
        if not hex_data:
            return [""] * len(passwords)

        binary_data = bytes.fromhex(hex_data)
        results = []
        ptr = 0

        for pwd in passwords:
            if ptr + 48 >= len(binary_data):
                results.append("")
                continue

            try:
                # Extract components
                salt = binary_data[ptr:ptr + 32]
                iv = binary_data[ptr + 32:ptr + 48]
                
                # Get the ciphertext
                remaining = len(binary_data) - ptr - 48
                ciphertext = binary_data[ptr + 48:ptr + 48 + remaining]
                if len(ciphertext) < self.block_size:
                    results.append("")
                    continue
                
                # Derive key and decrypt
                key = PBKDF2(pwd, salt, dkLen=32, count=self.iterations)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                
                # Decrypt and get message size
                padded_plaintext = cipher.decrypt(ciphertext)
                msg_size = int.from_bytes(padded_plaintext[:4], 'big')
                
                # Extract actual message
                msg_data = padded_plaintext[4:4 + msg_size]
                plaintext = msg_data.decode('utf-8')
                results.append(plaintext)
                
                # Update pointer for next layer
                total_size = 4 + msg_size  # Size block + message
                blocks_needed = (total_size + 31) // 32 * 32  # Round up to block size
                ptr += 48 + blocks_needed
                
            except Exception as e:
                print(f"Decoding error in layer: {e}")
                results.append("")
                ptr += 48 + self.block_size

        return results 