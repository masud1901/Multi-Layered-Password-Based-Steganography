# proposed_method.py
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from stegano import lsb
import cv2

class MultiLayerAES:
    """Multi-layer AES steganography with LSB."""

    def __init__(self, passwords, iterations=100000):
        self.passwords = passwords
        self.iterations = iterations
        self.block_size = 16  # AES block size

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
        """Multi-layer AES-CBC + LSB embedding."""
        if len(messages) != len(self.passwords):
            raise ValueError("Messages must match passwords count")

        # Calculate maximum capacity
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")
        max_bytes = (img.shape[0] * img.shape[1] * 3) // 8

        embedded_data = b""
        for pwd, msg in zip(self.passwords, messages):
            # Key derivation
            salt = os.urandom(16)
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
        """Extract and decrypt layers."""
        if len(passwords) != len(self.passwords):
            raise ValueError("Passwords count mismatch")

        hex_data = lsb.reveal(stego_path)
        if not hex_data:
            return [""] * len(passwords)

        binary_data = bytes.fromhex(hex_data)
        results = []
        ptr = 0

        for pwd in passwords:
            if ptr + 32 >= len(binary_data):
                results.append("")
                continue

            try:
                # Extract components
                salt = binary_data[ptr:ptr + 16]
                iv = binary_data[ptr + 16:ptr + 32]
                
                # Get the ciphertext
                remaining = len(binary_data) - ptr - 32
                ciphertext = binary_data[ptr + 32:ptr + 32 + remaining]
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
                blocks_needed = (total_size + 15) // 16 * 16
                ptr += 32 + blocks_needed
                
            except Exception as e:
                print(f"Decoding error in layer: {e}")
                results.append("")
                ptr += 32 + self.block_size

        return results