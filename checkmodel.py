import torch

weight_path = r"C:\Aakash PDFs\Image Upscale Stego\weights\realesr-general-x4v3.pth"
weights = torch.load(weight_path, map_location='cpu')
print(weights.keys())
