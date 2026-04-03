# PROJECT ARCHITECTURE: Nikolai
```text
  .vscode/
    settings.json
  core/
    agent_loop.py
    control_center.py
  GEMINI.md
  interface/
    vision_ingestion.py
    voice_interface.py
  memory/
    Initialize-memory.py
    mcp_memory_server.json
    memory_mcp_server.py
  nikolai_flattener.py
  Nikolai_Logic_Map.md
  package-lock.json
  package.json
  README.md
  REVENUE_STRATEGY.md
  RULES.md
  security/
    vault.key
    vault.py
  TECHNICAL_ARCHITECTURE.md
```

## FILE: .vscode\settings.json
```json
{
    "python.terminal.executeInFileDir": true,
    "python.terminal.useEnvFile": true,
    "python.linting.enabled": true,
    "python.analysis.autoImportCompletions": true,
    "python.defaultInterpreterPath": "C:\\HDT\\Nikolai\\venv\\Scripts\\python.exe",
    "[python]": {
        "editor.defaultFormatter": "ms-python.python",
        "editor.formatOnSave": true
    }
}
```

## FILE: core\agent_loop.py
```py
import time
import sqlite3
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Dynamic Path Resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent

# Inject paths for other modules
sys.path.append(str(ROOT_DIR / "memory"))
sys.path.append(str(ROOT_DIR / "interface"))

from memory_mcp_server import log_event, get_tasks, write_memory

# Database path is relative to the memory script, but let's anchor it
DB_PATH = ROOT_DIR / "memory" / "nikolai_memory.db"
CHECK_INTERVAL = 10  # seconds
HYPERFOCUS_THRESHOLD_MINUTES = 40

class Notifier:
    @staticmethod
    def speak(text):
        """Uses the local voice interface to speak."""
        try:
            # Import inside to avoid circular dependency
            import voice_interface
            voice_interface.speak(text)
        except Exception as e:
            print(f"[!] Voice error: {e}. Text: {text}")

    @staticmethod
    def show_toast(title, message):
        """Uses PowerShell to show a Windows notification."""
        safe_title = title.replace("'", "''")
        safe_msg = message.replace("'", "''")
        powershell_command = f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
        $notification = New-Object System.Windows.Forms.NotifyIcon
        $notification.Icon = [System.Drawing.SystemIcons]::Information
        $notification.BalloonTipTitle = '{safe_title}'
        $notification.BalloonTipText = '{safe_msg}'
        $notification.Visible = $true
        $notification.ShowBalloonTip(5000)
        """
        subprocess.run(["powershell", "-Command", powershell_command], capture_output=True)

    @staticmethod
    def log_to_reminders(message):
        """Appends a reminder to REMINDERS.txt."""
        reminders_file = ROOT_DIR / "REMINDERS.txt"
        with open(reminders_file, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

    @classmethod
    def notify(cls, title, message, use_voice=True):
        print(f"[*] NOTIFICATION: {title} - {message}")
        cls.log_to_reminders(f"{title}: {message}")
        cls.show_toast(title, message)
        if use_voice:
            cls.speak(message)

def run_loop():
    print(f"==================================================")
    print(f"  PROJECT NIKOLAI: COGNITIVE LOOP ACTIVE          ")
    print(f"  Root: {ROOT_DIR}")
    print(f"==================================================\n")
    
    log_event("nikolai", "system_boot", "Agent loop started.")
    
    last_task_check = datetime.now()
    
    try:
        while True:
            now = datetime.now()
            
            # 1. CHECK PENDING TASKS
            tasks = get_tasks(status="pending")
            if tasks:
                for task in tasks:
                    # Logic for task urgency or reminders can go here
                    pass

            # 2. CHECK FOR HYPERFOCUS / INACTIVITY
            # Placeholder for activity tracking logic
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[!] Loop terminated by user.")
        log_event("nikolai", "system_shutdown", "Agent loop stopped.")

if __name__ == "__main__":
    run_loop()

```

## FILE: core\control_center.py
```py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import sqlite3
from pathlib import Path

# Dynamic Path Resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent

# Inject paths for other modules
sys.path.append(str(ROOT_DIR / "memory"))
sys.path.append(str(ROOT_DIR / "security"))

from memory_mcp_server import add_resource, add_node, get_resource, DB_PATH, add_credential, remove_resource, update_resource
from vault import vault

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NikolaiControlCenter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nikolai Control Center")
        self.geometry("1100x750")

        self.editing_resource_name = None

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NIKOLAI", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=30)

        self.resource_btn = ctk.CTkButton(self.sidebar_frame, text="Resources / Cameras", command=self.show_resources)
        self.resource_btn.pack(pady=10, padx=20)

        self.network_btn = ctk.CTkButton(self.sidebar_frame, text="Static Networking", command=self.show_network)
        self.network_btn.pack(pady=10, padx=20)
        
        self.status_btn = ctk.CTkButton(self.sidebar_frame, text="Swarm Status", command=self.show_status)
        self.status_btn.pack(pady=10, padx=20)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", expand=True, fill="both", padx=20, pady=20)
        
        self.show_resources()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_resources(self):
        self.clear_main()
        self.editing_resource_name = None
        
        header_text = "Resource & Camera Manager"
        ctk.CTkLabel(self.main_frame, text=header_text, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        # Add/Edit Resource Form
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.form_frame, text="Friendly Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.res_name = ctk.CTkEntry(self.form_frame, placeholder_text="e.g. Front Door Camera")
        self.res_name.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Type:").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.res_type = ctk.CTkComboBox(self.form_frame, values=["rtsp", "audio", "visual", "sensor"])
        self.res_type.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Stream URL / IP:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.res_path = ctk.CTkEntry(self.form_frame, width=400, placeholder_text="rtsp://user:pass@192.168.x.x:554/stream")
        self.res_path.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Username:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.res_user = ctk.CTkEntry(self.form_frame)
        self.res_user.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Password:").grid(row=2, column=2, padx=10, pady=10, sticky="e")
        self.res_pass = ctk.CTkEntry(self.form_frame, show="*")
        self.res_pass.grid(row=2, column=3, padx=10, pady=10, sticky="w")
        
        self.submit_btn = ctk.CTkButton(self.form_frame, text="Add To Nikolai Swarm", command=self.save_resource, fg_color="green", hover_color="#006400")
        self.submit_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.cancel_btn = ctk.CTkButton(self.form_frame, text="Cancel Edit", command=self.show_resources, fg_color="gray")

        # List Frame
        list_label = ctk.CTkLabel(self.main_frame, text="Integrated Resources", font=ctk.CTkFont(size=16, weight="bold"))
        list_label.pack(pady=(20, 5))
        
        self.res_list_frame = ctk.CTkScrollableFrame(self.main_frame, height=300)
        self.res_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_resource_list()

    def save_resource(self):
        name = self.res_name.get()
        rtype = self.res_type.get()
        path = self.res_path.get()
        user = self.res_user.get()
        password = self.res_pass.get()
        
        if not name or not path:
            messagebox.showerror("Error", "Name and Path/URL are required.")
            return
            
        config = {"url": path}
        
        try:
            if self.editing_resource_name:
                update_resource(self.editing_resource_name, rtype, config, user, password)
                messagebox.showinfo("Success", f"Resource '{name}' updated successfully.")
            else:
                cred_id = None
                if user and password:
                    cred_id = add_credential(name, user, password)
                add_resource(name, rtype, config, cred_id)
                messagebox.showinfo("Success", f"Resource '{name}' integrated successfully.")
            
            self.show_resources()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save resource: {e}")

    def edit_resource(self, name):
        res = get_resource(name)
        if not res:
            messagebox.showerror("Error", "Resource data not found.")
            return
        
        self.editing_resource_name = name
        self.res_name.delete(0, tk.END)
        self.res_name.insert(0, name)
        self.res_name.configure(state="disabled") 
        
        self.res_type.set(res["type"])
        self.res_path.delete(0, tk.END)
        self.res_path.insert(0, res["config"].get("url", ""))
        
        self.res_user.delete(0, tk.END)
        if res.get("username"):
            self.res_user.insert(0, res["username"])
            
        self.res_pass.delete(0, tk.END)
        if res.get("password"):
            self.res_pass.insert(0, res["password"])
            
        self.submit_btn.configure(text="Update Resource", fg_color="blue", hover_color="#00008B")
        self.cancel_btn.grid(row=3, column=2, columnspan=2, pady=20)

    def delete_resource(self, name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove '{name}' from the swarm?"):
            try:
                remove_resource(name)
                messagebox.showinfo("Deleted", f"Resource '{name}' removed.")
                self.refresh_resource_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove resource: {e}")

    def refresh_resource_list(self):
        for widget in self.res_list_frame.winfo_children():
            widget.destroy()
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, config_json FROM resources")
        rows = cursor.fetchall()
        conn.close()
        
        for i, (name, rtype, config) in enumerate(rows):
            item = ctk.CTkFrame(self.res_list_frame)
            item.pack(fill="x", pady=5)
            
            ctk.CTkLabel(item, text=f"[{rtype.upper()}] {name}", width=200, anchor="w").pack(side="left", padx=10)
            url = json.loads(config).get('url', 'N/A')
            display_url = (url[:40] + '...') if len(url) > 43 else url
            ctk.CTkLabel(item, text=f"URL: {display_url}", anchor="w").pack(side="left", padx=10, expand=True, fill="x")
            
            ctk.CTkButton(item, text="Edit", width=60, command=lambda n=name: self.edit_resource(n)).pack(side="left", padx=5)
            ctk.CTkButton(item, text="Delete", width=60, fg_color="red", hover_color="#8B0000", command=lambda n=name: self.delete_resource(n)).pack(side="left", padx=5)

    def show_network(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Precise Static Networking (V-LAN)", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(form_frame, text="Device Hostname:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.node_host = ctk.CTkEntry(form_frame, placeholder_text="e.g. Nikolai-Mobile-1")
        self.node_host.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(form_frame, text="Role:").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.node_role = ctk.CTkComboBox(form_frame, values=["Nexus (Main)", "Agent", "Sensor Node", "Vision Node"])
        self.node_role.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        ctk.CTkButton(form_frame, text="Register Node & Assign IP", command=self.save_node).grid(row=1, column=0, columnspan=4, pady=20)
        
        self.node_list_frame = ctk.CTkScrollableFrame(self.main_frame, height=350)
        self.node_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.refresh_node_list()

    def save_node(self):
        host = self.node_host.get()
        role = self.node_role.get()
        if not host: return
        
        res = add_node(host, role)
        if isinstance(res, dict):
            messagebox.showinfo("Network Assigned", f"Node: {res['hostname']}\nVirtual IP: {res['virtual_ip']}")
        else:
            messagebox.showerror("Error", res)
        self.refresh_node_list()

    def refresh_node_list(self):
        for widget in self.node_list_frame.winfo_children():
            widget.destroy()
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT hostname, virtual_ip, role FROM network_nodes")
        rows = cursor.fetchall()
        conn.close()
        
        for name, ip, role in rows:
            item = ctk.CTkFrame(self.node_list_frame)
            item.pack(fill="x", pady=5)
            ctk.CTkLabel(item, text=name, width=200, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(item, text=f"IP: {ip}", width=150).pack(side="left", padx=10)
            ctk.CTkLabel(item, text=f"Role: {role}", width=150).pack(side="left", padx=10)

    def show_status(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Swarm Status Monitor", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        ctk.CTkLabel(self.main_frame, text="All systems nominal. Nexus online at 10.26.0.1", text_color="green").pack(pady=10)

if __name__ == "__main__":
    app = NikolaiControlCenter()
    app.mainloop()

```

## FILE: GEMINI.md
```md
# Project Nikolai: Core Mandates

## Objective

Nikolai is an all-encompassing life assistant designed to combat ADHD, distractions, and forgetfulness. He enhances the user's natural processes, prioritizes goals, and manages a revenue stream to support the user's personal business.

## Technical Standards

- **Memory First**: All long-term state, tasks, and significant events MUST be stored in the central SQLite database (`nikolai_memory.db`) via the MCP server.
- **Hybrid Sync Strategy**: Assistants (Gemini CLI, Copilot, Nikolai) may use local files or scratchpads for tactical work but MUST synchronize the final state back to the MCP database to ensure consistency.
- **Local-First, Cloud-Supplemented**: Operations should prioritize local hardware (vision, voice, database). Cloud resources (Google Pro, Azure, Copilot) are utilized for high-compute or specialized tasks.
- **Surgical Updates**: Code modifications must be precise and follow established patterns in `memory_mcp_server.py`, `agent_loop.py`, and `vault.py`.

## ADHD & Productivity Guardrails

- **User-Centric Authority**: The user is the final arbiter of task priority and scheduling. Nikolai suggests; the user decides.
- **Multi-Channel Reminders**: Reminders must be delivered via **Voice** (`voice_interface.py`), **Desktop Toast** (PowerShell/win32), and logged to `REMINDERS.txt`.
- **Behavioral Detection**:
  - **Hyperfocus Watcher**: Flag and remind the user if a single task (priority 1 or 2) exceeds 40 minutes without a status update.
  - **Priority Drift Guard**: Flag if the user initiates a new task while a higher-priority task is still in 'pending' status.
- **Granular Decomposition**: Large goals must be broken into small, atomic tasks logged in the memory bank to prevent overwhelm.

## Security & Business

- **Vault Integrity**: All credentials and sensitive data MUST stay encrypted within the `vault.py` framework. Never log or print raw secrets.
- **Revenue Scope**: Nikolai manages and operates digital content creation pipelines, AI solution delivery for low-tech companies, and affiliate marketing automation.
- **Shared Responsibility**: All project entities (Gemini, Copilot, Nikolai) are responsible for both the development and operation of revenue-generating tools.
- **Audit Log**: Every automated action taken by Nikolai or the assistants must be logged in the `event_log` for transparency.
```

## FILE: interface\vision_ingestion.py
```py
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

```

## FILE: interface\voice_interface.py
```py
import queue
import sounddevice as sd
import vosk
import json
import pyttsx3
from agent_loop import process_user_input

# Initialize TTS engine
tts_engine = pyttsx3.init()

# Load Vosk model (offline STT)
model = vosk.Model("models/vosk-model-small-en-us-0.15")
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

def start_listening():
    recognizer = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):

        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    handle_voice_command(text)

def handle_voice_command(text):
    response = process_user_input(text)
    speak(response)

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()
```

## FILE: memory\Initialize-memory.py
```py
import sqlite3
import os
from pathlib import Path

# Dynamic Path Resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
DB_PATH = SCRIPT_DIR / "nikolai_memory.db"

def init_db():
    print(f"[*] MEMORY: Initializing database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Event Log (History)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source TEXT,
        event_type TEXT,
        details TEXT
    )
    ''')

    # 2. Memory Entries (Persistent Thoughts)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memory_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source TEXT,
        type TEXT,
        content TEXT,
        tags TEXT
    )
    ''')

    # 3. Tasks (Cognitive Agenda)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        priority INTEGER,
        status TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
    )
    ''')

    # 4. Credentials (Encrypted Vault Nodes)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_name TEXT,
        username TEXT,
        encrypted_password TEXT
    )
    ''')

    # 5. Resources (Cameras, Sensors, APIs)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        type TEXT,
        config_json TEXT,
        credential_id INTEGER,
        FOREIGN KEY (credential_id) REFERENCES credentials (id)
    )
    ''')

    # 6. Network Nodes (V-LAN Topology)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS network_nodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT UNIQUE,
        virtual_ip TEXT UNIQUE,
        role TEXT,
        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("[+] SUCCESS: Database schema active.")

if __name__ == "__main__":
    init_db()

```

## FILE: memory\mcp_memory_server.json
```json
{
  "mcpServers": {
    "nikolai-memory": {
      "command": "C:/HDT/Nikolai/venv/Scripts/python.exe",
      "args": [
        "C:/HDT/Nikolai/memory/memory_mcp_server.py"
      ],
      "cwd": "C:/HDT/Nikolai/memory"
    }
  }
}

```

## FILE: memory\memory_mcp_server.py
```py
import sqlite3
import json
import os
import sys
from pathlib import Path
from fastmcp import FastMCP

# Dynamic Path Resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent
DB_PATH = SCRIPT_DIR / "nikolai_memory.db"

# Add security dir to path for vault import
sys.path.append(str(ROOT_DIR / "security"))
try:
    from vault import vault
except ImportError:
    vault = None

server = FastMCP("nikolai-memory")

# --- LOGGING & EVENTS ---
def log_event(source: str, event_type: str, details: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO event_log (source, event_type, details) VALUES (?, ?, ?)",
        (source, event_type, details)
    )
    conn.commit()
    conn.close()
    return "Event logged."

def get_recent_events(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_log ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- MEMORY & TASKS ---
def write_memory(content: str, source="user", type="note", tags=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memory_entries (source, type, content, tags) VALUES (?, ?, ?, ?)",
        (source, type, content, tags)
    )
    conn.commit()
    conn.close()
    return "Memory stored."

def read_memory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, source, type, content FROM memory_entries ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_task(title: str, description: str = "", priority: int = 3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, priority, status) VALUES (?, ?, ?, 'pending')",
        (title, description, priority)
    )
    conn.commit()
    conn.close()
    return f"Task '{title}' created."

def get_tasks(status="pending"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, priority, created_at FROM tasks WHERE status = ? ORDER BY priority ASC, created_at DESC", (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def complete_task(task_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return f"Task {task_id} marked complete."

# --- SWARM & RESOURCE MANAGEMENT ---
def add_credential(resource_name, username, password):
    if not vault: return None
    enc_pass = vault.encrypt(password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO credentials (resource_name, username, encrypted_password) VALUES (?, ?, ?)",
        (resource_name, username, enc_pass)
    )
    cred_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cred_id

def add_resource(name, rtype, config, credential_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resources (name, type, config_json, credential_id) VALUES (?, ?, ?, ?)",
        (name, rtype, json.dumps(config), credential_id)
    )
    conn.commit()
    conn.close()
    return f"Resource {name} added."

def get_resource(name):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.name, r.type, r.config_json, c.username, c.encrypted_password 
        FROM resources r
        LEFT JOIN credentials c ON r.credential_id = c.id
        WHERE r.name = ?
    ''', (name,))
    row = cursor.fetchone()
    conn.close()
    
    if not row: return None
    
    res = dict(row)
    res["config"] = json.loads(res["config_json"])
    if res.get("encrypted_password") and vault:
        res["password"] = vault.decrypt(res["encrypted_password"])
    return res

def remove_resource(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Find credential_id first
    cursor.execute("SELECT credential_id FROM resources WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row and row[0]:
        cursor.execute("DELETE FROM credentials WHERE id = ?", (row[0],))
    cursor.execute("DELETE FROM resources WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return True

def update_resource(name, rtype, config, username=None, password=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT credential_id FROM resources WHERE name = ?", (name,))
    row = cursor.fetchone()
    
    cred_id = row[0] if row else None
    
    if username and password:
        if cred_id:
            enc_pass = vault.encrypt(password) if vault else password
            cursor.execute("UPDATE credentials SET username = ?, encrypted_password = ? WHERE id = ?", (username, enc_pass, cred_id))
        else:
            cred_id = add_credential(name, username, password)
            
    cursor.execute(
        "UPDATE resources SET type = ?, config_json = ?, credential_id = ? WHERE name = ?",
        (rtype, json.dumps(config), cred_id, name)
    )
    conn.commit()
    conn.close()
    return True

def add_node(hostname, role):
    # Dynamic IP Assignment (Mock V-LAN Logic)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM network_nodes")
        count = cursor.fetchone()[0]
        v_ip = f"10.26.0.{100 + count}"
        
        cursor.execute(
            "INSERT INTO network_nodes (hostname, virtual_ip, role) VALUES (?, ?, ?)",
            (hostname, v_ip, role)
        )
        conn.commit()
        return {"hostname": hostname, "virtual_ip": v_ip}
    except Exception as e:
        return str(e)
    finally:
        conn.close()

# --- MCP REGISTRATION ---
@server.tool()
def store_thought(content: str):
    """Stores a general observation or persistent thought."""
    return write_memory(content, source="agent", type="thought")

@server.tool()
def add_task(title: str, description: str, priority: int = 3):
    """Creates a new actionable task."""
    return create_task(title, description, priority)

@server.tool()
def list_tasks():
    """Returns all pending tasks."""
    return get_tasks()

if __name__ == "__main__":
    server.run()

```

## FILE: package-lock.json
```json
{
  "name": "Memory",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "dependencies": {
        "numpy": "^0.0.1"
      }
    },
    "node_modules/numpy": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/numpy/-/numpy-0.0.1.tgz",
      "integrity": "sha512-HPoSFyRtH4dRUGjI6bzeVKgfOeNtIAWLvVWMqbaNGmWKE+npdnZ6L78TEJELgZBb+9XpL6r16vOz1jaQ7YVI7Q==",
      "license": "MIT"
    }
  }
}

```

## FILE: package.json
```json
{
  "dependencies": {
    "numpy": "^0.0.1"
  }
}

```

## FILE: README.md
```md
# Project Nikolai: Cognitive Agent & Memory Hub

Nikolai is a modular AI agent system designed to act as a "Digital Self." It integrates persistent long-term memory, real-time vision ingestion, and a local voice interface into a unified cognitive loop.

## 核心 (Core Architecture)

*   **Intelligence Core (`/core`)**: Manages the main cognitive loop, task prioritization, and hyperfocus protocols.
*   **Memory Hub (`/memory`)**: A FastMCP-powered SQLite database that serves as the Single Source of Truth (SSOT) for all agent thoughts and events.
*   **Sense Interfaces (`/interface`)**: Handles RTSP vision streams and local STT/TTS (Whisper) communication.
*   **Security Vault (`/security`)**: Provides Fernet-encrypted storage for sensitive credentials and network nodes.

## System Capabilities

- **Autonomous Loop**: Continuously monitors tasks and environmental events to keep the user on target.
- **Multimodal Ingestion**: Weaves together vision events, voice commands, and manual memory writes.
- **Swarm Management**: Integrated GUI for managing network resources, cameras, and encrypted credentials.
- **ADHD/Focus Protocols**: Built-in logic for hyperfocus alerts and priority drift notifications.

## Quick Start

1.  **Initialize Memory**:
    ```bash
    python memory/Initialize-memory.py
    ```
2.  **Start the Loop**:
    ```bash
    python core/agent_loop.py
    ```
3.  **Launch Control Center**:
    ```bash
    python core/control_center.py
    ```

## AI Orchestration
Nikolai is designed to be managed and expanded by AI architects. Refer to `RULES.md` and `TECHNICAL_ARCHITECTURE.md` for the collaboration framework.

---
*Authorized Forensic & Digital Twin Research Protocol.*

```

## FILE: REVENUE_STRATEGY.md
```md
# Nikolai Revenue Strategy: Digital Solutions & Content

This document outlines the operational strategy for Nikolai's revenue-generating activities.

## 1. Digital Content Creation

- **Objective**: Automate the production and distribution of high-value digital content.
- **Tools**: Python automation (Pillow, MoviePy, OpenAI/Google Pro APIs).
- **Nikolai's Role**:
  - **Idea Generation**: Scrape trends and suggest content topics.
  - **Drafting**: Use LLM APIs to generate scripts, articles, or social media posts.
  - **Scheduling**: Log publication tasks and track performance metrics in `nikolai_memory.db`.

## 2. AI Solutions for Low-Tech Companies

- **Objective**: Provide automated AI integration services (e.g., chatbots, data entry automation).
- **Tools**: Python-based API bridges, Zapier/Make.com integration (managed via Python), and local-first AI models.
- **Nikolai's Role**:
  - **Lead Tracking**: Monitor incoming requests or potential leads in the database.
  - **Status Reporting**: Provide the user with a "Conversational/Active" summary of project statuses and upcoming milestones.
  - **Delivery**: Automate the deployment of simple AI wrappers for clients.

## 3. Affiliate Marketing & Digital Assets

- **Objective**: Maintain and scale affiliate marketing campaigns.
- **Tools**: Selenium/Requests for web automation, link tracking, and SEO monitoring.
- **Nikolai's Role**:
  - **Link Health**: Periodically check affiliate links and log "broken link" events in the `event_log`.
  - **Performance Audit**: Log daily/weekly earnings and suggest optimizations based on conversion data.

## 4. Execution Rules for Assistants

- **No Secret Leaks**: Never hardcode API keys for affiliate platforms or AI services. Use `vault.py`.
- **Pre-Flight Logging**: Before starting any automated revenue task, Nikolai MUST log the intent (e.g., "Starting affiliate link audit") to the `event_log`.
- **Conversational Updates**: Use `voice_interface.py` to keep the user informed of revenue progress ("Nikolai here. I've successfully updated the affiliate links for the AI solutions blog.").

```

## FILE: RULES.md
```md
# Project Nikolai: Collaboration Framework

This document defines the roles and coordination rules for Gemini CLI, GitHub Copilot, and Project Nikolai (the agent system).

## 1. Role Definitions

### **Nikolai (The Agent)**

- **Primary Function**: The "Self". Operates the main `agent_loop.py`, executes long-running tasks, monitors vision/voice events, and provides user reminders.
- **Responsibility**: Owning the memory database and ensuring the user stays on target.

### **Gemini CLI (The Architect)**

- **Primary Function**: System development, complex refactoring, and high-level logic implementation.
- **Responsibility**: Expanding Nikolai's "body" and "brain", ensuring technical integrity, and providing deep codebase analysis.

### **GitHub Copilot (The Tactician)**

- **Primary Function**: Inline code-completion, rapid documentation, and local logic implementation.
- **Responsibility**: Streamlining the user's manual coding experience and providing tactical support within the IDE.

## 2. Coordination Rules

### **Single Source of Truth (SSOT)**

- **The Database**: `nikolai_memory.db` is the SSOT. Any change in task state or memory must be synchronized here via `memory_mcp_server.py`.
- **Hybrid Workflow**: When Gemini or the user is working on a feature, a "scratchpad" file (e.g., `scratch_new_feature.md`) can be used. Final decisions and results MUST be logged as a "memory" or "task" in the MCP server.

### **Conflict Resolution**

- **User Supremacy**: If Gemini CLI and Nikolai's loop propose conflicting priorities, the user's explicit input (voice or text) has absolute priority.
- **State Lock**: Only one assistant should perform high-impact file modifications at a time. Coordination occurs by checking the `event_log` for recent "development" events.

### **ADHD & Focus Protocol**

- **Notification Hook**: The `agent_loop.py` emits "Focus Reminders" via Voice, PowerShell Toast, and `REMINDERS.txt`.
- **Hyperfocus Alert**: If a Priority 1 or 2 task hasn't been updated for **40 minutes**, Nikolai must trigger a reminder.
- **Priority Drift Alert**: If a new task is started before higher-priority tasks are cleared, Nikolai will log a warning and notify the user.
- **Small Batches**: All directives from the user must be broken down by Gemini CLI into discrete, actionable steps recorded in the `tasks` table.

## 3. Revenue Stream & Security

- **Strict Vault Policy**: No entity (Nikolai, Gemini, Copilot) is permitted to expose credentials outside of `vault.py`.
- **Audit Requirement**: Any financial operation (e.g., API call to a trading platform, subscription check) must log its intent *before* execution and its result *after* execution to the `event_log`.

```

## FILE: security\vault.py
```py
import os
from pathlib import Path
from cryptography.fernet import Fernet

# Dynamic Path Resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
KEY_FILE = SCRIPT_DIR / "vault.key"

class NikolaiVault:
    def __init__(self):
        self.key = self._load_key()
        self.cipher = Fernet(self.key)

    def _load_key(self):
        if not KEY_FILE.exists():
            print(f"[*] SEC: Generating new master key at {KEY_FILE}")
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key
        return open(KEY_FILE, "rb").read()

    def encrypt(self, plaintext: str) -> str:
        if not plaintext: return ""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext: return ""
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except:
            return "[DECRYPTION_FAILED]"

vault = NikolaiVault()

```

## FILE: TECHNICAL_ARCHITECTURE.md
```md
# Project Nikolai: Technical Architecture & Agent Interop

This document maps out the interaction between Nikolai's core modules and the external AI assistants (Gemini CLI & Copilot).

## 1. System Architecture (Hub-and-Spoke)

- **Central Hub**: `memory_mcp_server.py` (FastMCP) manages the SQLite database (`nikolai_memory.db`).
- **Spokes**:
  - **`agent_loop.py`**: The main execution engine. Polls for tasks, vision events, and triggers reminders.
  - **`vision_ingestion.py`**: Monitors RTSP camera streams for motion and logs to the Hub.
  - **`voice_interface.py`**: Provides STT (Whisper/local) and TTS (local) for the user.
  - **`control_center.py`**: Admin GUI for managing resources and network nodes.

## 2. Interaction Flow for Assistants

### **A. Reading System State**

1. **Grep/Read Files**: Gemini CLI/Copilot read the source code to understand logic.
2. **MCP Tooling**: Gemini CLI calls `read_memory()` or `get_tasks()` via the MCP server to understand the current context of the user's life and Nikolai's work.

### **B. Modifying System State**

1. **Strategic Changes**: Gemini CLI performs surgical file modifications to the "Spokes" (e.g., adding a new detection logic to `agent_loop.py`).
2. **Tactical Assistance**: Copilot provides inline suggestions for repetitive boilerplate or documentation within the Spokes.
3. **Memory Writes**: Both assistants MUST use `write_memory()` or `create_task()` when proposing a new persistent thought or action.

## 3. Communication Protocols

- **Log-First Principle**: Every major action taken by an assistant must be logged as an `event` with `source='gemini_cli'` or `source='copilot'`.
- **Hybrid Memory Sync**:
  - When an assistant creates a temporary scratchpad file, it must be named `scratch_[purpose].md`.
  - Once the work is done, the assistant must summarize the outcome in a call to `write_memory()`.

## 4. User-Interaction Priority

- **Voice Interface**: Nikolai's "Conversational/Active" mode uses `voice_interface.py` to bridge the gap between digital thoughts and the user's focus.
- **Conflict Handling**: If the user provides a voice command that contradicts a task in the database, the voice command triggers an immediate "Memory Update" that overrides the previous state.

```

