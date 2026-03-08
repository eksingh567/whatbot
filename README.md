# whatbot

A fast, free WhatsApp bulk sender desktop app using **Python + Tkinter + WhatsApp Web**.

## Features
- Load contacts from CSV/XLSX (`phone` required, `name` optional)
- Personalized messages with `{name}` placeholder
- Optional headers and footers
- Optional image/media sending
- Status table (`Pending`, `Sending`, `Sent`, `Failed`)
- Randomized send delay (min/max) to reduce spam-like timing

## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run:
   ```bash
   python whatsapp_bot.py
   ```
3. WhatsApp Web opens automatically.
4. Scan QR from your phone.
5. Load contacts and click **START SENDING**.

## Contacts format
Use CSV/XLSX with these columns:

| phone | name |
|---|---|
| 919999999999 | Alex |
| +1 (555) 123-4567 | Sam |

The app strips non-numeric characters from `phone` automatically.

## Notes
- Keep WhatsApp Web open while sending.
- This tool uses `pywhatkit`, so speed depends on browser/web timing.
- Use responsibly and follow WhatsApp policies.
