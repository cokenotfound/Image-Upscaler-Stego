import io
import logging
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from embed import embed_image_lsb, embed_text_lsb
from extract import extract_image_lsb, extract_text_lsb

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stego-upscale")

app = FastAPI(
    title="Stego-Upscale AI API",
    description="FastAPI Backend for Real-ESRGAN Image Upscaling and LSB Steganography with XOR Encryption",
    version="1.0.0",
)

# CORS Configuration for Browser Extensions and Local Web Apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Global Real-ESRGAN model holder
_model = None
_model_mode = "uninitialized"


def get_upscaler_model():
    """
    Initializes and caches the Real-ESRGAN model.
    Tries NVIDIA discrete GPU (gpuid=1), then integrated GPU (gpuid=0), then CPU (gpuid=-1).
    Uses tilesize=0 (auto) for maximum compatibility.
    """
    global _model, _model_mode
    if _model is not None:
        return _model

    try:
        from realesrgan_ncnn_py import Realesrgan

        # Try GPUs with auto tilesize (tilesize=0)
        # GPU 1: Discrete GPU (NVIDIA RTX 3050)
        # GPU 0: Integrated GPU (AMD Radeon)
        for gid, name in [(1, "NVIDIA GeForce RTX (gpuid=1)"), (0, "AMD / Default GPU (gpuid=0)"), (-1, "CPU (gpuid=-1)")]:
            try:
                _model = Realesrgan(gpuid=gid, model=0, tilesize=0)
                _model_mode = f"Real-ESRGAN on {name}"
                logger.info(f"Real-ESRGAN successfully loaded on {_model_mode}")
                return _model
            except Exception as ex:
                logger.warning(f"Real-ESRGAN on {name} failed: {ex}")

        _model_mode = "Bicubic Fallback (OpenCV)"
        _model = "fallback"
        return _model

    except ImportError:
        logger.warning("realesrgan_ncnn_py not found. Using high-quality Bicubic 4x upscaling.")
        _model_mode = "Bicubic Fallback (OpenCV)"
        _model = "fallback"
        return _model


def upscale_image(image: np.ndarray, target_scale: int = 4) -> tuple[np.ndarray, int]:
    """
    Upscales an image using Real-ESRGAN or OpenCV interpolation fallback.
    Returns (upscaled_image, actual_scale_factor).
    """
    model = get_upscaler_model()
    if model and model != "fallback":
        try:
            logger.info("Processing image with Real-ESRGAN AI model...")
            upscaled = model.process_cv2(image)
            achieved_scale = max(2, round(upscaled.shape[0] / image.shape[0]))
            return upscaled, achieved_scale
        except Exception as e:
            logger.error(f"Error during Real-ESRGAN process_cv2: {e}. Falling back to Bicubic interpolation.")

    # High-quality bicubic 4x upscale fallback
    h, w = image.shape[:2]
    upscaled = cv2.resize(image, (w * target_scale, h * target_scale), interpolation=cv2.INTER_CUBIC)
    return upscaled, target_scale


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Stego-Upscale AI backend...")
    get_upscaler_model()


@app.get("/")
async def root():
    return {
        "name": "Stego-Upscale AI API",
        "status": "online",
        "model_mode": _model_mode,
        "endpoints": {
            "health": "/health",
            "encode": "POST /encode (multipart/form-data)",
            "decode": "POST /decode (multipart/form-data)",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_mode": _model_mode,
        "version": "1.0.0",
    }


@app.post("/encode")
async def encode(
    payload_type: str = Form("text"),
    cover_image: UploadFile = File(...),
    secret_text: Optional[str] = Form(""),
    secret_image: Optional[UploadFile] = File(None),
    scale: int = Form(4),
):
    """
    Upscales the cover image and embeds either secret text or a secret image
    into the upscaled pixels using LSB steganography and dynamic XOR encryption.
    Returns the lossless PNG stego image.
    """
    try:
        # 1. Read and decode cover image
        cover_bytes = await cover_image.read()
        if not cover_bytes:
            raise HTTPException(status_code=400, detail="Cover image file is empty.")

        cover_np = np.frombuffer(cover_bytes, np.uint8)
        cover_img = cv2.imdecode(cover_np, cv2.IMREAD_COLOR)

        if cover_img is None:
            raise HTTPException(status_code=400, detail="Could not decode cover image. Please provide a valid PNG or JPEG.")

        # 2. AI Upscaling
        logger.info(f"Upscaling cover image of shape {cover_img.shape}...")
        upscaled_cover, actual_scale = upscale_image(cover_img, target_scale=scale)
        logger.info(f"Upscaled image shape: {upscaled_cover.shape} (scale: {actual_scale}x)")

        # 3. Embed Payload
        if payload_type.lower() == "text":
            if not secret_text:
                raise HTTPException(status_code=400, detail="Secret text is empty.")
            logger.info(f"Embedding {len(secret_text)} characters of secret text...")
            stego_result = embed_text_lsb(upscaled_cover, secret_text, scale=actual_scale)

        elif payload_type.lower() == "image":
            if not secret_image:
                raise HTTPException(status_code=400, detail="Secret image file is required for image payload.")

            sec_bytes = await secret_image.read()
            if not sec_bytes:
                raise HTTPException(status_code=400, detail="Secret image file is empty.")

            sec_np = np.frombuffer(sec_bytes, np.uint8)
            sec_img = cv2.imdecode(sec_np, cv2.IMREAD_COLOR)

            if sec_img is None:
                raise HTTPException(status_code=400, detail="Could not decode secret image file.")

            logger.info(f"Embedding secret image of shape {sec_img.shape}...")
            stego_result = embed_image_lsb(upscaled_cover, sec_img, scale=actual_scale)

        else:
            raise HTTPException(status_code=400, detail=f"Invalid payload_type '{payload_type}'. Must be 'text' or 'image'.")

        # 4. Return lossless PNG image
        is_success, buffer = cv2.imencode(".png", stego_result)
        if not is_success:
            raise HTTPException(status_code=500, detail="Failed to encode stego image to PNG format.")

        return Response(
            content=buffer.tobytes(),
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="stego_upscaled.png"'},
        )

    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error during encoding: {ve}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(ve)})
    except Exception as e:
        logger.exception("Unexpected error in /encode")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": f"Internal server error: {str(e)}"})


@app.post("/decode")
async def decode(
    extract_type: str = Form("text"),
    stego_image: UploadFile = File(...),
    scale: int = Form(4),
):
    """
    Extracts and decrypts secret text or secret image from an upscaled stego image.
    Tries the provided scale first, and automatically checks alternate scale factors (2, 4) if needed.
    """
    try:
        stego_bytes = await stego_image.read()
        if not stego_bytes:
            raise HTTPException(status_code=400, detail="Stego image file is empty.")

        stego_np = np.frombuffer(stego_bytes, np.uint8)
        stego_img = cv2.imdecode(stego_np, cv2.IMREAD_COLOR)

        if stego_img is None:
            raise HTTPException(status_code=400, detail="Could not decode stego image. Make sure to upload a valid PNG.")

        # Candidate scales to try: specified scale, then 2, 4
        scales_to_try = [scale]
        for s in [2, 4]:
            if s not in scales_to_try:
                scales_to_try.append(s)

        if extract_type.lower() == "text":
            logger.info("Extracting secret text from stego image...")
            result_text = None
            last_err = None

            for s in scales_to_try:
                try:
                    text = extract_text_lsb(stego_img, scale=s)
                    if text:
                        result_text = text
                        logger.info(f"Successfully extracted text at scale={s}")
                        break
                except Exception as ex:
                    last_err = ex

            if result_text is None:
                if last_err:
                    raise ValueError(f"Could not extract secret text ({last_err})")
                raise HTTPException(status_code=400, detail="No secret text found or data is corrupted.")

            return JSONResponse(content={"success": True, "text": result_text})

        elif extract_type.lower() == "image":
            logger.info("Extracting secret image from stego image...")
            result_img = None
            for s in scales_to_try:
                try:
                    img = extract_image_lsb(stego_img, scale=s)
                    if img is not None:
                        result_img = img
                        logger.info(f"Successfully extracted image at scale={s}")
                        break
                except Exception:
                    continue

            if result_img is None:
                raise HTTPException(status_code=400, detail="No secret image found or data is corrupted.")

            is_success, buffer = cv2.imencode(".png", result_img)
            if not is_success:
                raise HTTPException(status_code=500, detail="Failed to encode extracted secret image to PNG.")

            return Response(
                content=buffer.tobytes(),
                media_type="image/png",
                headers={"Content-Disposition": 'attachment; filename="extracted_secret.png"'},
            )

        else:
            raise HTTPException(status_code=400, detail=f"Invalid extract_type '{extract_type}'. Must be 'text' or 'image'.")

    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Extraction error: {ve}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(ve)})
    except Exception as e:
        logger.exception("Unexpected error in /decode")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": f"Internal server error: {str(e)}"})
