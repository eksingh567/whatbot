import random
import time
import logging
from typing import Callable, Optional, Tuple
from urllib.parse import quote

import pywhatkit as kit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger("WhatBot.Bot")

class WhatsAppBot:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.mode = "Fast (Selenium)"
        self.user_data_dir = ".whatsapp_profile"
        self.wait = None

    def _ensure_driver(self):
        if self.driver is not None:
            try:
                # Check if driver is still alive
                self.driver.current_url
                return
            except Exception:
                self.driver = None

        logger.info("Initializing Selenium driver...")
        options = Options()
        options.add_argument("--start-maximized")
        # Persistent profile to avoid repeated QR scans
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        # Suppress chrome logs
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, timeout: int = 120):
        """Opens WhatsApp Web and waits for login."""
        self._ensure_driver()
        if "web.whatsapp.com" not in self.driver.current_url:
            self.driver.get("https://web.whatsapp.com")
        
        logger.info("Waiting for WhatsApp login (scan QR if needed)...")
        
        try:
            # Wait for either the chat list or the QR code
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side'] | //canvas[@aria-label='Scan me!']"))
            )
            
            # Check if logged in (pane-side exists)
            try:
                self.driver.find_element(By.XPATH, "//div[@id='pane-side']")
                logger.info("Logged in successfully.")
                return True
            except:
                logger.info("QR code visible. Please scan.")
                # Wait longer for the pane-side after QR scan
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']"))
                )
                return True
        except Exception as e:
            logger.error(f"Login timeout or error: {e}")
            return False

    def send_no_reload(self, phone: str, message: str) -> Tuple[bool, str]:
        """Sends a message using the internal search box (No Reload). Much faster."""
        self._ensure_driver()
        
        try:
            # 1. Find Search Box
            search_box_xpath = "//div[@contenteditable='true'][@data-tab='3'] | //div[@data-testid='chat-list-search']"
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, search_box_xpath)))
            
            # Clear search box (Ctrl+A then Backspace for stability)
            search_box.click()
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACKSPACE)
            
            # Type phone number and press Enter
            search_box.send_keys(phone)
            time.sleep(1.5) # Wait for results
            search_box.send_keys(Keys.ENTER)
            
            # 2. Wait for conversation to open and message box to appear
            msg_box_xpath = "//div[@contenteditable='true'][@data-tab='10'] | //div[@data-testid='conversation-compose-box-input']"
            msg_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, msg_box_xpath)))
            
            # 3. Type message and send
            # Use JS to inject text if it's very long for speed, or just send_keys
            # For multiline, we need to handle it properly
            for line in message.split('\n'):
                msg_box.send_keys(line)
                msg_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            msg_box.send_keys(Keys.ENTER)
            time.sleep(1) # Wait for send indicator
            
            return True, "Sent ✓ (No-Reload)"
            
        except Exception as e:
            logger.warning(f"No-Reload failed for {phone}: {e}. Falling back to URL method.")
            return self.send_selenium_url(phone, message)

    def send_selenium_url(self, phone: str, message: str) -> Tuple[bool, str]:
        """Falls back to URL-based send if internal search fails."""
        self._ensure_driver()
        url = f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}"
        self.driver.get(url)
        
        selectors = [
            "//button[@aria-label='Send']",
            "//span[@data-testid='send']",
            "//span[@data-icon='send']/ancestor::button"
        ]
        xhr_path = " | ".join(selectors)
        
        try:
            send_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xhr_path)))
            time.sleep(1)
            send_btn.click()
            time.sleep(2)
            return True, "Sent ✓ (URL)"
        except Exception as e:
            logger.error(f"URL send failed for {phone}: {e}")
            return False, f"Failed ✗ ({type(e).__name__})"

    def send_pywhatkit(self, phone: str, message: str, wait_time: int = 15, media_path: Optional[str] = None):
        """Sends a message using pywhatkit (fallback/media)."""
        try:
            if media_path:
                kit.sendwhats_image(
                    receiver=f"+{phone}",
                    img_path=media_path,
                    caption=message,
                    wait_time=wait_time,
                    tab_close=True,
                    close_time=3
                )
            else:
                kit.sendwhatmsg_instantly(
                    phone_no=f"+{phone}",
                    message=message,
                    wait_time=wait_time,
                    tab_close=True,
                    close_time=3
                )
            return True, "Sent ✓ (via Kit)"
        except Exception as e:
            logger.error(f"Failed to send to {phone} via PyWhatKit: {e}")
            return False, f"Failed ✗ ({type(e).__name__})"

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
