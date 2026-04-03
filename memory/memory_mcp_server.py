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
