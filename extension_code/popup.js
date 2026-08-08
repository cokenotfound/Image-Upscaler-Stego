/**
 * Stego-Upscale AI - Browser Extension Controller (Firefox & Chrome Compatible)
 * Communicates with FastAPI backend (http://localhost:8000)
 */

const API_BASE = "http://localhost:8000";

// State
let activeTab = "encode";
let encodePayloadType = "text";
let decodeExtractType = "text";

let coverFileObj = null;
let secretImgFileObj = null;
let stegoFileObj = null;

let lastEncodedBlob = null;
let lastDecodedImageBlob = null;

// DOM Elements
const serverBadge = document.getElementById("server-badge");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const btnPopoutTab = document.getElementById("btn-popout-tab");
const btnCloseWindow = document.getElementById("btn-close-window");

const tabEncodeBtn = document.getElementById("tab-encode-btn");
const tabDecodeBtn = document.getElementById("tab-decode-btn");
const encodePanel = document.getElementById("encode-panel");
const decodePanel = document.getElementById("decode-panel");

const statusBanner = document.getElementById("status-banner");
const bannerIcon = document.getElementById("banner-icon");
const bannerMessage = document.getElementById("banner-message");

// Encode elements
const coverInput = document.getElementById("cover-input");
const coverDropzone = document.getElementById("cover-dropzone");
const coverPreviewBox = document.getElementById("cover-preview-box");
const coverThumb = document.getElementById("cover-thumb");
const coverName = document.getElementById("cover-name");
const coverDimensions = document.getElementById("cover-dimensions");
const btnRemoveCover = document.getElementById("btn-remove-cover");

const togglePayloadText = document.getElementById("toggle-payload-text");
const togglePayloadImage = document.getElementById("toggle-payload-image");
const payloadTextGroup = document.getElementById("payload-text-group");
const payloadImageGroup = document.getElementById("payload-image-group");
const secretTextInput = document.getElementById("secret-text-input");
const textCharCount = document.getElementById("text-char-count");

const secretImgInput = document.getElementById("secret-img-input");
const secretImgDropzone = document.getElementById("secret-img-dropzone");
const secretImgPreviewBox = document.getElementById("secret-img-preview-box");
const secretImgThumb = document.getElementById("secret-img-thumb");
const secretImgName = document.getElementById("secret-img-name");
const secretImgDimensions = document.getElementById("secret-img-dimensions");
const btnRemoveSecretImg = document.getElementById("btn-remove-secret-img");

const btnRunEncode = document.getElementById("btn-run-encode");
const encodeResultBox = document.getElementById("encode-result-box");
const encodeResultImg = document.getElementById("encode-result-img");
const btnDownloadStego = document.getElementById("btn-download-stego");
const btnSendToDecode = document.getElementById("btn-send-to-decode");

// Decode elements
const stegoInput = document.getElementById("stego-input");
const stegoDropzone = document.getElementById("stego-dropzone");
const stegoPreviewBox = document.getElementById("stego-preview-box");
const stegoThumb = document.getElementById("stego-thumb");
const stegoName = document.getElementById("stego-name");
const stegoDimensions = document.getElementById("stego-dimensions");
const btnRemoveStego = document.getElementById("btn-remove-stego");

const toggleExtractText = document.getElementById("toggle-extract-text");
const toggleExtractImage = document.getElementById("toggle-extract-image");

const btnRunDecode = document.getElementById("btn-run-decode");
const decodeTextResultBox = document.getElementById("decode-text-result-box");
const extractedTextOutput = document.getElementById("extracted-text-output");
const btnCopyExtractedText = document.getElementById("btn-copy-extracted-text");

const decodeImageResultBox = document.getElementById("decode-image-result-box");
const extractedImagePreview = document.getElementById("extracted-image-preview");
const btnDownloadExtractedImg = document.getElementById("btn-download-extracted-img");

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  setupTabEvents();
  setupToggleEvents();
  setupFileInputEvents();
  setupDragAndDrop();
  setupClipboardPaste();
  setupRemoveButtons();
  setupActionEvents();
  setupPopoutAndCloseButtons();
});

// --- PERSISTENT FULL TAB & CLOSE (ESC) BUTTONS ---
function setupPopoutAndCloseButtons() {
  if (btnPopoutTab) {
    btnPopoutTab.addEventListener("click", () => {
      let url = "popup.html";
      if (typeof browser !== "undefined" && browser.runtime && browser.runtime.getURL) {
        url = browser.runtime.getURL("popup.html");
      } else if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.getURL) {
        url = chrome.runtime.getURL("popup.html");
      }

      // Opens a permanent browser tab that NEVER auto-closes
      if (typeof browser !== "undefined" && browser.tabs && browser.tabs.create) {
        browser.tabs.create({ url: url });
      } else if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.create) {
        chrome.tabs.create({ url: url });
      } else {
        window.open(url, "_blank");
      }
    });
  }

  if (btnCloseWindow) {
    btnCloseWindow.addEventListener("click", () => {
      window.close();
    });
  }

  // Close extension on ESC key
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      window.close();
    }
  });
}

// --- GLOBAL CTRL+V CLIPBOARD PASTE SUPPORT ---
function setupClipboardPaste() {
  window.addEventListener("paste", (e) => {
    const items = (e.clipboardData || window.clipboardData).items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const file = items[i].getAsFile();
        if (!file) continue;

        const pastedFile = new File([file], `screenshot_${Date.now()}.png`, { type: "image/png" });

        if (activeTab === "encode") {
          if (encodePayloadType === "image" && (document.activeElement === secretImgInput || secretImgPreviewBox.style.display === "none")) {
            handleSecretImageFile(pastedFile);
            showBanner("📋 Pasted screenshot as Secret Image!", "success");
          } else {
            handleCoverFile(pastedFile);
            showBanner("📋 Pasted screenshot as Cover Image!", "success");
          }
        } else {
          handleStegoFile(pastedFile);
          showBanner("📋 Pasted screenshot as Stego Image!", "success");
        }
        e.preventDefault();
        break;
      }
    }
  });
}

// --- REMOVE / CROSS (✕) BUTTONS ---
function setupRemoveButtons() {
  if (btnRemoveCover) {
    btnRemoveCover.addEventListener("click", (e) => {
      e.stopPropagation();
      coverFileObj = null;
      coverInput.value = "";
      coverPreviewBox.style.display = "none";
      encodeResultBox.style.display = "none";
      showBanner("Removed cover image.", "info");
    });
  }

  if (btnRemoveSecretImg) {
    btnRemoveSecretImg.addEventListener("click", (e) => {
      e.stopPropagation();
      secretImgFileObj = null;
      if (secretImgInput) secretImgInput.value = "";
      secretImgPreviewBox.style.display = "none";
      showBanner("Removed secret image.", "info");
    });
  }

  if (btnRemoveStego) {
    btnRemoveStego.addEventListener("click", (e) => {
      e.stopPropagation();
      stegoFileObj = null;
      stegoInput.value = "";
      stegoPreviewBox.style.display = "none";
      decodeTextResultBox.style.display = "none";
      decodeImageResultBox.style.display = "none";
      showBanner("Removed stego image.", "info");
    });
  }
}

// --- BACKEND HEALTH CHECK ---
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      statusDot.className = "status-dot online";
      statusText.innerText = "Online";
      serverBadge.title = `Backend online (${data.model_mode || "FastAPI"})`;
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    statusDot.className = "status-dot offline";
    statusText.innerText = "Offline";
    serverBadge.title = "FastAPI backend unreachable on http://localhost:8000";
    showBanner("Backend server offline. Ensure Docker or FastAPI is running on port 8000.", "error");
  }
}

// --- TAB SWITCHING ---
function setupTabEvents() {
  tabEncodeBtn.addEventListener("click", () => {
    activeTab = "encode";
    tabEncodeBtn.classList.add("active");
    tabDecodeBtn.classList.remove("active");
    encodePanel.classList.remove("hidden");
    decodePanel.classList.add("hidden");
    hideBanner();
  });

  tabDecodeBtn.addEventListener("click", () => {
    activeTab = "decode";
    tabDecodeBtn.classList.add("active");
    tabEncodeBtn.classList.remove("active");
    decodePanel.classList.remove("hidden");
    encodePanel.classList.add("hidden");
    hideBanner();
  });
}

// --- SUB-TOGGLES ---
function setupToggleEvents() {
  // Encode payload toggle
  togglePayloadText.addEventListener("click", () => {
    encodePayloadType = "text";
    togglePayloadText.classList.add("selected");
    togglePayloadImage.classList.remove("selected");
    payloadTextGroup.classList.remove("hidden");
    payloadImageGroup.classList.add("hidden");
  });

  togglePayloadImage.addEventListener("click", () => {
    encodePayloadType = "image";
    togglePayloadImage.classList.add("selected");
    togglePayloadText.classList.remove("selected");
    payloadImageGroup.classList.remove("hidden");
    payloadTextGroup.classList.add("hidden");
  });

  // Decode extract toggle
  toggleExtractText.addEventListener("click", () => {
    decodeExtractType = "text";
    toggleExtractText.classList.add("selected");
    toggleExtractImage.classList.remove("selected");
    decodeImageResultBox.style.display = "none";
  });

  toggleExtractImage.addEventListener("click", () => {
    decodeExtractType = "image";
    toggleExtractImage.classList.add("selected");
    toggleExtractText.classList.remove("selected");
    decodeTextResultBox.style.display = "none";
  });

  // Character counter
  secretTextInput.addEventListener("input", (e) => {
    const len = e.target.value.length;
    const bytes = new TextEncoder().encode(e.target.value).length;
    textCharCount.innerText = `${len} characters (${bytes} bytes)`;
  });
}

// --- FILE INPUT PREVIEWS ---
function setupFileInputEvents() {
  // Cover image input
  coverInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    handleCoverFile(file);
  });

  // Secret image input
  if (secretImgInput) {
    secretImgInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      handleSecretImageFile(file);
    });
  }

  // Stego image input
  stegoInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    handleStegoFile(file);
  });
}

function handleCoverFile(file) {
  coverFileObj = file;
  loadImagePreview(file, coverThumb, coverName, coverDimensions, coverPreviewBox);
  encodeResultBox.style.display = "none";
}

function handleSecretImageFile(file) {
  secretImgFileObj = file;
  loadImagePreview(file, secretImgThumb, secretImgName, secretImgDimensions, secretImgPreviewBox);
}

function handleStegoFile(file) {
  stegoFileObj = file;
  loadImagePreview(file, stegoThumb, stegoName, stegoDimensions, stegoPreviewBox);
  decodeTextResultBox.style.display = "none";
  decodeImageResultBox.style.display = "none";
}

// --- DRAG & DROP SUPPORT ---
function setupDragAndDrop() {
  const dropzones = [
    { el: coverDropzone, handler: handleCoverFile },
    { el: secretImgDropzone, handler: handleSecretImageFile },
    { el: stegoDropzone, handler: handleStegoFile },
  ];

  dropzones.forEach(({ el, handler }) => {
    if (!el) return;

    ["dragenter", "dragover"].forEach((eventName) => {
      el.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        el.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      el.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        el.classList.remove("dragover");
      });
    });

    el.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handler(files[0]);
      }
    });
  });
}

function loadImagePreview(file, thumbEl, nameEl, metaEl, boxEl) {
  nameEl.innerText = file.name;
  const sizeKB = (file.size / 1024).toFixed(1);

  const img = new Image();
  const url = URL.createObjectURL(file);
  img.src = url;

  img.onload = () => {
    thumbEl.src = url;
    metaEl.innerText = `${img.naturalWidth} × ${img.naturalHeight} px • ${sizeKB} KB`;
    boxEl.style.display = "flex";
  };
}

// --- ACTIONS & API CALLS ---
function setupActionEvents() {
  // ENCODE ACTION
  btnRunEncode.addEventListener("click", async () => {
    if (!coverFileObj) {
      showBanner("Please select or paste a cover image first.", "error");
      return;
    }

    if (encodePayloadType === "text" && !secretTextInput.value.trim()) {
      showBanner("Please enter secret text to hide.", "error");
      return;
    }

    if (encodePayloadType === "image" && !secretImgFileObj) {
      showBanner("Please select or paste a secret image to hide.", "error");
      return;
    }

    setButtonLoading(btnRunEncode, true, "Upscaling & Encrypting...");
    showBanner("Running Real-ESRGAN 4x upscale & LSB embedding...", "info");
    encodeResultBox.style.display = "none";

    const formData = new FormData();
    formData.append("payload_type", encodePayloadType);
    formData.append("cover_image", coverFileObj);
    formData.append("scale", "4");

    if (encodePayloadType === "text") {
      formData.append("secret_text", secretTextInput.value);
    } else {
      formData.append("secret_image", secretImgFileObj);
    }

    try {
      const response = await fetch(`${API_BASE}/encode`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = "Encoding failed on server.";
        try {
          const errData = await response.json();
          if (errData.detail) errorMsg = errData.detail;
          else if (errData.error) errorMsg = errData.error;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      const blob = await response.blob();
      lastEncodedBlob = blob;
      const resultUrl = URL.createObjectURL(blob);

      encodeResultImg.src = resultUrl;
      encodeResultBox.style.display = "block";

      showBanner("Upscaling & Stego complete! Image ready for download.", "success");

      // Auto-trigger download
      triggerDownload(blob, "stego_upscaled.png");
    } catch (err) {
      showBanner(`Error: ${err.message}`, "error");
    } finally {
      setButtonLoading(btnRunEncode, false, "<span>🚀</span> Upscale & Encrypt");
    }
  });

  // DOWNLOAD STEGO BUTTON
  btnDownloadStego.addEventListener("click", () => {
    if (lastEncodedBlob) {
      triggerDownload(lastEncodedBlob, "stego_upscaled.png");
    }
  });

  // SEND TO DECODE BUTTON
  btnSendToDecode.addEventListener("click", () => {
    if (!lastEncodedBlob) return;
    stegoFileObj = new File([lastEncodedBlob], "stego_upscaled.png", { type: "image/png" });
    loadImagePreview(stegoFileObj, stegoThumb, stegoName, stegoDimensions, stegoPreviewBox);

    // Switch to decode tab
    tabDecodeBtn.click();
    showBanner("Loaded generated stego image into Decode tab.", "info");
  });

  // DECODE ACTION
  btnRunDecode.addEventListener("click", async () => {
    if (!stegoFileObj) {
      showBanner("Please select, drop, or paste an upscaled stego PNG image.", "error");
      return;
    }

    setButtonLoading(btnRunDecode, true, "Extracting & Decrypting...");
    showBanner("Reading LSB layers & decrypting dynamic XOR keystream...", "info");
    decodeTextResultBox.style.display = "none";
    decodeImageResultBox.style.display = "none";

    const formData = new FormData();
    formData.append("extract_type", decodeExtractType);
    formData.append("stego_image", stegoFileObj);
    formData.append("scale", "4");

    try {
      const response = await fetch(`${API_BASE}/decode`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = "Extraction failed.";
        try {
          const errData = await response.json();
          if (errData.detail) errorMsg = errData.detail;
          else if (errData.error) errorMsg = errData.error;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      if (decodeExtractType === "text") {
        const data = await response.json();
        extractedTextOutput.value = data.text || "";
        decodeTextResultBox.style.display = "block";
        showBanner("Secret message successfully extracted!", "success");
      } else {
        const blob = await response.blob();
        lastDecodedImageBlob = blob;
        const imgUrl = URL.createObjectURL(blob);
        extractedImagePreview.src = imgUrl;
        decodeImageResultBox.style.display = "block";
        showBanner("Secret image successfully recovered!", "success");
        triggerDownload(blob, "extracted_secret.png");
      }
    } catch (err) {
      showBanner(`Extraction error: ${err.message}`, "error");
    } finally {
      setButtonLoading(btnRunDecode, false, "<span>🔓</span> Extract Hidden Secret");
    }
  });

  // COPY EXTRACTED TEXT
  btnCopyExtractedText.addEventListener("click", () => {
    if (!extractedTextOutput.value) return;
    navigator.clipboard.writeText(extractedTextOutput.value).then(() => {
      const origHtml = btnCopyExtractedText.innerHTML;
      btnCopyExtractedText.innerHTML = "<span>✅</span> Copied to Clipboard!";
      setTimeout(() => {
        btnCopyExtractedText.innerHTML = origHtml;
      }, 2000);
    });
  });

  // DOWNLOAD EXTRACTED IMAGE
  btnDownloadExtractedImg.addEventListener("click", () => {
    if (lastDecodedImageBlob) {
      triggerDownload(lastDecodedImageBlob, "extracted_secret.png");
    }
  });
}

// --- UTILITIES ---
function setButtonLoading(btn, isLoading, text) {
  if (isLoading) {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${text}`;
  } else {
    btn.disabled = false;
    btn.innerHTML = text;
  }
}

function showBanner(message, type = "info") {
  statusBanner.className = `status-banner ${type}`;
  bannerMessage.innerText = message;
  if (type === "error") bannerIcon.innerText = "❌";
  else if (type === "success") bannerIcon.innerText = "✅";
  else bannerIcon.innerText = "⏳";
}

function hideBanner() {
  statusBanner.style.display = "none";
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);

  // Chrome / Firefox Extension download API
  if (typeof chrome !== "undefined" && chrome.downloads && chrome.downloads.download) {
    chrome.downloads.download(
      {
        url: url,
        filename: filename,
        saveAs: false,
      },
      (downloadId) => {
        if (chrome.runtime.lastError) {
          fallbackAnchorDownload(url, filename);
        }
      }
    );
  } else if (typeof browser !== "undefined" && browser.downloads && browser.downloads.download) {
    browser.downloads.download({
      url: url,
      filename: filename,
      saveAs: false,
    }).catch(() => {
      fallbackAnchorDownload(url, filename);
    });
  } else {
    // Browser fallback
    fallbackAnchorDownload(url, filename);
  }
}

function fallbackAnchorDownload(url, filename) {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
