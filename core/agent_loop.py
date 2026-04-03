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
