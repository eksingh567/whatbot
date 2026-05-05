import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("WhatBot")

@dataclass
class Contact:
    phone: str
    name: str
    status: str = "Pending"

class SettingsManager:
    """Manages persistent application settings."""
    def __init__(self, settings_path: str = "settings.json"):
        self.path = Path(settings_path)
        self.defaults = {
            "theme": "dark",
            "message": "Hello {name},\nThis is a personalized message from WhatBot.",
            "headers": ["Hello Team", "*{name}*", ""],
            "footers": ["", "Have a great day.", "*Your Team*"],
            "use_headers": True,
            "use_footers": True,
            "use_names": True,
            "delay_min": 5,
            "delay_max": 15,
            "wait_time": 12,
            "mode": "Fast (Selenium)"
        }
        self.settings = self.load()

    def load(self) -> Dict[str, Any]:
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    data = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**self.defaults, **data}
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        return self.defaults.copy()

    def save(self, data: Dict[str, Any]):
        self.settings.update(data)
        try:
            with open(self.path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

def normalize_phone(raw_phone: str) -> str:
    """Strips non-numeric characters from phone numbers."""
    return "".join(filter(str.isdigit, str(raw_phone)))

def load_contacts_from_file(file_path: str) -> List[Contact]:
    """Loads contacts from CSV or Excel file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, dtype=str)
        else:
            df = pd.read_excel(path, dtype=str)
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")

    df.columns = df.columns.str.strip().str.lower()
    if "phone" not in df.columns:
        raise ValueError("File must contain a 'phone' column.")

    contacts = []
    seen_phones = set()
    
    for _, row in df.iterrows():
        raw_phone = str(row.get("phone", "")).strip()
        phone = normalize_phone(raw_phone)
        
        if not phone or phone in seen_phones:
            continue
            
        seen_phones.add(phone)
        name = str(row.get("name", "")).strip()
        if name.lower() == "nan":
            name = ""
            
        contacts.append(Contact(phone=phone, name=name))
        
    return contacts

def build_full_message(template: str, name: str, settings: Dict[str, Any]) -> str:
    """Composes the full message with headers, footers, and placeholders."""
    msg = template
    if settings.get("use_names") and name:
        msg = msg.replace("{name}", name)
        
    parts = []
    if settings.get("use_headers"):
        for h in settings.get("headers", []):
            if h.strip():
                parts.append(h.replace("{name}", name).strip())
                
    parts.append(msg)
    
    if settings.get("use_footers"):
        for f in settings.get("footers", []):
            if f.strip():
                parts.append(f.strip())
                
    return "\n".join(parts).strip()
