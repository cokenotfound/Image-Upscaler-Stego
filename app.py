import streamlit as st
import cv2
import numpy as np
import time
from realesrgan_ncnn_py import Realesrgan

# --- IMPORTS ---
try:
    from embed import embed_text_lsb
    from extract import extract_text_lsb
except ImportError:
    st.error("⚠️ Error: Could not find 'embed.py' or 'extract.py'. Please check your folder.")
    st.stop()

st.set_page_config(page_title="Stego-Upscale AI", layout="wide")

st.sidebar.title("Stego-Upscale AI")
app_mode = st.sidebar.radio("Select Mode:", ["Encode (Upscale + Hide)", "Decode (Extract)"])

# ==========================================
# MODE 1: ENCODE (Upscale -> Embed)
# ==========================================
if app_mode == "Encode (Upscale + Hide)":
    st.header("🔒 Encode: Upscale Image & Hide Text")

    col_input, col_settings = st.columns([1, 1])
    
    with col_input:
        uploaded_file = st.file_uploader("1. Upload Low-Res Image", type=['png', 'jpg', 'jpeg'])
    
    with col_settings:
        secret_message = st.text_area("2. Enter Secret Message", "My Secret Text")
        run_btn = st.button("🚀 Run AI & Encrypt", type="primary")

    # --- PROCESS LOGIC ---
    if run_btn:
        if uploaded_file and secret_message:
            
            # 1. INITIALIZE PROGRESS BAR (0%)
            my_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("⏳ Step 1: Loading image into memory...")
            
            try:
                # Load Image
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                original_image = cv2.imdecode(file_bytes, 1) # BGR Format
                
                # Update Progress -> 20%
                my_bar.progress(20)
                status_text.text("🚀 Step 2: AI Upscaling in progress (Please wait)...")
                
                # --- AI UPSCALING ---
                model = Realesrgan(gpuid=0, model=4, tilesize=192)
                upscaled_image = model.process_cv2(original_image)
                
                # Update Progress -> 70%
                my_bar.progress(70)
                status_text.text("🔒 Step 3: Embedding secret text into pixels...")

                # --- EMBEDDING ---
                stego_image = embed_text_lsb(upscaled_image, secret_message, scale=4)
                
                # Update Progress -> 100%
                my_bar.progress(100)
                status_text.success("✅ Processing Complete!")

                # --- DISPLAY RESULTS ---
                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Original")
                    # FIX: Changed use_container_width=True to width="stretch"
                    st.image(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB), width="stretch")
                with c2:
                    st.subheader("Result (Stego)")
                    # FIX: Changed use_container_width=True to width="stretch"
                    st.image(cv2.cvtColor(stego_image, cv2.COLOR_BGR2RGB), width="stretch")
                    
                    # Download Button
                    is_success, buffer = cv2.imencode(".png", stego_image)
                    st.download_button(
                        label="💾 Download Output Image",
                        data=buffer.tobytes(),
                        file_name="upscaled_stego.png",
                        mime="image/png"
                    )

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload an image and enter text first.")

# ==========================================
# MODE 2: DECODE (Extract)
# ==========================================
elif app_mode == "Decode (Extract)":
    st.header("🔓 Decode: Extract Hidden Message")

    uploaded_stego = st.file_uploader("Upload Stego-Image", type=['png'])
    extract_btn = st.button("🔍 Extract Text")

    if extract_btn and uploaded_stego:
        
        # 1. INITIALIZE PROGRESS BAR (0%)
        my_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("⏳ Reading image data...")

        try:
            file_bytes = np.asarray(bytearray(uploaded_stego.read()), dtype=np.uint8)
            stego_image = cv2.imdecode(file_bytes, 1)
            
            # Update Progress -> 50%
            my_bar.progress(50)
            status_text.text("🔓 Decrypting LSB layers...")

            # --- EXTRACT LOGIC ---
            extracted_message = extract_text_lsb(stego_image, 4)
            
            # Update Progress -> 100%
            my_bar.progress(100)
            status_text.success("Done!")
            
            st.divider()
            if extracted_message:
                st.success("Message Found!")
                st.text_area("Decrypted Text:", extracted_message, height=150)
            else:
                st.warning("No message found. Make sure this is the correct image.")
        
        except Exception as e:
            st.error(f"Extraction Error: {e}")