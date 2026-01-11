import cv2
import os
from embed import embed_text_lsb
from extract import extract_text_lsb
import numpy as np

# -----------------------------
# Configuration / Inputs
# -----------------------------

input_image_path = r"C:\Aakash PDFs\Image Upscale Stego\samples\abhiram.png"

# Extract just the filename without directory
filename = os.path.basename(input_image_path)      # 'myphoto.png'
# Extract name without extension
name, ext = os.path.splitext(filename)            # name='myphoto', ext='.png'

# Create output filename
stego_image_path = f"upscaled_{name}{ext}"  

scale_factor = 4                        # Upscale factor
secret_message = input("Enter the secret message to hide: ")

# -----------------------------
# Step 1: Load image
# -----------------------------
original_image = cv2.imread(input_image_path)
if original_image is None:
    raise FileNotFoundError(f"Could not load image at {input_image_path}")

# -----------------------------
# Step 2: Upscale image using OpenCV
# -----------------------------
height, width = original_image.shape[:2]
new_size = (width * scale_factor, height * scale_factor)

# Use cubic interpolation for smooth upscaling
upscaled_image = cv2.resize(original_image, new_size, interpolation=cv2.INTER_CUBIC)

# -----------------------------
# Step 3: Embed secret text
# -----------------------------
stego_image = embed_text_lsb(upscaled_image, secret_message, scale_factor)

# -----------------------------
# Step 4: Save stego image
# -----------------------------
cv2.imwrite(stego_image_path, stego_image)
print(f"Stego image saved at: {stego_image_path}")

# -----------------------------
# Step 5: Extract hidden text
# -----------------------------
stego_image_loaded = cv2.imread(stego_image_path)
extracted_message = extract_text_lsb(stego_image_loaded, scale_factor)
print("Extracted Message:", extracted_message)
