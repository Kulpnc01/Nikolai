import cv2
import time
import numpy as np
import os
from PIL import Image, ImageFilter
from memory_mcp_server import get_resource, log_event

# Resource name to fetch
CAMERA_RESOURCE_NAME = "Primary Camera"

def fetch_rtsp_config():
    """Fetches RTSP URL and credentials from the Nikolai database."""
    print(f"[*] Fetching config for '{CAMERA_RESOURCE_NAME}'...")
    res = get_resource(CAMERA_RESOURCE_NAME)
    if res and res["type"] == "rtsp":
        url = res["config"].get("url")
        user = res.get("username")
        password = res.get("password")
        
        # If user/pass are provided separately, inject them into the URL if not already there
        if user and password and "@" not in url:
            if url.startswith("rtsp://"):
                url = f"rtsp://{user}:{password}@{url[7:]}"
        
        return url
    return None

def start_vision_ingestion():
    rtsp_url = fetch_rtsp_config()
    
    if not rtsp_url:
        print(f"[-] Resource '{CAMERA_RESOURCE_NAME}' not found or invalid. Please add it via Nikolai Control Center.")
        return

    # Hide credentials for logging
    safe_url = rtsp_url.split('@')[-1] if '@' in rtsp_url else rtsp_url
    
    # Try different protocols if standard RTSP fails
    urls_to_try = [rtsp_url]
    if rtsp_url.startswith("rtsp://"):
        # Some cameras prefer TCP transport explicitly in the URL or via environment
        pass

    print(f"[*] Opening RTSP stream with OpenCV: {safe_url}")
    
    # Force TCP transport for RTSP in OpenCV/FFmpeg
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print(f"[-] Could not open RTSP stream. Trying without explicit credentials in URL if applicable...")
        # Fallback: maybe the camera doesn't like credentials in the DESCRIBE method but works otherwise?
        # Or try a simple ping/check
        cap = cv2.VideoCapture(rtsp_url) # Retry once
        if not cap.isOpened():
            print(f"[-] Final failure to open RTSP stream. Error 406 often means the camera rejected the request format.")
            return

    print("[+] OpenCV stream opened.")

    # Read first frame
    ret, frame1_orig = cap.read()
    if not ret:
        print("[-] Failed to read first frame")
        cap.release()
        return
    
    frame1 = cv2.resize(frame1_orig, (1280, 720))
    print(f"[+] Got initial frame: {frame1.shape}")
    print("[+] Vision ingestion running.")

    while True:
        try:
            ret, frame2_orig = cap.read()
            if not ret:
                print("[-] Lost connection to camera.")
                # Attempt to reconnect
                print("[*] Attempting to reconnect...")
                cap.release()
                time.sleep(5)
                cap = cv2.VideoCapture(rtsp_url)
                continue
            
            frame2 = cv2.resize(frame2_orig, (1280, 720))
            
            # Motion detection using numpy (keeping original logic)
            diff = np.abs(frame1.astype(int) - frame2.astype(int)).astype(np.uint8)
            gray = np.dot(diff[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)

            # Keep the PIL-based Gaussian blur as in original script
            gray_pil = Image.fromarray(gray)
            gray_pil = gray_pil.filter(ImageFilter.GaussianBlur(radius=2.5))
            gray = np.array(gray_pil)

            thresh = (gray > 20).astype(np.uint8) * 255
            white_pixels = np.sum(thresh > 127)

            if white_pixels > 1500:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] Motion detected ({white_pixels} pixels)")
                
                # Log to Nikolai's event log
                try:
                    log_event("vision", "motion_detected", f"Motion detected on {CAMERA_RESOURCE_NAME} ({white_pixels} pixels)")
                except Exception as e:
                    print(f"[-] Error logging motion event: {e}")

            frame1 = frame2
            
        except Exception as e:
            print(f"[-] Error processing frame: {e}")
            break

        # Slight delay to match original behavior
        time.sleep(0.1)

    cap.release()


if __name__ == "__main__":
    # Ensure we are in the right directory so DB is found
    if os.path.dirname(__file__):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    start_vision_ingestion()
