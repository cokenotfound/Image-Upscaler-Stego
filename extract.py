import cv2
import numpy as np
from functions import (
    bits_to_bytes,
    get_lsb,
    get_msb,
    get_new_pixel_positions,
    generate_xor_key,
)


def extract_text_lsb(stego_image: np.ndarray, scale: int = 4) -> str:
    """
    Extracts and decrypts a hidden UTF-8 text string from the LSBs of an upscaled stego image.
    """
    Height, Width, _ = stego_image.shape
    new_pixels = get_new_pixel_positions((Height // scale, Width // scale), scale)
    max_bits = len(new_pixels) * 3

    if max_bits < 32:
        raise ValueError("Stego image is too small to contain a valid payload header.")

    # Generate dynamic XOR key based on pixel positions
    xor_key_bits = generate_xor_key(new_pixels, max_bits)

    # Extract LSBs from new pixels
    extracted_bits = []
    for row, col in new_pixels:
        for ch in range(3):  # BGR channels
            if len(extracted_bits) < max_bits:
                extracted_bits.append(get_lsb(stego_image[row, col, ch]))

    # XOR Decryption
    decrypted_bits = [b ^ k for b, k in zip(extracted_bits, xor_key_bits)]
    decrypted_bytes = bits_to_bytes(decrypted_bits)

    if len(decrypted_bytes) < 4:
        raise ValueError("Insufficient data extracted from image.")

    # Read 4-byte big-endian message length prefix
    message_length = int.from_bytes(decrypted_bytes[:4], 'big')
    if message_length <= 0 or message_length > (len(decrypted_bytes) - 4):
        raise ValueError("No hidden text message found or stego payload is corrupted.")

    secret_bytes = decrypted_bytes[4:4 + message_length]
    secret_text = secret_bytes.decode('utf-8', errors='replace')
    return secret_text


def extract_image_lsb(stego_image: np.ndarray, scale: int = 4) -> np.ndarray:
    """
    Extracts and decrypts a hidden secret image from the LSBs of an upscaled stego image.
    Returns the decoded image as a NumPy BGR array.
    """
    Height, Width, _ = stego_image.shape
    new_pixels = get_new_pixel_positions((Height // scale, Width // scale), scale)
    max_bits = len(new_pixels) * 3

    if max_bits < 32:
        raise ValueError("Stego image is too small to contain a valid payload header.")

    xor_key_bits = generate_xor_key(new_pixels, max_bits)

    extracted_bits = []
    for row, col in new_pixels:
        for ch in range(3):
            if len(extracted_bits) < max_bits:
                extracted_bits.append(get_lsb(stego_image[row, col, ch]))

    decrypted_bits = [b ^ k for b, k in zip(extracted_bits, xor_key_bits)]
    decrypted_bytes = bits_to_bytes(decrypted_bits)

    if len(decrypted_bytes) < 4:
        raise ValueError("Insufficient data extracted from image.")

    message_length = int.from_bytes(decrypted_bytes[:4], 'big')
    if message_length <= 0 or message_length > (len(decrypted_bytes) - 4):
        raise ValueError("No hidden image found or stego payload is corrupted.")

    img_bytes = decrypted_bytes[4:4 + message_length]
    img_np = np.frombuffer(img_bytes, np.uint8)
    sec_img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    if sec_img is None:
        raise ValueError("Failed to decode extracted bytes as a valid image format.")

    return sec_img


def extract_text_msb(stego_image: np.ndarray, scale: int = 4) -> str:
    """
    Auxiliary extraction of text from MSB layers.
    """
    Height, Width, _ = stego_image.shape
    new_pixels = get_new_pixel_positions((Height // scale, Width // scale), scale)
    max_bits = len(new_pixels) * 3

    if max_bits < 32:
        raise ValueError("Stego image is too small to contain a valid header.")

    xor_key_bits = generate_xor_key(new_pixels, max_bits)

    extracted_bits = []
    for row, col in new_pixels:
        for ch in range(3):
            if len(extracted_bits) < max_bits:
                extracted_bits.append(get_msb(stego_image[row, col, ch]))

    decrypted_bits = [b ^ k for b, k in zip(extracted_bits, xor_key_bits)]
    decrypted_bytes = bits_to_bytes(decrypted_bits)

    message_length = int.from_bytes(decrypted_bytes[:4], 'big')
    if message_length <= 0 or message_length > (len(decrypted_bytes) - 4):
        raise ValueError("No hidden text message found in MSBs.")

    return decrypted_bytes[4:4 + message_length].decode('utf-8', errors='replace')
