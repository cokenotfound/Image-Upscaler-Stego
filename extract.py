import numpy as np
from functions import *

def extract_text_lsb(stego_image: np.ndarray, scale: int):

    Height, Width, Colours = stego_image.shape

    # Step 1: Get the new pixel positions used for embedding
    new_pixels = get_new_pixel_positions((Height//scale, Width//scale), scale)

    # Step 2: Estimate maximum number of bits embedded
    max_bits = len(new_pixels) * 3  # 3 channels per pixel

    # Step 3: Generate dynamic XOR key based on new pixel positions
    xor_key_bits = generate_xor_key(new_pixels, max_bits)

    # Step 4: Extract LSBs from new pixels
    extracted_bits = []
    for row, col in new_pixels:
        for ch in range(3):  # BGR channels
            if len(extracted_bits) < max_bits:
                extracted_bits.append(get_lsb(stego_image[row, col, ch]))

    # Step 5: XOR decryption
    decrypted_bits = [b ^ k for b, k in zip(extracted_bits, xor_key_bits)]

    # Step 6: Convert bits to bytes
    decrypted_bytes = bits_to_bytes(decrypted_bits)

    # Step 7: Extract length prefix and recover the hidden text
    message_length = int.from_bytes(decrypted_bytes[:4], 'big')
    secret_text = decrypted_bytes[4:4+message_length].decode('utf-8')

    return secret_text

import numpy as np
from functions import *

def extract_text_msb(stego_image: np.ndarray, scale: int):
    Height, Width, Colours = stego_image.shape

    # Step 1: Get the new pixel positions used for embedding
    new_pixels = get_new_pixel_positions((Height//scale, Width//scale), scale)

    # Step 2: Estimate maximum number of bits embedded
    max_bits = len(new_pixels) * 3  # 3 channels per pixel

    # Step 3: Generate dynamic XOR key based on new pixel positions
    xor_key_bits = generate_xor_key(new_pixels, max_bits)

    # Step 4: Extract MSBs from new pixels
    extracted_bits = []
    for row, col in new_pixels:
        for ch in range(3):  # BGR channels
            if len(extracted_bits) < max_bits:
                extracted_bits.append(get_msb(stego_image[row, col, ch]))

    # Step 5: XOR decryption
    decrypted_bits = [b ^ k for b, k in zip(extracted_bits, xor_key_bits)]

    # Step 6: Convert bits to bytes
    decrypted_bytes = bits_to_bytes(decrypted_bits)

    # Step 7: Extract length prefix and recover the hidden text
    message_length = int.from_bytes(decrypted_bytes[:4], 'big')
    secret_text = decrypted_bytes[4:4+message_length].decode('utf-8')

    return secret_text
