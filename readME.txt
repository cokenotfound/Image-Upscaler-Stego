# Image Upscale Steganography with SHA-256 XOR Encryption

## Project Overview

This project implements a secure image steganography system that hides secret messages inside images using a combination of **image upscaling**, **SHA-256 based encryption**, and **least significant bit (LSB) manipulation**.  

By using the upscaled image’s pixel data to generate a key, the system ensures that only the exact image (after upscaling) can decrypt the hidden message, adding an additional layer of security.

---

## Technologies Used

- **Python 3.12**  
- **OpenCV**: Image loading, resizing, and pixel manipulation  
- **NumPy**: Efficient array operations on image pixels  
- **hashlib (SHA-256)**: Generating a deterministic key from upscaled image pixels  
- **tqdm**: Progress bars during encoding and decoding  
- **PNG images**: Lossless format for LSB steganography  

> Optional: You can use a GAN-based model (e.g., Real-ESRGAN) instead of OpenCV for higher-quality upscaling.

---

## Pipeline / How It Works

### 1. Encoder Pipeline (Hide Secret Message)

1. **Load Original Image**  
   Read the input image using OpenCV.

2. **Upscale Image**  
   - Use **OpenCV cubic interpolation** or a **GAN model** to increase image resolution.  
   - Upscaling increases the available pixel positions for embedding.

3. **Generate SHA-256 Key**  
   - Flatten the upscaled image pixel values.  
   - Hash the pixel data using **SHA-256** to generate a deterministic key for encryption.

4. **Encrypt Secret Message**  
   - Convert the secret message to bytes.  
   - XOR the message bytes with the SHA-256 key (repeating/truncating the key as needed).

5. **Embed Encrypted Data via LSB**  
   - Flatten the image and embed encrypted message bits into the **least significant bit of each pixel channel**.  
   - Use `tqdm` for progress visualization.

6. **Save Stego Image**  
   - Save the resulting stego image as a **PNG** file to avoid compression artifacts.

---

### 2. Decoder Pipeline (Extract Secret Message)

1. **Load Stego Image**  
   Read the stego image using OpenCV.

2. **Upscale Original Image / Use Saved Upscaled Image**  
   Must match the encoder exactly to generate the same SHA-256 key.

3. **Generate SHA-256 Key**  
   Flatten the upscaled image pixels and hash with SHA-256.

4. **Extract LSB Bits**  
   Retrieve the bits from the least significant bit of each pixel channel.

5. **Decrypt Message**  
   Convert bits to bytes and XOR with the SHA-256 key to retrieve the original secret message.

---

## Features

- Deterministic encryption using **SHA-256 key derived from upscaled image**  
- Supports both **OpenCV interpolation** and optional **GAN-based upscaling**  
- LSB steganography combined with XOR encryption for **extra security**  
- Works for text of varying lengths, with a progress bar for user feedback  

---

## Limitations

- **Upscaling must be deterministic**: using different methods (GAN vs OpenCV) or parameters will change the SHA-256 key and prevent message extraction  
- **Message size limit**: The message cannot exceed the number of bits available in the image (1 bit per channel per pixel)  
- **PNG required**: Lossy formats like JPEG will corrupt hidden data  
- **Encryption key depends on upscaled image**: If the image is slightly altered, the secret cannot be recovered  

---

## Future Work

- Implement a **custom GAN model** to upscale images with higher quality while preserving reproducibility  
- Optimize **embedding strategy** to use multiple LSB layers for larger message capacity  
- Add **support for other file types** and larger payloads  
- Include **robustness against minor image modifications** (noise, cropping, etc.) using error-correcting codes  

---