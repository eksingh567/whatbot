<div align="center">
  <h1>🤖 WhatBot</h1>
  <p><strong>Fast, free WhatsApp bulk sender desktop app utilizing Python, Tkinter, and WhatsApp Web.</strong></p>

  [![Python](https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=Selenium&logoColor=white)](https://www.selenium.dev/)
  [![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://web.whatsapp.com/)
</div>

---

## ⚡ What's faster now?
This app now has **Fast (Selenium)** mode as default:
- Keeps a single browser session open continuously.
- Sends text messages directly in WhatsApp Web chat pages.
- Avoids the heavier open/close cycle per message associated with pywhatkit.

*For media sending, it automatically falls back to **Compatible (PyWhatKit)** mode.*

## ✨ Key Features
- **Bulk Loading**: Load contacts from CSV/XLSX (`phone` required, `name` optional).
- **Personalization**: Send dynamic messages with the `{name}` placeholder.
- **Formatting**: Optional headers and footers for your campaigns.
- **Dual Modes**: Fast send mode (Selenium) & Compatible send mode (PyWhatKit).
- **Media Support**: Optional image/media sending capabilities.
- **Live Tracking**: Real-time status table (`Pending`, `Sending`, `Sent`, `Failed`).
- **Human Simulation**: Randomized send delays to prevent flagging.

## 🚀 Quick Start
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run Application**:
   ```bash
   python whatsapp_bot.py
   ```
3. WhatsApp Web will open automatically.
4. Scan the QR code from your mobile device.
5. Load your contact list and click **START SENDING**.

## 📁 Contacts Format
Use CSV/XLSX files formatted with the following columns:

| phone | name |
|---|---|
| 919999999999 | Alex |
| +1 (555) 123-4567 | Sam |

*Note: The app strips non-numeric characters from the `phone` column automatically.*

## ⚠️ Important Notes
- **Fast Mode** requires a local Chrome browser and a ChromeDriver-compatible Selenium setup.
- Ensure WhatsApp Web remains open while sending.
- **Use responsibly and strictly adhere to WhatsApp's Terms of Service and Anti-Spam policies.**
