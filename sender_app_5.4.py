import pandas as pd
import pywhatkit as kit
import time
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import webbrowser

# ========= OPEN WHATSAPP =========
def connect_whatsapp():
    messagebox.showinfo(
        "Login Required",
        "WhatsApp Web will open now.\n\n"
        "Scan QR code from your phone.\n"
        "Wait 30 seconds for login."
    )
    webbrowser.open("https://web.whatsapp.com")
    time.sleep(30)
    bring_app_to_front()

def bring_app_to_front():
    root.after(0, lambda: root.attributes('-topmost', True))
    root.after(200, lambda: root.attributes('-topmost', False))
    root.after(300, lambda: root.lift())
    root.after(400, lambda: root.focus_force())

# ========= GLOBAL DATA =========
numbers_file = None
media_files = []
row_map = {}

# ========= LOAD CONTACTS =========
def load_numbers():
    global row_map
    df = pd.read_excel(numbers_file, dtype=str)
    df.columns = df.columns.str.strip().str.lower()

    table.delete(*table.get_children())
    row_map.clear()

    for _, row in df.iterrows():
        if pd.isna(row.get('phone')):
            continue

        phone = ''.join(filter(str.isdigit, row['phone']))
        name = str(row.get('name', '')).strip()

        if name.lower() == "nan":
            name = ""

        row_id = table.insert('', 'end', values=(phone, name, "Pending"))
        row_map[phone] = (row_id, name)

# ========= SAFE STATUS UPDATE =========
def update_status(phone, status):
    def update():
        if phone in row_map:
            row_id, _ = row_map[phone]
            table.set(row_id, "Status", status)
            table.see(row_id)
    root.after(0, update)

# ========= CLEAR SENT =========
def clear_sent():
    sent_rows = []

    for item in table.get_children():
        status = table.set(item, "Status")
        if "Sent" in status:
            sent_rows.append(item)

    for item in sent_rows:
        table.delete(item)

    messagebox.showinfo("Cleared", "Sent contacts removed from status table.")

# ========= DRAG & DROP =========
def drop_excel(event):
    global numbers_file
    numbers_file = event.data.strip().replace("{","").replace("}","")
    excel_label.config(text=os.path.basename(numbers_file))
    load_numbers()

def drop_media(event):
    global media_files
    files = root.tk.splitlist(event.data)
    media_files = [f.strip("{}") for f in files if os.path.exists(f)]

    media_list.delete(0, tk.END)
    for f in media_files:
        media_list.insert(tk.END, os.path.basename(f))

# ========= START SEND =========
def start_send():
    messagebox.showinfo("Info", "Ensure WhatsApp Web is logged in.")
    threading.Thread(target=process_send, daemon=True).start()

# ========= PROCESS SEND =========
def process_send():
    if not numbers_file:
        root.after(0, lambda: messagebox.showerror("Error", "Drop Excel file"))
        return

    message_template = message_box.get("1.0", tk.END)
    message_template = "\n".join(line.rstrip() for line in message_template.splitlines())

    delay = int(delay_entry.get())
    wait_time = int(wait_entry.get())
    total = len(row_map)

    for phone in row_map:
        row_id, name = row_map[phone]
        update_status(phone, "Sending...")

        # PERSONALIZATION
        if use_names.get() and name:
            message = message_template.replace("{name}", name)
        else:
            message = message_template

        final_message = ""

        # HEADERS
        if use_headers.get():
            headers = []
            for h in [header1.get(), header2.get(), header3.get()]:
                if h.strip():
                    headers.append(h.replace("{name}", name))
            if headers:
                final_message += "\n".join(headers) + "\n\n"

        final_message += message + "\n"

        # FOOTERS
        if use_footers.get():
            footers = []
            for f in [footer1.get(), footer2.get(), footer3.get()]:
                if f.strip():
                    footers.append(f.strip())
            if footers:
                final_message += "\n" + "\n".join(footers)

        try:
            if send_media.get() and media_files:
                for media in media_files:
                    kit.sendwhats_image(
                        receiver="+" + phone,
                        img_path=media,
                        caption=final_message,
                        wait_time=wait_time,
                        tab_close=True,
                        close_time=3
                    )
                    time.sleep(delay)
                    bring_app_to_front()
            else:
                kit.sendwhatmsg_instantly(
                    "+" + phone,
                    final_message,
                    wait_time=wait_time,
                    tab_close=True
                )
                time.sleep(delay)
                bring_app_to_front()

            update_status(phone, f"Sent ✓ ({name})")

        except Exception:
            update_status(phone, f"Failed ✗ ({name})")

    root.after(0, lambda: messagebox.showinfo(
        "Completed",
        f"Messaging finished for {total} contacts."
    ))
    bring_app_to_front()

# ========= UI =========
root = TkinterDnD.Tk()

# ========= AUTO FONT SCALING =========
screen_w = root.winfo_screenwidth()

# Base width reference (Full HD)
BASE_WIDTH = 1920

scale_factor = screen_w / BASE_WIDTH

def scale_font(size):
    return max(8, int(size * scale_factor))



root.title("Sender WhatsApp 5.3")

# Auto open WhatsApp once
root.after(1000, lambda: threading.Thread(target=connect_whatsapp, daemon=True).start())

# Get screen size
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

root = TkinterDnD.Tk()
root.title("WhatsApp Sender Pro")

# Get screen size
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# Set window size relative to screen
win_w = int(screen_w * 0.85)
win_h = int(screen_h * 0.85)
root.geometry(f"{win_w}x{win_h}")

root.configure(bg="#f4f6f8")

# ---- AUTO SCALE UI ----
# Base width your UI was designed for
base_width = 1000
scale_factor = win_w / base_width

# Apply scaling to all widgets
root.tk.call("tk", "scaling", scale_factor)


root.configure(bg="#f4f6f8")

main = tk.Frame(root, bg="#f4f6f8")
main.pack(fill="both", expand=True, padx=10, pady=10)

left = tk.Frame(main, bg="#f4f6f8")
left.pack(side="left", fill="both", expand=True)

right = tk.Frame(main, bg="#f4f6f8")
right.pack(side="right", fill="both", expand=True)

# MESSAGE
tk.Label(left, text="Message Editor", font=("Segoe UI", scale_font(16), "bold"),
         bg="#f4f6f8").pack(anchor="w")

message_box = tk.Text(left, height=6, font=("Segoe UI", 11))
message_box.pack(fill="x", pady=4)

# HEADERS
tk.Label(left, text="Headers", font=("Segoe UI", scale_font(12), "bold"),
         bg="#f4f6f8").pack(anchor="w")

header1 = tk.Entry(left); header1.insert(0, "Hello Team"); header1.pack(fill="x")
header2 = tk.Entry(left); header2.insert(0, "*{name}*"); header2.pack(fill="x")
header3 = tk.Entry(left); header3.pack(fill="x")

# FOOTERS
tk.Label(left, text="Footers", font=("Segoe UI", scale_font(12), "bold"),
         bg="#f4f6f8").pack(anchor="w")

footer1 = tk.Entry(left); footer1.pack(fill="x")
footer2 = tk.Entry(left); footer2.insert(0,"Have a Good day."); footer2.pack(fill="x")
footer3 = tk.Entry(left); footer3.insert(0,"*Team Popular - Delhi*"); footer3.pack(fill="x")

# OPTIONS
use_headers = tk.BooleanVar(value=True)
use_footers = tk.BooleanVar(value=True)
use_names = tk.BooleanVar(value=True)
send_media = tk.BooleanVar(value=True)

for text,var in [
    ("Use Headers",use_headers),
    ("Use Footers",use_footers),
    ("Personalize with Names",use_names),
    ("Send Media",send_media)
]:
    tk.Checkbutton(left, text=text, variable=var,
                   bg="#f4f6f8").pack(anchor="w")

# DROP ZONES
tk.Label(left, text="Excel Contacts", font=("Segoe UI", scale_font(12), "bold"),
         bg="#f4f6f8").pack(anchor="w")

excel_drop = tk.Label(left, text="Drop Excel File", bg="#dfe6e9", height=2)
excel_drop.pack(fill="x")
excel_drop.drop_target_register(DND_FILES)
excel_drop.dnd_bind('<<Drop>>', drop_excel)

excel_label = tk.Label(left, text="No file loaded", bg="#f4f6f8")
excel_label.pack(anchor="w")

tk.Label(left, text="Media Files", font=("Segoe UI", scale_font(12), "bold"),
         bg="#f4f6f8").pack(anchor="w")

media_drop = tk.Label(left, text="Drop Media Files", bg="#dfe6e9", height=2)
media_drop.pack(fill="x")
media_drop.drop_target_register(DND_FILES)
media_drop.dnd_bind('<<Drop>>', drop_media)

media_frame = tk.Frame(left)
media_frame.pack(fill="x", pady=4)

media_scroll = tk.Scrollbar(media_frame)
media_scroll.pack(side="right", fill="y")

media_list = tk.Listbox(media_frame, height=4,
                        yscrollcommand=media_scroll.set)
media_list.pack(side="left", fill="x", expand=True)

media_scroll.config(command=media_list.yview)

# SETTINGS
settings = tk.Frame(left, bg="#f4f6f8")
settings.pack(anchor="w")

tk.Label(settings, text="Delay").grid(row=0,column=0)
delay_entry = tk.Entry(settings,width=6); delay_entry.insert(0,"20")
delay_entry.grid(row=0,column=1)

tk.Label(settings, text="Wait").grid(row=0,column=2)
wait_entry = tk.Entry(settings,width=6); wait_entry.insert(0,"30")
wait_entry.grid(row=0,column=3)

tk.Button(left, text="START SENDING",
          bg="#2ecc71", fg="white",
          font=("Segoe UI", 11, "bold"),
          command=start_send).pack(fill="x", pady=6)

tk.Button(left, text="CLEAR SENT FROM STATUS",
          bg="#e74c3c", fg="white",
          font=("Segoe UI", 10, "bold"),
          command=clear_sent).pack(fill="x", pady=4)

# CONTACT TABLE
tk.Label(right, text="Contacts Status",
         font=("Segoe UI", 14, "bold"),
         bg="#f4f6f8").pack()

table_frame = tk.Frame(right)
table_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

columns=("Phone","Name","Status")
table=ttk.Treeview(table_frame, columns=columns,
                   show="headings",
                   yscrollcommand=scrollbar.set)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=90)

table.pack(fill="both", expand=True)
scrollbar.config(command=table.yview)

root.mainloop()