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
