import cv2
import numpy as np
from functions import (
    bytes_to_bits,
    set_lsb,
    set_msb,
    get_new_pixel_positions,
    generate_xor_key,
)


def embed_text_lsb(image: np.ndarray, text: str, scale: int = 4) -> np.ndarray:
    """
    Embeds a secret UTF-8 string into the LSBs of upscaled pixels using XOR encryption.
    """
    Height, Width, _ = image.shape
    text_bytes = text.encode('utf-8')
    length_prefix = len(text_bytes).to_bytes(4, 'big')
    data_bytes = length_prefix + text_bytes
    bitstream = bytes_to_bits(data_bytes)

    # Get newly generated pixel positions from the upscale process
    new_pixels = get_new_pixel_positions((Height // scale, Width // scale), scale)
    total_capacity_bits = len(new_pixels) * 3  # 3 color channels (BGR)

    if len(bitstream) > total_capacity_bits:
        max_bytes = (total_capacity_bits // 8) - 4
        raise ValueError(
            f"Payload too large: message requires {len(text_bytes)} bytes, "
            f"but image capacity is {max_bytes} bytes."
        )

    # Dynamic XOR encryption based on pixel positions
    xor_key_bits = generate_xor_key(new_pixels, len(bitstream))
    encrypted_bits = [b ^ k for b, k in zip(bitstream, xor_key_bits)]

    stego_image = image.copy()
    bit_idx = 0
    total_bits = len(encrypted_bits)

    for row, col in new_pixels:
        if bit_idx >= total_bits:
            break
        for ch in range(3):  # BGR channels
            if bit_idx < total_bits:
                stego_image[row, col, ch] = set_lsb(stego_image[row, col, ch], encrypted_bits[bit_idx])
                bit_idx += 1

    return stego_image


def embed_image_lsb(image: np.ndarray, secret_img: np.ndarray, scale: int = 4) -> np.ndarray:
    """
    Embeds a secret image (encoded as lossless PNG) into the LSBs of upscaled pixels
    using XOR encryption.
    """
    is_success, buffer = cv2.imencode('.png', secret_img)
    if not is_success:
        raise ValueError("Could not encode secret image to PNG format.")

    img_bytes = buffer.tobytes()
    length_prefix = len(img_bytes).to_bytes(4, 'big')
    data_bytes = length_prefix + img_bytes
    bitstream = bytes_to_bits(data_bytes)

    Height, Width, _ = image.shape
    new_pixels = get_new_pixel_positions((Height // scale, Width // scale), scale)
    total_capacity_bits = len(new_pixels) * 3

    if len(bitstream) > total_capacity_bits:
        max_bytes = (total_capacity_bits // 8) - 4
        raise ValueError(
            f"Secret image too large: compressed payload is {len(img_bytes)} bytes, "
            f"exceeding cover image capacity of {max_bytes} bytes."
        )

    xor_key_bits = generate_xor_key(new_pixels, len(bitstream))
    encrypted_bits = [b ^ k for b, k in zip(bitstream, xor_key_bits)]

    stego_image = image.copy()
    bit_idx = 0
    total_bits = len(encrypted_bits)

    for row, col in new_pixels:
        if bit_idx >= total_bits:
            break
        for ch in range(3):
            if bit_idx < total_bits:
                stego_image[row, col, ch] = set_lsb(stego_image[row, col, ch], encrypted_bits[bit_idx])
                bit_idx += 1

    return stego_image


def embed_text_msb(image: np.ndarray, text: str, scale: int = 4) -> np.ndarray:
    """
    Auxiliary embedding using MSB manipulation and XOR encryption.
    """
    Height, Width, _ = image.shape
    text_bytes = text.encode('utf-8')
    length_prefix = len(text_bytes).to_bytes(4, 'big')
    data_bytes = length_prefix + text_bytes
    bitstream = bytes_to_bits(data_bytes)

    new_pixels = get_new_pixel_positions((Height // scale, Width // scale), scale)
    total_capacity_bits = len(new_pixels) * 3

    if len(bitstream) > total_capacity_bits:
        max_bytes = (total_capacity_bits // 8) - 4
        raise ValueError(f"Payload too large for image capacity ({max_bytes} bytes).")

    xor_key_bits = generate_xor_key(new_pixels, len(bitstream))
    encrypted_bits = [b ^ k for b, k in zip(bitstream, xor_key_bits)]

    stego_image = image.copy()
    bit_idx = 0
    total_bits = len(encrypted_bits)

    for row, col in new_pixels:
        if bit_idx >= total_bits:
            break
        for ch in range(3):
            if bit_idx < total_bits:
                stego_image[row, col, ch] = set_msb(stego_image[row, col, ch], encrypted_bits[bit_idx])
                bit_idx += 1

    return stego_image
