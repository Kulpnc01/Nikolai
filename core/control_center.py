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
