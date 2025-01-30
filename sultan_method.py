# sultan_method.py
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from stegano import lsb
import os

class SimpleAESLSB:
    def __init__(self, password):
        self.salt = b'sultan_2023_salt'  # Fixed salt per method
        self.key = PBKDF2(password, self.salt, dkLen=32, count=100000)

    def encode(self, image_path, message, output_path):
        """Single-layer AES-256 + LSB"""
        # AES Encryption
        iv = os.urandom(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded = message + ' '*(16 - len(message)%16)
        ciphertext = iv + cipher.encrypt(padded.encode())
        
        # LSB Embedding
        lsb.hide(image_path, ciphertext.hex()).save(output_path)

    def decode(self, stego_path):
        """Extract and decrypt"""
        hex_data = lsb.reveal(stego_path)
        ciphertext = bytes.fromhex(hex_data)
        
        iv = ciphertext[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[16:]).decode().strip()
        
        return plaintext