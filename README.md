# whatbot

Fast, free WhatsApp bulk sender desktop app using **Python + Tkinter + WhatsApp Web**.

## What's faster now?
This app now has **Fast (Selenium)** mode as default:
- Keeps one browser session open.
- Sends text messages directly in WhatsApp Web chat pages.
- Avoids the heavier open/close cycle per message from pywhatkit.

For media sending, it automatically falls back to **Compatible (PyWhatKit)** mode.

## Features
- Load contacts from CSV/XLSX (`phone` required, `name` optional)
- Personalized messages with `{name}` placeholder
- Optional headers and footers
- Fast send mode (Selenium)
- Compatible send mode (PyWhatKit)
- Optional image/media sending
- Status table (`Pending`, `Sending`, `Sent`, `Failed`)
- Randomized send delay

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
- Fast mode requires a local Chrome + ChromeDriver-compatible Selenium setup.
- Keep WhatsApp Web open while sending.
- Use responsibly and follow WhatsApp policies.
