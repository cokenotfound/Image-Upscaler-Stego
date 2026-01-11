import cv2
from extract import extract_text_lsb

# -----------------------------
# Configuration
# -----------------------------
stego_image_path = r"C:\Aakash PDFs\Image Upscale Stego\samples\upscaled_esrgan_abhiram.png"
scale_factor = 4  

# -----------------------------
# Step 1: Load stego image
# -----------------------------
stego_image = cv2.imread(stego_image_path)
if stego_image is None:
    raise FileNotFoundError(f"Could not load image at {stego_image_path}")
print("Image Loaded. Extracting Message...")

# -----------------------------
# Step 2: Extract hidden text
# -----------------------------
extracted_message = extract_text_lsb(stego_image, scale_factor)
print("Extracted Message:", extracted_message)
