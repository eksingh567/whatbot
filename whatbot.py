import os
import re
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import pywhatkit as kit
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


@dataclass
class Contact:
    phone: str
    name: str


class WhatsBotApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("WhatBot - Fast & Free WhatsApp Sender")
        self.root.geometry("1220x780")
        self.root.configure(bg="#f4f6f8")

        self.contacts: Dict[str, Contact] = {}
        self.row_map: Dict[str, str] = {}
        self.numbers_file: Optional[Path] = None
        self.media_files: List[Path] = []

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        main = tk.Frame(self.root, bg="#f4f6f8")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(main, bg="#f4f6f8")
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(main, bg="#f4f6f8")
        right.pack(side="right", fill="both", expand=True)

        tk.Label(
            left,
            text="Message Editor",
            font=("Segoe UI", 16, "bold"),
            bg="#f4f6f8",
        ).pack(anchor="w")

        self.message_box = tk.Text(left, height=8, font=("Segoe UI", 11))
        self.message_box.insert(
            "1.0",
            "Hi {name},\n"
            "This is a quick update from our team.\n"
            "Reply STOP if you don't want future messages.",
        )
        self.message_box.pack(fill="x", pady=4)

        tk.Label(left, text="Headers", font=("Segoe UI", 12, "bold"), bg="#f4f6f8").pack(anchor="w")
        self.header1 = tk.Entry(left)
        self.header1.insert(0, "Hello,")
        self.header1.pack(fill="x")
        self.header2 = tk.Entry(left)
        self.header2.insert(0, "*{name}*")
        self.header2.pack(fill="x")
        self.header3 = tk.Entry(left)
        self.header3.pack(fill="x")

        tk.Label(left, text="Footers", font=("Segoe UI", 12, "bold"), bg="#f4f6f8").pack(anchor="w")
        self.footer1 = tk.Entry(left)
        self.footer1.insert(0, "Thanks")
        self.footer1.pack(fill="x")
        self.footer2 = tk.Entry(left)
        self.footer2.insert(0, "- WhatBot")
        self.footer2.pack(fill="x")
        self.footer3 = tk.Entry(left)
        self.footer3.pack(fill="x")

        self.use_headers = tk.BooleanVar(value=True)
        self.use_footers = tk.BooleanVar(value=True)
        self.use_names = tk.BooleanVar(value=True)
        self.send_media = tk.BooleanVar(value=False)

        for text, var in [
            ("Use Headers", self.use_headers),
            ("Use Footers", self.use_footers),
            ("Personalize with Names", self.use_names),
            ("Send Media", self.send_media),
        ]:
            tk.Checkbutton(left, text=text, variable=var, bg="#f4f6f8").pack(anchor="w")

        self._file_controls(left)
        self._settings(left)
        self._table(right)

    def _file_controls(self, left: tk.Frame) -> None:
        tk.Label(left, text="Contacts File (Excel/CSV)", font=("Segoe UI", 12, "bold"), bg="#f4f6f8").pack(anchor="w")

        file_row = tk.Frame(left, bg="#f4f6f8")
        file_row.pack(fill="x", pady=3)

        tk.Button(file_row, text="Load Contacts", command=self.pick_numbers_file, bg="#3498db", fg="white").pack(side="left")
        self.file_label = tk.Label(file_row, text="No file loaded", bg="#f4f6f8")
        self.file_label.pack(side="left", padx=8)

        tk.Label(left, text="Media Files (optional)", font=("Segoe UI", 12, "bold"), bg="#f4f6f8").pack(anchor="w")
        media_row = tk.Frame(left, bg="#f4f6f8")
        media_row.pack(fill="x")
        tk.Button(media_row, text="Add Media", command=self.pick_media, bg="#9b59b6", fg="white").pack(side="left")

        self.media_list = tk.Listbox(left, height=4)
        self.media_list.pack(fill="x", pady=4)

    def _settings(self, left: tk.Frame) -> None:
        settings = tk.Frame(left, bg="#f4f6f8")
        settings.pack(anchor="w", pady=4)

        tk.Label(settings, text="Delay (sec)", bg="#f4f6f8").grid(row=0, column=0)
        self.delay_entry = tk.Entry(settings, width=6)
        self.delay_entry.insert(0, "10")
        self.delay_entry.grid(row=0, column=1)

        tk.Label(settings, text="Wait (sec)", bg="#f4f6f8").grid(row=0, column=2, padx=(8, 0))
        self.wait_entry = tk.Entry(settings, width=6)
        self.wait_entry.insert(0, "20")
        self.wait_entry.grid(row=0, column=3)

        button_row = tk.Frame(left, bg="#f4f6f8")
        button_row.pack(fill="x", pady=4)

        tk.Button(
            button_row,
            text="1) Open WhatsApp Web",
            bg="#34495e",
            fg="white",
            command=lambda: threading.Thread(target=self.connect_whatsapp, daemon=True).start(),
        ).pack(fill="x", pady=2)

        tk.Button(
            button_row,
            text="2) START SENDING",
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            command=self.start_send,
        ).pack(fill="x", pady=2)

        tk.Button(
            button_row,
            text="Clear Sent from Status",
            bg="#e74c3c",
            fg="white",
            command=self.clear_sent,
        ).pack(fill="x", pady=2)

    def _table(self, right: tk.Frame) -> None:
        tk.Label(right, text="Contacts Status", font=("Segoe UI", 14, "bold"), bg="#f4f6f8").pack()

        table_frame = tk.Frame(right)
        table_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("Phone", "Name", "Status")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=170 if col != "Status" else 260)

        self.table.pack(fill="both", expand=True)
        scrollbar.config(command=self.table.yview)

    # ---------- File loading ----------
    def pick_numbers_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select contacts file",
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        self.numbers_file = Path(path)
        self.file_label.config(text=self.numbers_file.name)
        self.load_numbers()

    def pick_media(self) -> None:
        files = filedialog.askopenfilenames(title="Select media files")
        if not files:
            return

        self.media_files = [Path(f) for f in files if Path(f).exists()]
        self.media_list.delete(0, tk.END)
        for item in self.media_files:
            self.media_list.insert(tk.END, item.name)

    def load_numbers(self) -> None:
        if not self.numbers_file:
            return

        df = self._read_contacts_file(self.numbers_file)
        if df is None:
            return

        self.table.delete(*self.table.get_children())
        self.contacts.clear()
        self.row_map.clear()

        loaded = 0
        for _, row in df.iterrows():
            raw_phone = "" if pd.isna(row.get("phone")) else str(row.get("phone"))
            phone = self.normalize_phone(raw_phone)
            if not phone:
                continue

            name = "" if pd.isna(row.get("name")) else str(row.get("name")).strip()
            contact = Contact(phone=phone, name=name)

            row_id = self.table.insert("", "end", values=(contact.phone, contact.name, "Pending"))
            self.contacts[contact.phone] = contact
            self.row_map[contact.phone] = row_id
            loaded += 1

        messagebox.showinfo("Contacts Loaded", f"Loaded {loaded} contacts.")

    def _read_contacts_file(self, path: Path) -> Optional[pd.DataFrame]:
        try:
            if path.suffix.lower() == ".csv":
                df = pd.read_csv(path, dtype=str)
            else:
                df = pd.read_excel(path, dtype=str)

            df.columns = [c.strip().lower() for c in df.columns]
            if "phone" not in df.columns:
                messagebox.showerror("Invalid file", "The file must include a 'phone' column.")
                return None
            if "name" not in df.columns:
                df["name"] = ""
            return df
        except Exception as exc:
            messagebox.showerror("Read error", f"Could not read contacts file:\n{exc}")
            return None

    @staticmethod
    def normalize_phone(raw: str) -> str:
        digits = re.sub(r"\D", "", raw)
        return digits

    # ---------- Sending ----------
    def connect_whatsapp(self) -> None:
        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "Login Required",
                "WhatsApp Web will open now.\n\nScan QR code and wait at least 20-30 seconds.",
            ),
        )
        webbrowser.open("https://web.whatsapp.com")

    def clear_sent(self) -> None:
        sent_rows = [
            row_id
            for row_id in self.table.get_children()
            if "Sent" in self.table.set(row_id, "Status")
        ]
        for row_id in sent_rows:
            self.table.delete(row_id)
        messagebox.showinfo("Done", "Sent contacts removed from the table.")

    def start_send(self) -> None:
        if not self.contacts:
            messagebox.showerror("No contacts", "Load contacts first.")
            return

        threading.Thread(target=self.process_send, daemon=True).start()

    def process_send(self) -> None:
        try:
            delay = int(self.delay_entry.get().strip())
            wait_time = int(self.wait_entry.get().strip())
        except ValueError:
            self.root.after(0, lambda: messagebox.showerror("Invalid settings", "Delay and Wait must be integers."))
            return

        message_template = self.message_box.get("1.0", tk.END).strip()
        total = len(self.contacts)

        for phone, contact in self.contacts.items():
            self.update_status(phone, "Sending...")
            payload = self.build_message(contact.name, message_template)

            try:
                if self.send_media.get() and self.media_files:
                    for media in self.media_files:
                        kit.sendwhats_image(
                            receiver=f"+{phone}",
                            img_path=str(media),
                            caption=payload,
                            wait_time=wait_time,
                            tab_close=True,
                            close_time=2,
                        )
                        time.sleep(delay)
                else:
                    kit.sendwhatmsg_instantly(
                        phone_no=f"+{phone}",
                        message=payload,
                        wait_time=wait_time,
                        tab_close=True,
                        close_time=2,
                    )
                    time.sleep(delay)

                self.update_status(phone, f"Sent ✓ ({contact.name})")
            except Exception as exc:
                self.update_status(phone, f"Failed ✗ ({contact.name}) - {type(exc).__name__}")

        self.root.after(0, lambda: messagebox.showinfo("Completed", f"Finished sending messages to {total} contacts."))

    def build_message(self, name: str, message_template: str) -> str:
        message = message_template
        if self.use_names.get() and name:
            message = message.replace("{name}", name)

        lines: List[str] = []
        if self.use_headers.get():
            for header in [self.header1.get(), self.header2.get(), self.header3.get()]:
                if header.strip():
                    lines.append(header.replace("{name}", name))

        lines.append(message)

        if self.use_footers.get():
            for footer in [self.footer1.get(), self.footer2.get(), self.footer3.get()]:
                if footer.strip():
                    lines.append(footer.strip())

        return "\n".join(lines).strip()

    def update_status(self, phone: str, status: str) -> None:
        def _set() -> None:
            row_id = self.row_map.get(phone)
            if not row_id:
                return
            self.table.set(row_id, "Status", status)
            self.table.see(row_id)

        self.root.after(0, _set)


def main() -> None:
    root = tk.Tk()
    app = WhatsBotApp(root)
    root.after(700, lambda: threading.Thread(target=app.connect_whatsapp, daemon=True).start())
    root.mainloop()


if __name__ == "__main__":
    main()
