import threading
import time
import random
import logging
from typing import List, Optional
from tkinter import filedialog, messagebox

from utils import SettingsManager, Contact, load_contacts_from_file, build_full_message, logger
from bot import WhatsAppBot
from ui_components import ModernUI

class WhatBotApp:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.bot = WhatsAppBot()
        self.contacts: List[Contact] = []
        self.is_running = False
        
        self.ui = ModernUI(
            settings=self.settings_manager.settings,
            on_start=self.start_campaign,
            on_save=self.save_settings,
            on_load_contacts=self.pick_contacts,
            on_open_browser=self.open_whatsapp_web
        )

    def save_settings(self):
        new_settings = self.ui.get_ui_settings()
        self.settings_manager.save(new_settings)

    def pick_contacts(self):
        file_path = filedialog.askopenfilename(
            title="Select Contacts File",
            filetypes=[("Excel/CSV", "*.xlsx *.csv")]
        )
        if file_path:
            try:
                self.contacts = load_contacts_from_file(file_path)
                self.ui.status_table.clear()
                for contact in self.contacts:
                    self.ui.log_status(contact)
                messagebox.showinfo("Success", f"Loaded {len(self.contacts)} unique contacts.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def open_whatsapp_web(self):
        def _target():
            self.bot.login()
        threading.Thread(target=_target, daemon=True).start()

    def start_campaign(self):
        if self.is_running:
            return
        if not self.contacts:
            messagebox.showwarning("No Contacts", "Please load a contacts file first.")
            return
            
        self.is_running = True
        self.ui.start_btn.configure(state="disabled", text="RUNNING...")
        self.save_settings() # Save before starting
        
        threading.Thread(target=self._campaign_loop, daemon=True).start()

    def _campaign_loop(self):
        settings = self.settings_manager.settings
        template = settings.get("message", "")
        mode = settings.get("mode", "Fast (Selenium)")
        
        count = 0
        total = len(self.contacts)
        
        # If in Selenium mode, ensure logged in
        if mode.startswith("Fast"):
            if not self.bot.login():
                self.ui.after(0, lambda: messagebox.showerror("Bot Error", "Could not connect to WhatsApp Web."))
                self._stop_campaign()
                return

        for contact in self.contacts:
            if not self.is_running:
                break
                
            contact.status = "Sending..."
            self.ui.after(0, lambda c=contact: self.ui.log_status(c))
            
            full_msg = build_full_message(template, contact.name, settings)
            
            success = False
            status_text = "Failed"
            
            try:
                if mode.startswith("Fast"):
                    success, status_text = self.bot.send_no_reload(contact.phone, full_msg)
                else:
                    success, status_text = self.bot.send_pywhatkit(contact.phone, full_msg, wait_time=settings.get("wait_time", 12))
            except Exception as e:
                status_text = f"Error: {str(e)}"
            
            contact.status = status_text
            self.ui.after(0, lambda c=contact: self.ui.log_status(c))
            
            count += 1
            self.ui.after(0, lambda c=count, t=total: self.ui.update_progress(c, t))
            
            if count < total:
                delay = random.randint(settings.get("delay_min", 5), settings.get("delay_max", 15))
                time.sleep(delay)

        self.ui.after(0, lambda: messagebox.showinfo("Done", f"Campaign finished. {count}/{total} processed."))
        self._stop_campaign()

    def _stop_campaign(self):
        self.is_running = False
        self.ui.after(0, lambda: self.ui.start_btn.configure(state="normal", text="START CAMPAIGN"))

    def run(self):
        self.ui.mainloop()

if __name__ == "__main__":
    app = WhatBotApp()
    app.run()
