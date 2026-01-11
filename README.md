# Image Upscale Steganography with AI & SHA-256

## Abstract
This project implements a secure, AI-powered image steganography system designed to hide secret messages within digital images. Unlike traditional steganography tools that work on static images, this application first utilizes **Real-ESRGAN (AI Super-Resolution)** to upscale low-resolution inputs by 4x. This process not only enhances visual quality but also significantly increases the pixel capacity available for hiding data.

The system features a **Streamlit-based Graphical User Interface (GUI)** for seamless interaction. Security is enforced via a dual-layer approach: **Least Significant Bit (LSB)** manipulation for invisibility, combined with **SHA-256 XOR encryption**. Uniquely, the encryption key is derived deterministically from the upscaled image's pixel data, ensuring that the message can only be decrypted if the exact image structure is preserved.

## Technologies Used
- **Python 3.12**: Core programming language.
- **Streamlit**: Interactive Web GUI for Drag & Drop, Side-by-Side comparison, and Progress Bar.
- **Real-ESRGAN (ncnn-py)**: High-performance AI model for 4x image upscaling (GPU accelerated).
- **OpenCV (cv2)**: Advanced image processing and bitwise pixel manipulation.
- **NumPy**: Efficient high-speed array operations for pixel flattening and reshaping.
- **Hashlib (SHA-256)**: Cryptographic hashing for generating deterministic encryption keys.

## Key Features
- **AI-Powered Upscaling**: Automatically transforms low-res images into high-resolution (4x) versions using Real-ESRGAN before embedding data.
- **Modern Web GUI**: A clean, browser-based interface (Streamlit) that eliminates the need for command-line usage.
- **Dynamic Security**: The encryption key is dynamically generated from the image pixels themselves; if the image is altered, the key breaks, and the message remains secure.
- **Visual Comparison**: Side-by-side preview of the "Original Low-Res" vs. "Final Stego-Image" to verify visual quality.
- **Real-Time Feedback**: Interactive progress bars for long-running tasks like AI inference and bitwise embedding.
- **Lossless Processing**: Uses PNG format strictly to prevent compression artifacts from destroying the hidden message.

## Directory Structure
Based on the current project setup, the folder structure is as follows:

```text
/StegoUpscaleProject
├── .gitignore            # Git configuration
├── app.py                # Main Streamlit application (Run this file)
├── checkmodel.py         # Utility to verify AI models
├── embed.py              # (Optional/Legacy) Script for embedding
├── extract.py            # (Optional/Legacy) Script for extracting
├── functions.py          # Helper functions
├── main.py               # (Optional) Alternative entry point
├── README.md             # Project documentation
├── stegencode.py         # Core logic for LSB embedding & Encryption
├── stegdecode.py         # Core logic for LSB extraction & Decryption
├── samples/              # Folder containing test images
└── weights/              # Folder for Real-ESRGAN model weights
```

## Implementation

### 1. Installation
First, ensure you have Python installed, then install the required dependencies:

```bash
pip install streamlit opencv-python-headless numpy realesrgan-ncnn-py
```

### 2. Running the App

Launch the graphical interface using Streamlit from your terminal:

```bash
streamlit run app.py
```
