import numpy as np
import hashlib

# Convert bytes → bits
def bytes_to_bits(byte_data):
    bits = []
    for byte in byte_data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

# Convert bits → bytes
def bits_to_bytes(bits):
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i+j < len(bits):
                byte = (byte << 1) | bits[i+j]
        byte_array.append(byte)
    return bytes(byte_array)

# Set least significant bit
def set_lsb(value, bit):
    return (value & 0xFE) | bit

# Get least significant bit
def get_lsb(value):
    return value & 1

def set_msb(value, bit):
    return (value & 0x7F) | (bit << 7)

def get_msb(value):
    return (value >> 7) & 1

# Get new pixel positions after upscaling
def get_new_pixel_positions(orig_shape, scale):
    H, W = orig_shape[:2]
    new_positions = []
    
    #new positions are not divisible by original position % scaling factor
    for row in range(H*scale):
        for col in range(W*scale):
            if row % scale != 0 or col % scale != 0:
                new_positions.append((row, col))
    return new_positions

# Generate dynamic XOR key from new pixel positions
def generate_xor_key(new_positions, message_length):
    pos_bytes = bytearray()
    for row, col in new_positions:
        pos_bytes += row.to_bytes(2,'big') + col.to_bytes(2,'big')

    # Hash positions
    hash_bytes = hashlib.sha256(pos_bytes).digest()  # 32 bytes

    # Repeat to match message length in bits
    key_bits = bytes_to_bits(hash_bytes)
    repeats = (message_length // len(key_bits)) + 1
    return (key_bits * repeats)[:message_length]
