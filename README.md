# WhatBot

A **fast and free WhatsApp sender** built with Python + Tkinter + `pywhatkit`, inspired by your reference script.

## Features

- Load contacts from **Excel or CSV** (`phone`, `name` columns)
- Personalize messages with `{name}`
- Optional headers/footers
- Send text-only messages or text + media
- Real-time status table (`Pending`, `Sending`, `Sent`, `Failed`)
- One-click WhatsApp Web opener

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python whatbot.py
```

## Contacts format

Use a file with columns:

| phone        | name      |
|--------------|-----------|
| +91 99999... | Alex      |
| 9198888....  | Priya     |

Notes:
- `phone` is required
- `name` is optional
- Non-digit characters are removed automatically from phone numbers

## How to use

1. Click **Open WhatsApp Web** and scan QR.
2. Click **Load Contacts** and choose your Excel/CSV file.
3. (Optional) Add media files.
4. Write your message using `{name}` if needed.
5. Tune **Delay** and **Wait** for speed/stability.
6. Click **START SENDING**.

## Performance tips

- Keep `Delay` low (e.g., 6–10 sec) for faster bulk sends.
- Increase `Wait` (20–35 sec) on slower machines/network.
- Keep Chrome logged into WhatsApp Web for best reliability.

## Important

Use this responsibly:
- Only message users who have opted in.
- Respect WhatsApp policies and local anti-spam regulations.
