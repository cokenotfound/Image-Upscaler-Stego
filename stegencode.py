import cv2
import os
from realesrgan_ncnn_py import Realesrgan
from embed import embed_text_lsb

# -----------------------------
# Inputs
# -----------------------------
input_image_path = r"C:\Aakash PDFs\Image Upscale Stego\samples\abhiram.png"
secret_message = input("Enter the secret message to hide: ")

filename = os.path.basename(input_image_path)
name, ext = os.path.splitext(filename)
stego_image_path = f"C:/Aakash PDFs/Image Upscale Stego/samples/upscaled_esrgan_{name}{ext}"

# -----------------------------
# Load original image
# -----------------------------
original_image = cv2.imread(input_image_path)
if original_image is None:
    raise FileNotFoundError(f"Could not load image at {input_image_path}")

# -----------------------------
# Load RealESRGAN (GPU)
# -----------------------------
print("Loading RealESRGAN on GPU...")
model = Realesrgan(gpuid=0, model=4, tilesize=192)  # GPU + tiling
print("Upscaling image...")
upscaled_image = model.process_cv2(original_image)

print(f"Upscaling complete.")

# -----------------------------
# Embed secret message
# -----------------------------
print("Embedding secret message...")
stego_image = embed_text_lsb(upscaled_image, secret_message, scale=4)

# -----------------------------
# Save stego image
# -----------------------------
os.makedirs(os.path.dirname(stego_image_path), exist_ok=True)
cv2.imwrite(stego_image_path, stego_image)

print(f"Stego image saved at: {stego_image_path}")
print("DONE.")
