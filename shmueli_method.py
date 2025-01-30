# shmueli_method.py (fixed)
import cv2
import numpy as np

class MaxEnergySeam:
    def __init__(self):
        self.END_MARKER = "11111111"  # Binary 0xFF terminator
        self.MAX_MESSAGE_LENGTH = 1000  # Safety limit

    def _calculate_energy(self, gray):
        """Calculate energy map using Scharr operator"""
        dx = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
        dy = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
        return cv2.magnitude(dx, dy)

    def _find_seam(self, energy):
        """Dynamic programming to find maximum energy seam"""
        h, w = energy.shape
        cum_energy = energy.copy()
        path = np.zeros_like(energy, dtype=int)

        # Forward pass
        for j in range(1, w):
            for i in range(h):
                offsets = [max(i - 1, 0), i, min(i + 1, h - 1)]
                prev_energies = cum_energy[offsets, j - 1]
                max_idx = np.argmax(prev_energies)
                cum_energy[i, j] += prev_energies[max_idx]
                path[i, j] = offsets[max_idx]

        # Backtracking
        seam = []
        i = np.argmax(cum_energy[:, -1])
        for j in reversed(range(w)):
            seam.append((i, j))
            i = path[i, j]

        return [ (x, y) for (x, y) in reversed(seam) ]

    def encode(self, image_path, message, output_path):
        """Embed message along high-energy seams"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Invalid image path")

        # Validate message
        if not all(ord(c) < 128 for c in message):
            raise ValueError("Only ASCII characters supported")

        # Convert message to binary with end marker
        bin_msg = ''.join(f"{ord(c):08b}" for c in message) + self.END_MARKER
        bin_msg = bin_msg.ljust(len(bin_msg) + (8 - len(bin_msg) % 8), '0')

        # Calculate energy map
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        energy = self._calculate_energy(gray)

        # Find seam and embed
        seam = self._find_seam(energy)
        for idx, (i, j) in enumerate(seam):
            if idx >= len(bin_msg):
                break
            # Embed in LSB of all channels
            img[i, j, :] = [ (p & 0xFE) | int(bin_msg[idx]) for p in img[i, j] ]

        cv2.imwrite(output_path, img)

    def decode(self, stego_path):
        """Extract message from stego image"""
        img = cv2.imread(stego_path)
        if img is None:
            raise ValueError("Invalid stego image")

        # Calculate energy map
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        energy = self._calculate_energy(gray)

        # Find seam and extract bits
        seam = self._find_seam(energy)
        bin_str = ''.join(str(img[x, y, 0] & 1) for (x, y) in seam)

        # Find end marker
        end_idx = bin_str.find(self.END_MARKER)
        if end_idx == -1:
            end_idx = len(bin_str)

        # Convert binary to ASCII
        chars = []
        for i in range(0, end_idx, 8):
            byte_str = bin_str[i:i + 8]
            if len(byte_str) < 8:
                byte_str += '0' * (8 - len(byte_str))  # Pad with zeros
            try:
                chars.append(chr(int(byte_str, 2)))
            except:
                chars.append('�')  # Replacement character for invalid bytes

        return ''.join(chars).rstrip('\x00')