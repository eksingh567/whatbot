import tkinter as tk
from typing import List, Callable, Optional, Dict
import os
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils import Contact, build_full_message

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ScrollableStatusTable(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Headers
        ctk.CTkLabel(self, text="Phone", font=("Inter", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Name", font=("Inter", 12, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self, text="Status", font=("Inter", 12, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.rows: Dict[str, Dict[str, ctk.CTkLabel]] = {}

    def update_contact(self, contact: Contact):
        if contact.phone not in self.rows:
            row_idx = len(self.rows) + 1
            labels = {
                "phone": ctk.CTkLabel(self, text=contact.phone),
                "name": ctk.CTkLabel(self, text=contact.name),
                "status": ctk.CTkLabel(self, text=contact.status, text_color="#3498db")
            }
            labels["phone"].grid(row=row_idx, column=0, padx=10, pady=2, sticky="w")
            labels["name"].grid(row=row_idx, column=1, padx=10, pady=2, sticky="w")
            labels["status"].grid(row=row_idx, column=2, padx=10, pady=2, sticky="w")
            self.rows[contact.phone] = labels
        else:
            self.rows[contact.phone]["status"].configure(text=contact.status)
            # Update color based on status
            if "Sent" in contact.status:
                self.rows[contact.phone]["status"].configure(text_color="#2ecc71")
            elif "Failed" in contact.status:
                self.rows[contact.phone]["status"].configure(text_color="#e74c3c")
            elif "Sending" in contact.status:
                self.rows[contact.phone]["status"].configure(text_color="#f1c40f")

    def clear(self):
        for labels in self.rows.values():
            for lbl in labels.values():
                lbl.destroy()
        self.rows.clear()

class ModernUI(ctk.CTk):
    def __init__(self, settings: Dict, 
                 on_start: Callable, 
                 on_save: Callable, 
                 on_load_contacts: Callable,
                 on_open_browser: Callable):
        super().__init__()
        
        self.settings = settings
        self.on_start = on_start
        self.on_save = on_save
        self.on_load_contacts = on_load_contacts
        self.on_open_browser = on_open_browser
        
        self.title("WhatBot - Premium WhatsApp Automation")
        self.geometry("1100x750")
        
        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._setup_sidebar()
        self._setup_main_area()
        
    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="WhatBot v2", font=("Inter", 24, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_send = ctk.CTkButton(self.sidebar, text="Campaign", command=lambda: self._show_page("send"))
        self.btn_send.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_contacts = ctk.CTkButton(self.sidebar, text="Load Contacts", command=self.on_load_contacts)
        self.btn_contacts.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_browser = ctk.CTkButton(self.sidebar, text="Open WhatsApp Web", command=self.on_open_browser, fg_color="#34495e")
        self.btn_browser.grid(row=3, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

    def _setup_main_area(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Dashboard Page
        self.dashboard_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)
        
        # Left Side: Message Composition
        left_col = ctk.CTkFrame(self.dashboard_frame)
        left_col.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(left_col, text="Message Template", font=("Inter", 16, "bold")).pack(anchor="w", padx=10, pady=10)
        self.msg_box = ctk.CTkTextbox(left_col, height=150)
        self.msg_box.pack(fill="x", padx=10, pady=5)
        self.msg_box.insert("1.0", self.settings.get("message", ""))
        
        # Headers/Footers
        ctk.CTkLabel(left_col, text="Dynamic Headers", font=("Inter", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.headers_entries = []
        for i, val in enumerate(self.settings.get("headers", ["", "", ""])):
            entry = ctk.CTkEntry(left_col, placeholder_text=f"Header {i+1}")
            entry.insert(0, val)
            entry.pack(fill="x", padx=10, pady=2)
            self.headers_entries.append(entry)
            
        ctk.CTkLabel(left_col, text="Dynamic Footers", font=("Inter", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.footers_entries = []
        for i, val in enumerate(self.settings.get("footers", ["", "", ""])):
            entry = ctk.CTkEntry(left_col, placeholder_text=f"Footer {i+1}")
            entry.insert(0, val)
            entry.pack(fill="x", padx=10, pady=2)
            self.footers_entries.append(entry)

        # Right Side: Controls and Status
        right_col = ctk.CTkFrame(self.dashboard_frame)
        right_col.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 0))
        right_col.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_col, text="Campaign Controls", font=("Inter", 16, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Settings Row
        settings_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        settings_frame.pack(fill="x", padx=10)
        
        self.mode_var = tk.StringVar(value=self.settings.get("mode", "Fast (Selenium)"))
        ctk.CTkLabel(settings_frame, text="Mode:").grid(row=0, column=0, padx=5, pady=5)
        self.mode_menu = ctk.CTkOptionMenu(settings_frame, values=["Fast (Selenium)", "Compatible (PyWhatKit)"], variable=self.mode_var)
        self.mode_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Status Table
        ctk.CTkLabel(right_col, text="Live Status", font=("Inter", 14, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        self.status_table = ScrollableStatusTable(right_col)
        self.status_table.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Start Button
        self.start_btn = ctk.CTkButton(right_col, text="START CAMPAIGN", font=("Inter", 16, "bold"), 
                                      fg_color="#2ecc71", hover_color="#27ae60", height=45,
                                      command=self.on_start)
        self.start_btn.pack(fill="x", padx=10, pady=10)

        # Progress bar
        self.progress = ctk.CTkProgressBar(right_col)
        self.progress.pack(fill="x", padx=10, pady=(0, 10))
        self.progress.set(0)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def _show_page(self, page):
        # Only one page for now, but extensible
        pass

    def get_ui_settings(self) -> Dict:
        return {
            "message": self.msg_box.get("1.0", "end-1c"),
            "headers": [e.get() for e in self.headers_entries],
            "footers": [e.get() for e in self.footers_entries],
            "mode": self.mode_var.get()
        }

    def update_progress(self, current: int, total: int):
        if total > 0:
            self.progress.set(current / total)

    def log_status(self, contact: Contact):
        self.status_table.update_contact(contact)
