import os
import random
import threading
import time
import webbrowser
from dataclasses import dataclass
from urllib.parse import quote

import pandas as pd
import pywhatkit as kit
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


@dataclass
class Contact:
    phone: str
    name: str


class WhatsAppBotApp:
    """Desktop WhatsApp sender with fast Selenium mode + pywhatkit fallback."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Fast & Free WhatsApp Bot")
        self.root.geometry("1200x760")
        self.root.configure(bg="#f4f6f8")

        self.contacts: list[Contact] = []
        self.row_map: dict[str, str] = {}
        self.media_files: list[str] = []
        self.sending = False

        self.driver = None
        self.ui_closed = False

        self.use_headers = tk.BooleanVar(value=True)
        self.use_footers = tk.BooleanVar(value=True)
        self.use_names = tk.BooleanVar(value=True)
        self.send_media = tk.BooleanVar(value=False)
        self.mode_var = tk.StringVar(value="Fast (Selenium)")

        self._build_ui()

    def _build_ui(self):
        main = tk.Frame(self.root, bg="#f4f6f8")
        main.pack(fill="both", expand=True, padx=12, pady=12)
        left = tk.Frame(main, bg="#f4f6f8")
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(main, bg="#f4f6f8")
        right.pack(side="right", fill="both", expand=True)

        tk.Label(left, text="Message", font=("Segoe UI", 14, "bold"), bg="#f4f6f8").pack(anchor="w")
        self.message_box = tk.Text(left, height=7, font=("Segoe UI", 11))
        self.message_box.insert("1.0", "Hello {name},\nThis is a fast and free WhatsApp bot message.")
        self.message_box.pack(fill="x", pady=4)

        tk.Label(left, text="Headers", font=("Segoe UI", 11, "bold"), bg="#f4f6f8").pack(anchor="w")
        self.header1 = tk.Entry(left)
        self.header1.insert(0, "Hello Team")
        self.header1.pack(fill="x")
        self.header2 = tk.Entry(left)
        self.header2.insert(0, "*{name}*")
        self.header2.pack(fill="x")
        self.header3 = tk.Entry(left)
        self.header3.pack(fill="x")

        tk.Label(left, text="Footers", font=("Segoe UI", 11, "bold"), bg="#f4f6f8").pack(anchor="w", pady=(6, 0))
        self.footer1 = tk.Entry(left)
        self.footer1.pack(fill="x")
        self.footer2 = tk.Entry(left)
        self.footer2.insert(0, "Have a great day.")
        self.footer2.pack(fill="x")
        self.footer3 = tk.Entry(left)
        self.footer3.insert(0, "*Your Team*")
        self.footer3.pack(fill="x")

        for label, var in [
            ("Use Headers", self.use_headers),
            ("Use Footers", self.use_footers),
            ("Personalize with Names", self.use_names),
            ("Send Media (uses pywhatkit fallback)", self.send_media),
        ]:
            tk.Checkbutton(left, text=label, variable=var, bg="#f4f6f8").pack(anchor="w")

        controls = tk.Frame(left, bg="#f4f6f8")
        controls.pack(fill="x", pady=8)
        tk.Button(controls, text="Open WhatsApp Web", command=self.open_whatsapp_web, bg="#3498db", fg="white").grid(row=0, column=0, padx=4)
        tk.Button(controls, text="Load Contacts (CSV/XLSX)", command=self.pick_contacts_file).grid(row=0, column=1, padx=4)
        tk.Button(controls, text="Add Media", command=self.pick_media_files).grid(row=0, column=2, padx=4)

        mode_frame = tk.Frame(left, bg="#f4f6f8")
        mode_frame.pack(anchor="w", pady=(4, 2))
        tk.Label(mode_frame, text="Send Mode", bg="#f4f6f8").grid(row=0, column=0, padx=(0, 4))
        ttk.Combobox(mode_frame, textvariable=self.mode_var, values=["Fast (Selenium)", "Compatible (PyWhatKit)"], width=24, state="readonly").grid(row=0, column=1)

        settings = tk.Frame(left, bg="#f4f6f8")
        settings.pack(anchor="w", pady=6)
        tk.Label(settings, text="Wait Time", bg="#f4f6f8").grid(row=0, column=0)
        self.wait_entry = tk.Entry(settings, width=6)
        self.wait_entry.insert(0, "12")
        self.wait_entry.grid(row=0, column=1, padx=4)
        tk.Label(settings, text="Delay Min", bg="#f4f6f8").grid(row=0, column=2)
        self.delay_min_entry = tk.Entry(settings, width=6)
        self.delay_min_entry.insert(0, "2")
        self.delay_min_entry.grid(row=0, column=3, padx=4)
        tk.Label(settings, text="Delay Max", bg="#f4f6f8").grid(row=0, column=4)
        self.delay_max_entry = tk.Entry(settings, width=6)
        self.delay_max_entry.insert(0, "5")
        self.delay_max_entry.grid(row=0, column=5, padx=4)

        btn_frame = tk.Frame(left, bg="#f4f6f8")
        btn_frame.pack(fill="x", pady=8)
        self.start_btn = tk.Button(btn_frame, text="START SENDING", command=self.start_sending, bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"))
        self.start_btn.pack(fill="x")
        tk.Button(btn_frame, text="Clear Sent Rows", command=self.clear_sent, bg="#e74c3c", fg="white").pack(fill="x", pady=4)

        self.meta_label = tk.Label(left, text="No contacts loaded.", bg="#f4f6f8", fg="#333")
        self.meta_label.pack(anchor="w")

        tk.Label(right, text="Contacts Status", font=("Segoe UI", 14, "bold"), bg="#f4f6f8").pack(anchor="w")
        table_frame = tk.Frame(right)
        table_frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        cols = ("Phone", "Name", "Status")
        self.table = ttk.Treeview(table_frame, columns=cols, show="headings", yscrollcommand=scrollbar.set)
        for col, width in [("Phone", 180), ("Name", 160), ("Status", 300)]:
            self.table.heading(col, text=col)
            self.table.column(col, width=width)
        self.table.pack(fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

        tk.Label(right, text="Selected media files", bg="#f4f6f8").pack(anchor="w")
        self.media_list = tk.Listbox(right, height=6)
        self.media_list.pack(fill="x")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _is_fast_mode(self) -> bool:
        return self.mode_var.get().startswith("Fast")

    def _ensure_driver(self):
        if self.driver is not None:
            return
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except Exception as exc:
            raise RuntimeError("Fast mode needs selenium. Run: pip install selenium") from exc

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument(f"--user-data-dir={os.path.abspath('.whatsapp_profile')}")
        self.driver = webdriver.Chrome(options=options)

    def _wait_until_logged_in(self, timeout=120):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']"))
        )

    def open_whatsapp_web(self):
        if self._is_fast_mode():
            try:
                self._ensure_driver()
                self.driver.get("https://web.whatsapp.com")
                messagebox.showinfo("Login", "Scan QR in the opened browser (first time only).")
            except Exception as exc:
                messagebox.showerror("Fast mode error", str(exc))
        else:
            messagebox.showinfo("Login", "WhatsApp Web will open now. Scan QR and keep browser open.")
            webbrowser.open("https://web.whatsapp.com")

    def pick_contacts_file(self):
        path = filedialog.askopenfilename(filetypes=[("Data files", "*.csv *.xlsx *.xls")])
        if not path:
            return
        try:
            self.load_contacts(path)
            self.meta_label.config(text=f"Loaded contacts: {len(self.contacts)} from {os.path.basename(path)}")
        except Exception as exc:
            messagebox.showerror("Load failed", str(exc))

    def load_contacts(self, path: str):
        df = pd.read_csv(path, dtype=str) if path.lower().endswith(".csv") else pd.read_excel(path, dtype=str)
        df.columns = df.columns.str.strip().str.lower()
        if "phone" not in df.columns:
            raise ValueError("Contacts file must include a 'phone' column.")

        self.contacts.clear()
        self.row_map.clear()
        self.table.delete(*self.table.get_children())

        seen = set()
        for _, row in df.iterrows():
            phone = "".join(ch for ch in str(row.get("phone", "")).strip() if ch.isdigit())
            if not phone or phone in seen:
                continue
            seen.add(phone)
            name = str(row.get("name", "")).strip()
            if name.lower() == "nan":
                name = ""
            self.contacts.append(Contact(phone=phone, name=name))
            row_id = self.table.insert("", "end", values=(phone, name, "Pending"))
            self.row_map[phone] = row_id

    def pick_media_files(self):
        files = filedialog.askopenfilenames()
        if not files:
            return
        self.media_files = [f for f in files if os.path.exists(f)]
        self.media_list.delete(0, tk.END)
        for path in self.media_files:
            self.media_list.insert(tk.END, os.path.basename(path))

    def clear_sent(self):
        phone_by_row = {row_id: phone for phone, row_id in self.row_map.items()}
        for row in self.table.get_children():
            if self.table.set(row, "Status").startswith("Sent"):
                self.table.delete(row)
                phone = phone_by_row.get(row)
                if phone:
                    self.row_map.pop(phone, None)

    def update_status(self, phone: str, text: str):
        if self.ui_closed:
            return
        self.root.after(0, lambda: self._update_row(phone, text))

    def _update_row(self, phone: str, text: str):
        if self.ui_closed:
            return
        row_id = self.row_map.get(phone)
        if row_id:
            try:
                if self.table.exists(row_id):
                    self.table.set(row_id, "Status", text)
                    self.table.see(row_id)
                else:
                    self.row_map.pop(phone, None)
            except tk.TclError:
                # Row/table can disappear while worker thread is still posting updates.
                self.row_map.pop(phone, None)

    def start_sending(self):
        if self.sending:
            return
        if not self.contacts:
            messagebox.showerror("No contacts", "Load contacts first.")
            return
        self.sending = True
        self.start_btn.config(state="disabled")
        threading.Thread(target=self._send_loop, daemon=True).start()

    def _compose_message(self, name: str) -> str:
        message = self.message_box.get("1.0", tk.END).strip()
        if self.use_names.get() and name:
            message = message.replace("{name}", name)

        chunks = []
        if self.use_headers.get():
            headers = [self.header1.get(), self.header2.get(), self.header3.get()]
            chunks.extend([h.replace("{name}", name).strip() for h in headers if h.strip()])
        chunks.append(message)
        if self.use_footers.get():
            footers = [self.footer1.get(), self.footer2.get(), self.footer3.get()]
            chunks.extend([f.strip() for f in footers if f.strip()])
        return "\n".join(chunks).strip()

    def _send_via_selenium(self, phone: str, message: str):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        self.driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}")
        send_btn = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send'] | //span[@data-icon='send']/ancestor::button"))
        )
        send_btn.click()

    def _send_via_pywhatkit(self, phone: str, message: str, wait_time: int):
        if self.send_media.get() and self.media_files:
            for media in self.media_files:
                kit.sendwhats_image(
                    receiver=f"+{phone}",
                    img_path=media,
                    caption=message,
                    wait_time=wait_time,
                    tab_close=True,
                    close_time=2,
                )
        else:
            kit.sendwhatmsg_instantly(
                phone_no=f"+{phone}",
                message=message,
                wait_time=wait_time,
                tab_close=True,
                close_time=2,
            )

    def _send_loop(self):
        try:
            wait_time = int(self.wait_entry.get())
            delay_min = int(self.delay_min_entry.get())
            delay_max = int(self.delay_max_entry.get())
            if delay_min > delay_max:
                delay_min, delay_max = delay_max, delay_min

            if self._is_fast_mode():
                self._ensure_driver()
                self.driver.get("https://web.whatsapp.com")
                self._wait_until_logged_in()
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Startup error", str(exc)))
            self._sending_done()
            return

        for contact in self.contacts:
            message = self._compose_message(contact.name)
            self.update_status(contact.phone, "Sending...")
            try:
                if self._is_fast_mode() and not (self.send_media.get() and self.media_files):
                    self._send_via_selenium(contact.phone, message)
                else:
                    self._send_via_pywhatkit(contact.phone, message, wait_time)
                self.update_status(contact.phone, "Sent ✓")
            except Exception as exc:
                self.update_status(contact.phone, f"Failed ✗ ({exc})")
            time.sleep(random.randint(delay_min, delay_max))

        self.root.after(0, lambda: messagebox.showinfo("Done", f"Finished for {len(self.contacts)} contacts."))
        self._sending_done()

    def _sending_done(self):
        self.sending = False
        self.root.after(0, lambda: self.start_btn.config(state="normal"))

    def on_close(self):
        self.ui_closed = True
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WhatsAppBotApp(root)
    root.after(500, app.open_whatsapp_web)
    root.mainloop()


if __name__ == "__main__":
    main()
