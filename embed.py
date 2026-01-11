import numpy as np
from functions import *

def embed_text_lsb(image: np.ndarray, text: str, scale: int):
    Height, Width, Colours = image.shape
    # Convert text to bytes with 4-byte length prefix
    text_bytes = text.encode('utf-8')
    length_prefix = len(text_bytes).to_bytes(4, 'big')
    data_bytes = length_prefix + text_bytes
    bitstream = bytes_to_bits(data_bytes)
    
    # Get new pixels and dynamic XOR key
    new_pixels = get_new_pixel_positions((Height//scale, Width//scale), scale)
    xor_key_bits = generate_xor_key(new_pixels, len(bitstream))
    
    # XOR encryption
    encrypted_bits = [b ^ k for b,k in zip(bitstream, xor_key_bits)]
    
    # Embed into LSBs of new pixels
    stego_image = image.copy()
    bit_idx = 0
    for row,col in new_pixels:
        if bit_idx >= len(encrypted_bits):
            break
        for ch in range(3):  # BGR channels in OpenCV
            if bit_idx < len(encrypted_bits):
                stego_image[row,col,ch] = set_lsb(stego_image[row,col,ch], encrypted_bits[bit_idx])
                bit_idx += 1
    return stego_image

def embed_text_msb(image: np.ndarray, text: str, scale: int):
    Height, Width, Colours = image.shape

    # Convert text to bytes with 4-byte length prefix
    text_bytes = text.encode('utf-8')
    length_prefix = len(text_bytes).to_bytes(4, 'big')
    data_bytes = length_prefix + text_bytes
    bitstream = bytes_to_bits(data_bytes)

    # Get new pixels and dynamic XOR key
    new_pixels = get_new_pixel_positions((Height//scale, Width//scale), scale)
    xor_key_bits = generate_xor_key(new_pixels, len(bitstream))

    # XOR encryption
    encrypted_bits = [b ^ k for b, k in zip(bitstream, xor_key_bits)]

    # Embed into MSBs of new pixels
    stego_image = image.copy()
    bit_idx = 0
    for row, col in new_pixels:
        if bit_idx >= len(encrypted_bits):
            break
        for ch in range(3):  # BGR channels in OpenCV
            if bit_idx < len(encrypted_bits):
                stego_image[row, col, ch] = set_msb(stego_image[row, col, ch], encrypted_bits[bit_idx])
                bit_idx += 1
    return stego_image

