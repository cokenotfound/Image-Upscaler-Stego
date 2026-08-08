# 🛡️ Stego-Upscale AI: Modern FastAPI Backend & Browser Extension

Comprehensive documentation of architectural upgrades, steganographic implementations, containerization, and browser extension integration.

---

## 🌟 Executive Summary of Changes

The project has been transitioned from a standalone Streamlit prototype into an asynchronous **FastAPI backend** paired with a **WebExtension (Firefox & Chrome)**, with hardware-accelerated **Real-ESRGAN Super-Resolution** and **LSB Steganography + Dynamic XOR Encryption**.

---

## 📁 Repository Structure & File Overview

```
Image-Upscaler-Stego/
├── 🚀 Backend API & AI Core
│   ├── main.py              # FastAPI server (Endpoints: /encode, /decode, /health, /)
│   ├── embed.py             # LSB & MSB Stego embedding (Text & Image payloads)
│   ├── extract.py           # LSB & MSB Stego extraction & XOR decryption
│   ├── functions.py         # Bit manipulation, Dynamic XOR Key Generator, SHA-256 hashing
│   ├── requirements.txt     # Backend dependencies (FastAPI, Uvicorn, OpenCV, Real-ESRGAN)
│   ├── start_backend.bat    # 1-Click Windows Batch launcher for .venv & Uvicorn
│   └── start_backend.ps1    # PowerShell launcher with automatic .venv setup
│
├── 🐳 Containerization
│   ├── Dockerfile           # Python 3.12-slim container with OpenCV system dependencies
│   └── docker-compose.yml   # Multi-stage Compose setup on port 8000 with healthchecks
│
├── 🧩 Browser Extension (Firefox & Chrome)
│   ├── extension_code/
│   │   ├── manifest.json    # Manifest V3 configuration with Sidebar and permissions
│   │   ├── popup.html       # Full-screen responsive AI Workstation UI
│   │   ├── popup.js         # API integration, Ctrl+V paste, drag & drop, tab handling
│   │   └── icon.png         # Extension badge icon (16x16, 48x48, 128x128)
│
├── 💾 Backups of Original Files
│   ├── embed_old.py         # Original embed functions preserved before modification
│   ├── extract_old.py       # Original extract functions preserved before modification
│   ├── main_old.py          # Original CLI test script preserved before modification
│   └── app.py               # Original Streamlit web application preserved
│
└── 📖 Documentation
    ├── README.md            # Original project documentation
    └── README2.md           # Comprehensive change summary & guide (this file)
```

---

## 🛠️ Detailed Breakdown of Completed Upgrades

### 1. ⚡ FastAPI Backend & Real-ESRGAN AI Acceleration ([main.py](main.py))
- **Asynchronous Endpoints**:
  - `POST /encode`: Accepts cover image + text/image payload. Upscales the image via Real-ESRGAN and embeds encrypted payload into LSBs.
  - `POST /decode`: Extracts secret text or downloads decoded secret image from stego PNG.
  - `GET /health`: Health status endpoint returning active hardware mode.
  - `GET /`: API metadata and route directory.
- **Dual-GPU Vulkan Probing**:
  - Automatically detects **NVIDIA GeForce RTX 3050 Laptop GPU** (`gpuid=1`), **AMD Radeon Graphics** (`gpuid=0`), and CPU Vulkan mode (`gpuid=-1`).
  - Configured with `model=0` (Real-ESRGAN x4plus) and auto-tile sizing (`tilesize=0`).
  - Fallback mechanism to high-quality OpenCV Bicubic 4x interpolation if GPU is unavailable.
- **CORS Support**: Configured `CORSMiddleware` with `allow_origins=["*"]` and exposed `Content-Disposition` headers for seamless browser extension downloads.

### 2. 🔐 Steganography & XOR Cryptography ([embed.py](embed.py), [extract.py](extract.py))
- **Text & Image Payload Embedding**:
  - `embed_text_lsb(image, text, scale)`: Converts text to UTF-8 with 4-byte length prefix, hashes new pixel coordinates with SHA-256 to generate a dynamic XOR keystream, encrypts bitstream, and embeds into LSBs of upscaled pixels.
  - `embed_image_lsb(image, secret_img, scale)`: Encodes secret image into lossless PNG byte buffer with 4-byte length prefix and embeds using the dynamic XOR keystream.
- **Decryption & Extraction**:
  - `extract_text_lsb(stego_image, scale)`: Recovers LSB bits from upscaled coordinates, decrypts using dynamic XOR key, and unpacks UTF-8 text.
  - `extract_image_lsb(stego_image, scale)`: Decrypts LSB bitstream and reconstructs OpenCV BGR image from recovered PNG bytes.

### 3. 🧩 Browser Extension UI & Workstation ([extension_code/](extension_code/))
- **Manifest V3 Specification**:
  - Fully compatible with **Firefox** and **Chrome/Edge**.
  - Added `browser_specific_settings` (`gecko.id`) for Firefox compatibility.
  - Added `sidebar_action` to allow permanent docking in Firefox Sidebar (`Ctrl + B`).
- **Responsive 2-Column AI Workstation**:
  - Responsive layout (`100vw / 100vh`) with center alignment.
  - Left column: Cover image picker, payload selector (Text / Image), secret inputs.
  - Right column: Real-time preview & output display with instant download/copy buttons.
- **📋 Instant Screenshot Paste (`Ctrl + V`)**:
  - Integrated global `paste` event handler: capture any screenshot (`Win + Shift + S`) and press `Ctrl + V` inside the tool to load it immediately without saving to disk.
- **❌ 1-Click Remove Cross (`✕`)**:
  - Added delete buttons directly on image preview containers to reset/clear images in one click.
- **🪟 Persistent Window & Sidebar Options**:
  - `⤢ Full Tab` button opens a persistent tab (or pinned tab) that **never auto-closes when clicking away**.
  - Closes on `Esc` key press or clicking `✕ Close`.

### 4. 📦 Virtual Environment & Automation Scripts
- **[.venv Support]**: Automated virtual environment creation and dependency tracking.
- **[start_backend.bat](start_backend.bat)**: 1-click batch launcher for Windows.
- **[start_backend.ps1](start_backend.ps1)**: PowerShell startup script.
- **[.gitignore](.gitignore)**: Updated to ignore `.venv`, `__pycache__`, and temporary artifacts.

### 5. 🐳 Docker & Containerization ([Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml))
- `Dockerfile` based on `python:3.12-slim` with OpenCV system libraries (`libgl1`, `libglib2.0-0`, `build-essential`).
- `docker-compose.yml` configured on port `8000:8000` with restart policies and healthchecks.

---

## 🚀 Quickstart Guide

### Option A: Local Python Backend (Recommended for NVIDIA GPU Acceleration)
```powershell
# 1-Click Launch:
.\start_backend.bat

# Or manual execution:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Docker Backend
```bash
docker compose up --build
```

---

## 🦊 Installing in Firefox

1. Open Firefox and type `about:debugging` in the address bar.
2. Click **This Firefox** on the left menu.
3. Under **Temporary Extensions**, click **Load Temporary Add-on...**
4. Select `extension_code/manifest.json`.
5. Open the extension from your toolbar, click **`⤢ Full Tab`** (or open via Firefox Sidebar with `Ctrl + B`), take a screenshot with `Win + Shift + S`, and paste with `Ctrl + V`!
