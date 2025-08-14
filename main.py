# -*- coding: utf-8 -*-
"""
Molo XML – Desktop app (PySide6)
---------------------------------
Single-file application implementing the PRD.

• OS: Windows 10/11 (offline)
• UI: Dropzone + outlet select + days picker + Generate + Open Folder
• Input: Storyous Excel export (monthly, list with daily rows)
• Output: 1 XML (dataPack) per selected day; includes vch (cash), inv(card), inv(voucher)
• Encoding: Windows-1250; Namespaces/element order mimics provided golden XML
• Never generates invoice/transfer documents

Build (developer):
    py -m pip install PySide6 pandas openpyxl
    pyinstaller --noconfirm --onedir --windowed --name MoloXML main.py

Note: For packaging as MSI, wrap the PyInstaller onedir folder with WiX (outside this file).
"""

from __future__ import annotations
import os
import re
import sys
import json
import uuid
import math
import ctypes
import traceback
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 3rd party
import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets
from lxml import etree as ET

APP_NAME = "LGS XML"
TZ = "Europe/Prague"  # informational; Windows uses local time for yymmdd_hhmmss

# ============================================================================
# MODERN UI STYLING - Minimalist White-Gray with Financial Green Theme
# ============================================================================

COLORS = {
    "primary_green": "#10B981",      # Financial green (emerald)
    "primary_green_hover": "#059669", # Darker green on hover  
    "primary_green_light": "#D1FAE5", # Light green background
    "primary_green_dark": "#047857",  # Even darker green for active states
    "background": "#F8FAFC",         # Very light gray background
    "card_bg": "#FFFFFF",            # Pure white cards
    "border": "#E2E8F0",             # Light gray borders
    "border_hover": "#CBD5E1",       # Slightly darker border on hover
    "text_primary": "#1E293B",       # Dark gray text
    "text_secondary": "#64748B",     # Medium gray text
    "text_muted": "#94A3B8",         # Light gray text
    "shadow": "rgba(0, 0, 0, 0.08)", # Subtle shadow
    "shadow_hover": "rgba(0, 0, 0, 0.12)", # Stronger shadow on hover
    "error": "#EF4444",              # Red for errors
    "warning": "#F59E0B",            # Orange for warnings
    "success": "#10B981",            # Green for success (same as primary)
    "dropzone_bg": "#F1F5F9",        # Light gray for dropzone
    "dropzone_border": "#CBD5E1",    # Border for dropzone
    "dropzone_hover": "#E2E8F0",     # Hover state for dropzone
}

def get_professional_stylesheet() -> str:
    """Return professional stylesheet inspired by modern file upload interfaces"""
    return f"""
    /* Main Application Window - Professional Background */
    QMainWindow {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #FAFBFC, stop: 1 #F1F3F4);
        font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
        font-size: 10pt;
        color: {COLORS['text_primary']};
    }}
    
    /* Remove card styling for compact layout */
    
    /* Professional Dropzone - Compact */
    DropFrame {{
        background-color: #FAFBFF;
        border: 2px dashed #D1D9E0;
        border-radius: 12px;
        min-height: 100px;
        padding: 20px;
        margin: 8px;
    }}
    
    DropFrame:hover {{
        background-color: #F0F7FF;
        border-color: {COLORS['primary_green']};
        border-width: 2px;
        border-style: dashed;
    }}
    
    /* Modern Button System */
    QPushButton {{
        background-color: white;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 500;
        font-size: 10pt;
        color: {COLORS['text_primary']};
        min-height: 20px;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: #F8F9FA;
        border-color: #DADCE0;
    }}
    
    QPushButton:pressed {{
        background-color: #F1F3F4;
    }}
    
    /* Primary Action Button - Professional Green */
    QPushButton#primary {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #16A085, stop: 1 #138D75);
        color: white;
        border: none;
        font-weight: 600;
        font-size: 11pt;
        padding: 16px 32px;
        min-height: 24px;
        border-radius: 12px;
    }}
    
    QPushButton#primary:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #17A589, stop: 1 #148F77);
    }}
    
    QPushButton#primary:pressed {{
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #138D75, stop: 1 #117A65);
    }}
    
    /* Secondary Buttons */
    QPushButton#secondary {{
        background-color: {COLORS['primary_green_light']};
        border: 1px solid {COLORS['primary_green']};
        color: {COLORS['primary_green_dark']};
        font-weight: 600;
    }}
    
    QPushButton#secondary:hover {{
        background-color: white;
    }}
    
    /* Professional ComboBox */
    QComboBox {{
        background-color: white;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 11pt;
        color: {COLORS['text_primary']};
        min-height: 24px;
        font-weight: 500;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['primary_green']};
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['primary_green']};
        border-width: 2px;
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
        padding-right: 8px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid #9AA0A6;
        margin-right: 4px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: white;
        border: 1px solid #E8EAED;
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {COLORS['primary_green_light']};
    }}
    
    /* Input Fields */
    QLineEdit {{
        background-color: white;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 10pt;
        color: {COLORS['text_primary']};
        min-height: 20px;
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['primary_green']};
        border-width: 2px;
    }}
    
    /* Professional Typography */
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: 10pt;
        font-weight: 500;
    }}
    
    QLabel#title {{
        font-size: 18pt;
        font-weight: 700;
        color: #1A1B1F;
        margin-bottom: 4px;
    }}
    
    QLabel#section_header {{
        font-size: 14pt;
        font-weight: 600;
        color: #1A1B1F;
        margin-bottom: 12px;
        margin-top: 8px;
    }}
    
    QLabel#subtitle {{
        color: #5F6368;
        font-size: 9pt;
        font-weight: 400;
        margin-bottom: 16px;
    }}
    
    QLabel#info {{
        color: #5F6368;
        font-size: 9pt;
        font-weight: 400;
        font-style: italic;
    }}
    
    /* Modern Checkboxes */
    QCheckBox {{
        color: {COLORS['text_primary']};
        font-size: 10pt;
        spacing: 12px;
        padding: 4px;
    }}
    
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid #DADCE0;
        border-radius: 6px;
        background-color: white;
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['primary_green']};
        background-color: {COLORS['primary_green_light']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary_green']};
        border-color: {COLORS['primary_green']};
        image: none;
    }}
    
    QCheckBox::indicator:checked:hover {{
        background-color: {COLORS['primary_green_hover']};
    }}
    
    /* Professional Text Areas */
    QTextEdit {{
        background-color: white;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 16px;
        font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
        font-size: 9pt;
        color: {COLORS['text_primary']};
        line-height: 1.5;
    }}
    
    /* Custom Scrollbars */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 12px;
        border-radius: 6px;
        margin: 3px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: #DADCE0;
        border-radius: 6px;
        min-height: 30px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: #BDC1C6;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    
    /* Professional Status Messages */
    QLabel#status_success {{
        color: #137333;
        font-weight: 600;
        background-color: #E8F5E8;
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #137333;
    }}
    
    QLabel#status_error {{
        color: #D93025;
        font-weight: 600;
        background-color: #FCE8E6;
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #D93025;
    }}
    
    QLabel#status_warning {{
        color: #E37400;
        font-weight: 600;
        background-color: #FEF7E0;
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #E37400;
    }}
    """

# Animation and Effects Helper
class ModernEffects:
    @staticmethod
    def add_hover_effect(widget):
        """Add smooth hover effect to any widget"""
        def on_enter(event):
            widget.setProperty("hover", True)
            widget.style().polish(widget)
            
        def on_leave(event):
            widget.setProperty("hover", False) 
            widget.style().polish(widget)
            
        widget.enterEvent = on_enter
        widget.leaveEvent = on_leave
    
    @staticmethod
    def add_click_effect(widget):
        """Add click ripple effect"""
        original_click = widget.mousePressEvent
        
        def enhanced_click(event):
            # Create subtle flash effect
            widget.setProperty("clicked", True)
            widget.style().polish(widget)
            QtCore.QTimer.singleShot(100, lambda: [
                widget.setProperty("clicked", False),
                widget.style().polish(widget)
            ])
            if original_click:
                original_click(event)
                
        widget.mousePressEvent = enhanced_click

# --------------------------------------------------------------------------------------
# Configuration (defaults) – mirrors PRD; can be overridden by external config.json
# --------------------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "version": "1.0",
    "ico": "17126240",
    "programVersion": "14005.6 SQL (14.7.2025)",
    "application": "Transformace",
    "note_text": "tržby",
    "timezone": TZ,
    "output_dir": str(Path.home() / "Documents" / "Pohoda XML"),  # User's preferred output directory
    "naming": {
        "pokladna": "Pokladna {DD.M.YYYY} - {OUTLET} - {ID}.xml",
        "ostatni":  "OstatniPohledavky {DD.M.YYYY} - {METHOD_LABEL} - {OUTLET} - {ID}.xml",
        "id_format": "yymmdd_hhmmss"
    },
    "global_rules": {
        "ignore_invoice_transfer": True,
        "rounding_tolerance": 0.01,
        "encoding": "windows-1250",
        "date_from_filename": True
    },
    "payment_ids": {
        "card":    {"ids": "Plat.kartou", "paymentType": "creditcard"},
        "voucher": {"ids": "Šekem",      "paymentType": "cheque"},
        "cashless": {"ids": "Cashless",  "paymentType": "cashless"}
    },
    "outlets": {
        # Bistro
        "Bistro": {
            "centre": "3", "cashAccount_ids": "Bistro",
            "voucher_header_text": "Tržby hotově Molo Bistro",
            "invoice_header_texts": {
                "cashless": "Tržby Molo Bistro - voucher cashless"
            },
            "accounts": {
                "inv": {"high": "315000/602116", "low": "315000/602114", "none": "315000/602117"},
                "vch": {"high": "211000/602116", "low": "211000/602114", "none": "211000/602117"}
            },
            "item_texts": {
                "cash":     {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":     {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher":  {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"},
                "cashless": {"high": "21% Beverage", "low": "12% Food ", "none": "0% Service Charge"}
            }
        },
        # Restaurant
        "Restaurant": {
            "centre": "1", "cashAccount_ids": "MOLO",
            "invoice_header_texts": {
                "cashless": "Tržby MOLO Restaurant - voucher cashless"
            },
            "accounts": {
                "inv": {"high": "315000/602112", "low": "315000/602110", "none": "315000/602113"},
                "vch": {"high": "211000/602112", "low": "211000/602110", "none": "211000/602113"}
            },
            "item_texts": {
                "cash":     {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":     {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher":  {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"},
                "cashless": {"high": "21% Beverage", "low": "12% Food ", "none": "0% Service Charge"}
            }
        },
        # CDL
        "CDL": {
            "centre": "4", "cashAccount_ids": "CdL",
            "accounts": {
                "inv": {"high": "315000/602123", "low": "315000/602121", "none": "315000/602124"},
                "vch": {"high": "211000/602123", "low": "211000/602121", "none": "211000/602124"}
            },
            "invoice_header_texts": {
                "card": "Tržby Café du Lac - kartou",
                "cashless": "Tržby Café du Lac - voucher cashless"
            },
            "item_texts": {
                "cash":     {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":     {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher":  {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"},
                "cashless": {"high": "21% Beverage", "low": "12% Food ", "none": "0% Service Charge"}
            }
        },
        # B&G
        "B&G": {
            "centre": "1", "cashAccount_ids": "BaG",
            "invoice_header_texts": {
                "cashless": "Tržby Bistro & Grill - voucher cashless"
            },
            "accounts": {
                "inv": {"high": "315000/602112", "low": "315000/602110", "none": "315000/602113"},
                "vch": {"high": "211000/602112", "low": "211000/602110", "none": "211000/602113"}
            },
            "item_texts": {
                "cash":     {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":     {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher":  {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"},
                "cashless": {"high": "21% Beverage", "low": "12% Food ", "none": "0% Service Charge"}
            }
        },
        # Molo2
        "Molo2": {
            "centre": "2", "cashAccount_ids": "MOLO",
            "invoice_header_texts": {
                "cashless": "Tržby MOLO2 - voucher cashless"
            },
            "accounts": {
                "inv": {"high": "315000/602112", "low": "315000/602110", "none": "315000/602113"},
                "vch": {"high": "211000/602112", "low": "211000/602110", "none": "211000/602113"}
            },
            "item_texts": {
                "cash":     {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":     {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher":  {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"},
                "cashless": {"high": "21% Beverage", "low": "12% Food ", "none": "0% Service Charge"}
            }
        }
    },
    # Header mapping via regex – used for all outlets; sections may be absent in specific outlet files
    "header_map": {
        "date_col_candidates": ["^Datum$", "^Den$", "^$"],
        "sections": {
            "cash": {
                "base_high":  "^Základ 21% \\(Hotově\\)$",
                "vat_high":   "^DPH 21% \\(Hotově\\)$",
                "gross_high": "^Tržby s DPH 21% \\(Hotově\\)$",
                "base_low":   "^Základ 12% \\(Hotově\\)$",
                "vat_low":    "^DPH 12% \\(Hotově\\)$",
                "gross_low":  "^Tržby s DPH 12% \\(Hotově\\)$",
                "base_none":  "^Základ 0% \\(Hotově\\)$",
                "vat_none":   "^DPH 0% \\(Hotově\\)$",
                "gross_none": "^Tržby s DPH 0% \\(Hotově\\)$"
            },
            "card": {
                "base_high":  "^Základ 21% \\(Kartou\\)$",
                "vat_high":   "^DPH 21% \\(Kartou\\)$",
                "gross_high": "^Tržby s DPH 21% \\(Kartou\\)$",
                "base_low":   "^Základ 12% \\(Kartou\\)$",
                "vat_low":    "^DPH 12% \\(Kartou\\)$",
                "gross_low":  "^Tržby s DPH 12% \\(Kartou\\)$",
                "base_none":  "^Základ 0% \\(Kartou\\)$",
                "vat_none":   "^DPH 0% \\(Kartou\\)$",
                "gross_none": "^Tržby s DPH 0% \\(Kartou\\)$"
            },
            "voucher": {
                "base_high":  "^Základ 21% \\(Voucher\\)$",
                "vat_high":   "^DPH 21% \\(Voucher\\)$",
                "gross_high": "^Tržby s DPH 21% \\(Voucher\\)$",
                "base_low":   "^Základ 12% \\(Voucher\\)$",
                "vat_low":    "^DPH 12% \\(Voucher\\)$",
                "gross_low":  "^Tržby s DPH 12% \\(Voucher\\)$",
                "base_none":  "^Základ 0% \\(Voucher\\)$",
                "vat_none":   "^DPH 0% \\(Voucher\\)$",
                "gross_none": "^Tržby s DPH 0% \\(Voucher\\)$"
            },
            "cashless": {
                "base_high":  "^Základ 21% \\(Cashless\\)$",
                "vat_high":   "^DPH 21% \\(Cashless\\)$",
                "gross_high": "^Tržby s DPH 21% \\(Cashless\\)$",
                "base_low":   "^Základ 12% \\(Cashless\\)$",
                "vat_low":    "^DPH 12% \\(Cashless\\)$",
                "gross_low":  "^Tržby s DPH 12% \\(Cashless\\)$",
                "base_none":  "^Základ 0% \\(Cashless\\)$",
                "vat_none":   "^DPH 0% \\(Cashless\\)$",
                "gross_none": "^Tržby s DPH 0% \\(Cashless\\)$"
            },
            "invoice_ignore": {"any": ["\\(Faktura\\)", "\\(Bankovní převod\\)"]},
            "totals_ignore":  {"any": ["^Základ Celkem$", "^DPH Celkem$", "^Tržby s DPH Celkem$"]}
        }
    }
}

# Application data in AppData\Local (hidden from user)
APP_DATA_DIR = Path.home() / "AppData" / "Local" / "MoloXML"
CONFIG_DIR = APP_DATA_DIR / "Config"
LOG_DIR = APP_DATA_DIR / "Logs"

# User output files in Documents (visible to user)
OUTPUT_DIR = Path.home() / "Documents" / "Pohoda XML"

# Paths
CONFIG_PATH = CONFIG_DIR / "config.json"
OLD_CONFIG_DIR = Path.home() / "Documents" / "Pohoda XML" / "Config"
OLD_CONFIG_PATH = OLD_CONFIG_DIR / "config.json"

# --------------------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------------------

def ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    ensure_dirs()
    write_log(f"DEBUG: Loading config from {CONFIG_PATH}")
    
    # Migration: if config exists in old location, move it to new location
    if not CONFIG_PATH.exists() and OLD_CONFIG_PATH.exists():
        try:
            # Copy config to new location
            config_content = OLD_CONFIG_PATH.read_text(encoding="utf-8")
            CONFIG_PATH.write_text(config_content, encoding="utf-8")
            # Log after directories are ensured
            write_log(f"Migrated config from old location to {CONFIG_PATH}")
        except Exception as e:
            write_log(f"Config migration failed: {e}")
    
    # Load config from current location
    if CONFIG_PATH.exists():
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            write_log(f"DEBUG: Successfully loaded config with {len(config.get('outlets', {}))} outlets")
            return config
        except Exception as e:
            write_log(f"DEBUG: Failed to load config: {e}")
            pass
    
    # write default if not exists
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return DEFAULT_CONFIG


def save_config(config: dict):
    """Save configuration to config.json"""
    ensure_dirs()
    try:
        CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        write_log(f"Config saved to {CONFIG_PATH}")
    except Exception as e:
        write_log(f"Failed to save config: {e}")


def log_path_today() -> Path:
    now = datetime.now()
    p = LOG_DIR / f"{now:%Y-%m}"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"app_{now:%Y%m%d}.txt"


def write_log(line: str):
    p = log_path_today()
    with p.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%H:%M:%S}] {line}\n")


def norm_number(x) -> float:
    if pd.isna(x):
        return 0.0
    s = str(x)
    s = s.replace("\u00A0", "").replace(" ", "")
    s = s.replace("Kč", "").replace("CZK", "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def yymmdd_hhmmss(now: Optional[datetime] = None) -> str:
    now = now or datetime.now()
    return f"{now:%y%m%d_%H%M%S}"


def parse_month_year_from_filename(path: Path) -> Optional[Tuple[int,int]]:
    m = re.search(r"(\d{1,2})_(\d{4})(?=\.[Xx][Ll][Ss][Xx]$)", path.name)
    if not m:
        # fallback: try anywhere
        m = re.search(r"(\d{1,2})_(\d{4})", path.name)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def next_business_day(d: date) -> date:
    nd = d + timedelta(days=1)
    if nd.weekday() == 5:  # Saturday -> Monday
        nd += timedelta(days=2)
    elif nd.weekday() == 6:  # Sunday -> Monday
        nd += timedelta(days=1)
    return nd

# --------------------------------------------------------------------------------------
# Excel parsing → internal model
# --------------------------------------------------------------------------------------

class ExcelAdapter:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.header_map = cfg.get("header_map", {})
        write_log(f"DEBUG: ExcelAdapter initialized with header_map keys: {list(self.header_map.keys())}")

    def _pick_sheet(self, xl: pd.ExcelFile) -> str:
        # choose sheet containing 'přehled' and 'tržeb'
        for s in xl.sheet_names:
            low = s.lower()
            if "přehled" in low or "prehled" in low:
                if "trž" in low or "trz" in low or "trzeb" in low or "tržeb" in low:
                    return s
        return xl.sheet_names[0]

    def _match_cols(self, columns: List[str], pattern: str) -> Optional[str]:
        rx = re.compile(pattern)
        for c in columns:
            if rx.fullmatch(str(c)):
                return c
        return None

    def _section_values(self, df: pd.DataFrame, section_key: str) -> Dict[str, str]:
        sec = self.header_map.get("sections", {}).get(section_key, {})
        write_log(f"DEBUG: Looking for {section_key} section: {sec}")
        out = {}
        for k, pat in sec.items():
            if not isinstance(pat, str):
                continue
            col = self._match_cols(list(df.columns), pat)
            write_log(f"DEBUG: Pattern '{pat}' -> column '{col}'")
            if col:
                out[k] = col
        write_log(f"DEBUG: Section {section_key} columns: {out}")
        return out

    def read_day(self, xlsx_path: Path, target_day: date) -> Dict[str, Dict[str, float]]:
        xl = pd.ExcelFile(xlsx_path)
        sheet = self._pick_sheet(xl)
        df = xl.parse(sheet)
        df.columns = [str(c).strip() for c in df.columns]
        if df.empty:
            raise ValueError("Prázdný list v Excelu.")

        # date column is first column
        day_col = df.columns[0]
        day_str = df[day_col].astype(str).str.strip()
        candidates = [
            f"{target_day.day}.{target_day.month}.",          # 3.6.
            f"{target_day.day:02d}.{target_day.month:02d}.",  # 03.06.
            f"{target_day.day}.{target_day.month}"            # 3.6 (bez tečky)
        ]
        mask = day_str.isin(candidates)
        if not mask.any():
            raise ValueError(f"Den {target_day.isoformat()} v Excelu nenalezen.")
        row = df.loc[mask].iloc[0]

        # build values
        methods = {"cash": {}, "card": {}, "voucher": {}, "cashless": {}}
        for method_key in ["cash", "card", "voucher", "cashless"]:
            cols = self._section_values(df, method_key)
            for rate_key in ["high", "low", "none"]:
                base = norm_number(row.get(cols.get(f"base_{rate_key}", ""))) if cols.get(f"base_{rate_key}") else 0.0
                vat  = norm_number(row.get(cols.get(f"vat_{rate_key}", ""))) if cols.get(f"vat_{rate_key}") else 0.0
                gross= norm_number(row.get(cols.get(f"gross_{rate_key}", ""))) if cols.get(f"gross_{rate_key}") else round(base+vat, 2)
                methods[method_key][f"base_{rate_key}"] = round(base, 2)
                methods[method_key][f"vat_{rate_key}"]  = round(vat, 2)
                methods[method_key][f"gross_{rate_key}"] = round(gross, 2)
        return methods

    def detect_month_year_from_excel(self, xlsx_path: Path) -> Optional[Tuple[int, int]]:
        """Detect month and year from dates in the first column of Excel file."""
        try:
            xl = pd.ExcelFile(xlsx_path)
            sheet = self._pick_sheet(xl)
            df = xl.parse(sheet)
            if df.empty:
                return None
            day_col = df.columns[0]
            
            # Look for dates in format d.m. or dd.mm.
            months_years = set()
            for v in df[day_col].dropna().astype(str).str.strip():
                m = re.match(r"(\d{1,2})\.(\d{1,2})\.?", v)
                if not m:
                    continue
                mth = int(m.group(2))
                # Try to detect year - could be current year or from filename
                current_year = datetime.now().year
                months_years.add((mth, current_year))
            
            if not months_years:
                return None
            
            # If all dates are from the same month, return that month
            months = set(my[0] for my in months_years)
            if len(months) == 1:
                month = months.pop()
                # Try to get year from filename first, fallback to current year
                filename_my = parse_month_year_from_filename(xlsx_path)
                year = filename_my[1] if filename_my else current_year
                return (month, year)
            
            # If multiple months, try filename or use the most common one
            filename_my = parse_month_year_from_filename(xlsx_path)
            if filename_my:
                return filename_my
            
            # Return the first month found with current year
            return (min(months), current_year)
            
        except Exception:
            return None

    def available_days(self, xlsx_path: Path, month: int, year: int) -> List[int]:
        xl = pd.ExcelFile(xlsx_path)
        sheet = self._pick_sheet(xl)
        df = xl.parse(sheet)
        if df.empty:
            return []
        day_col = df.columns[0]
        days = []
        for v in df[day_col].dropna().astype(str).str.strip():
            m = re.match(r"(\d{1,2})\.(\d{1,2})\.?", v)
            if not m:
                continue
            d = int(m.group(1))
            mth = int(m.group(2))
            if mth == month:
                days.append(d)
        return sorted(set(days))

# --------------------------------------------------------------------------------------
# XML builders (Pohoda)
# --------------------------------------------------------------------------------------

NS = {
    "dat": "http://www.stormware.cz/schema/version_2/data.xsd",
    "inv": "http://www.stormware.cz/schema/version_2/invoice.xsd",
    "vch": "http://www.stormware.cz/schema/version_2/voucher.xsd",
    "typ": "http://www.stormware.cz/schema/version_2/type.xsd",
    "rsp": "http://www.stormware.cz/schema/version_2/response.xsd",
    "rdc": "http://www.stormware.cz/schema/version_2/documentresponse.xsd",
    "ftr": "http://www.stormware.cz/schema/version_2/filter.xsd",
    "lst": "http://www.stormware.cz/schema/version_2/list.xsd",
}
# lxml handles namespaces via nsmap on elements; no global registration needed.


def E(tag: str, text: Optional[str] = None, ns: str = "", attrib: Optional[Dict[str, str]] = None, nsmap: Optional[Dict[str,str]] = None) -> ET.Element:
    """Create XML element with proper namespace (lxml; supports nsmap placement)."""
    if ns:
        uri = NS[ns]
        qname = f"{{{uri}}}{tag}"
    else:
        qname = tag
    if nsmap is not None:
        el = ET.Element(qname, attrib or {}, nsmap=nsmap)
    else:
        el = ET.Element(qname, attrib or {})
    if text is not None:
        el.text = str(text)
    return el


def _fmt(n: float) -> str:
    # integer -> no decimals; else 2 decimals (to mimic samples)
    if abs(n - round(n)) < 0.005:
        return str(int(round(n)))
    return f"{n:.2f}"

def add_sum_home_currency(parent: ET.Element, amounts: Dict[str, float], ns: str):
    home = E("homeCurrency", ns=ns)
    home.append(E("priceNone", _fmt(amounts.get('base_none', 0.0)), "typ"))
    home.append(E("priceLow", _fmt(amounts.get('base_low', 0.0)), "typ"))
    home.append(E("priceLowVAT", _fmt(amounts.get('vat_low', 0.0)), "typ"))
    home.append(E("priceLowSum", _fmt((amounts.get('base_low',0.0)+amounts.get('vat_low',0.0))), "typ"))
    home.append(E("priceHigh", _fmt(amounts.get('base_high', 0.0)), "typ"))
    home.append(E("priceHighVAT", _fmt(amounts.get('vat_high', 0.0)), "typ"))
    home.append(E("priceHighSum", _fmt((amounts.get('base_high',0.0)+amounts.get('vat_high',0.0))), "typ"))
    rnd = E("round", ns="typ")
    rnd.append(E("priceRound", "0", "typ"))
    home.append(rnd)
    parent.append(home)


def build_invoice(method: str, amounts: Dict[str, float], day: date, outlet_cfg: dict) -> ET.Element:
    cfg = load_config()
    # Declare explicit namespace prefix on <inv:invoice>
    inv = E("invoice", ns="inv", attrib={"version": "2.0"}, nsmap={"inv": NS["inv"]})

    # Header with namespace declarations; order mirrors golden XML
    hdr = E("invoiceHeader", ns="inv", nsmap={"rsp": NS["rsp"], "rdc": NS["rdc"], "typ": NS["typ"], "ftr": NS["ftr"], "lst": NS["lst"]})
    hdr.append(E("invoiceType", "receivable", ns="inv"))

    # number - use 2509 prefix for Ostatni Pohledavky, no symVar (will be auto-generated by Pohoda)
    nr = outlet_cfg.get(f"invoice_numberRequested_{method}") or outlet_cfg.get("invoice_numberRequested")
    if not nr:
        nr = "2509"
    num = E("number", ns="inv"); num.append(E("ids", nr, "typ")); hdr.append(num)
    # symVar removed - will be auto-generated by Pohoda

    # dates
    dt_txt = day.strftime("%Y-%m-%d")
    for nm in ("date", "dateTax", "dateAccounting", "dateDue"):
        hdr.append(E(nm, dt_txt, "inv"))

    # header accounting (can differ from item accounts)
    hdr_acc_id = outlet_cfg.get("accounts", {}).get("inv_header") or outlet_cfg["accounts"]["inv"]["high"]
    acc = E("accounting", ns="inv"); acc.append(E("ids", hdr_acc_id, "typ")); hdr.append(acc)

    # VAT class
    clv = E("classificationVAT", ns="inv"); clv.append(E("ids", "UDA5", "typ")); hdr.append(clv)

    # header text (overrideable by config)
    header_texts = outlet_cfg.get("invoice_header_texts", {})
    header_text = header_texts.get(method) or outlet_cfg.get("invoice_header_text") or f"Tržby {method}"
    hdr.append(E("text", header_text, "inv"))

    # myIdentity (company)
    ident = cfg.get("company_identity", {
        "company": "Lipno Gastro Services s.r.o.",
        "city": "Praha",
        "street": "Radlická",
        "number": "751/113e",
        "zip": "158 00",
        "ico": "17126240",
        "dic": "CZ17126240"
    })
    my = E("myIdentity", ns="inv")
    addr = E("address", ns="typ")
    addr.append(E("company", ident.get("company", ""), "typ"))
    addr.append(E("city", ident.get("city", ""), "typ"))
    addr.append(E("street", ident.get("street", ""), "typ"))
    addr.append(E("number", ident.get("number", ""), "typ"))
    addr.append(E("zip", ident.get("zip", ""), "typ"))
    addr.append(E("ico", ident.get("ico", ""), "typ"))
    addr.append(E("dic", ident.get("dic", ""), "typ"))
    my.append(addr)
    hdr.append(my)

    # payment type
    pay = E("paymentType", ns="inv")
    if method == "card":
        pay.append(E("ids", cfg["payment_ids"]["card"]["ids"], "typ"))
        pay.append(E("paymentType", cfg["payment_ids"]["card"]["paymentType"], "typ"))
        liq = next_business_day(day)
    elif method == "cashless":
        pay.append(E("ids", cfg["payment_ids"]["cashless"]["ids"], "typ"))
        liq = day
    else:  # voucher
        pay.append(E("ids", cfg["payment_ids"]["voucher"]["ids"], "typ"))
        pay.append(E("paymentType", cfg["payment_ids"]["voucher"]["paymentType"], "typ"))
        liq = day
    hdr.append(pay)

    # bank account and symConst
    bank = cfg.get("bank", {"ids": "RBCZ", "accountNo": "7415855002", "bankCode": "5500", "symConst": "0308"})
    acc_el = E("account", ns="inv")
    acc_el.append(E("ids", bank.get("ids", "RBCZ"), "typ"))
    acc_el.append(E("accountNo", bank.get("accountNo", ""), "typ"))
    acc_el.append(E("bankCode", bank.get("bankCode", ""), "typ"))
    hdr.append(acc_el)
    hdr.append(E("symConst", bank.get("symConst", "0308"), "inv"))

    # centre, liquidation, locks
    centre = E("centre", ns="inv"); centre.append(E("ids", outlet_cfg["centre"], "typ")); hdr.append(centre)
    liq_el = E("liquidation", ns="inv"); liq_el.append(E("date", liq.strftime("%Y-%m-%d"), "typ")); hdr.append(liq_el)
    hdr.append(E("lock2", "false", "inv")); hdr.append(E("markRecord", "false", "inv"))
    inv.append(hdr)

    # Detail (use _fmt for numbers to match samples)
    det = E("invoiceDetail", ns="inv", nsmap={"rsp": NS["rsp"], "rdc": NS["rdc"], "typ": NS["typ"], "ftr": NS["ftr"], "lst": NS["lst"]})

    def add_item(rate_key: str):
        base = amounts.get(f"base_{rate_key}", 0.0)
        vat  = amounts.get(f"vat_{rate_key}", 0.0)
        # Always include all VAT sections (high, low, none) even if amounts are zero
        it = E("invoiceItem", ns="inv")
        # Use specific item texts for detail items
        item_text = outlet_cfg["item_texts"][method][rate_key]
        it.append(E("text", item_text, "inv"))
        it.append(E("quantity", "1.0", "inv"))
        it.append(E("coefficient", "1.0", "inv"))
        it.append(E("payVAT", "false", "inv"))
        it.append(E("rateVAT", rate_key, "inv"))
        it.append(E("discountPercentage", "0.0", "inv"))
        cur = E("homeCurrency", ns="inv")
        cur.append(E("unitPrice", _fmt(base), "typ"))
        cur.append(E("price", _fmt(base), "typ"))
        cur.append(E("priceVAT", _fmt(vat), "typ"))
        cur.append(E("priceSum", _fmt(base+vat), "typ"))
        it.append(cur)
        # Each item uses its specific account based on rate
        acc = E("accounting", ns="inv"); acc.append(E("ids", outlet_cfg["accounts"]["inv"][rate_key], "typ")); it.append(acc)
        if rate_key == "none":
            cl = E("classificationVAT", ns="inv"); cl.append(E("ids", "UN", "typ")); cl.append(E("classificationVATType", "nonSubsume", "typ")); it.append(cl)
        it.append(E("PDP", "false", "inv"))
        det.append(it)

    for rk in ("high","low","none"):
        add_item(rk)
    inv.append(det)

    # Summary
    sum_el = E("invoiceSummary", ns="inv", nsmap={"rsp": NS["rsp"], "rdc": NS["rdc"], "typ": NS["typ"], "ftr": NS["ftr"], "lst": NS["lst"]})
    # Different rounding for voucher vs card
    rounding_doc = "math2one" if method == "voucher" else "none"
    sum_el.append(E("roundingDocument", rounding_doc, "inv"))
    sum_el.append(E("roundingVAT", "none", "inv"))
    sum_el.append(E("typeCalculateVATInclusivePrice", "VATNewMethod", "inv"))
    add_sum_home_currency(sum_el, amounts, "inv")
    inv.append(sum_el)
    return inv


def build_voucher(amounts: Dict[str, float], day: date, outlet_cfg: dict, outlet_name: Optional[str] = None) -> ET.Element:
    # vch ns declared on <vch:voucher> element (to match samples)
    v = E("voucher", ns="vch", attrib={"version": "2.0"}, nsmap={"vch": NS["vch"]})

    # header with local namespace declarations (rsp, rdc, typ, ftr, lst)
    hdr = E("voucherHeader", ns="vch", nsmap={"rsp": NS["rsp"], "rdc": NS["rdc"], "typ": NS["typ"], "ftr": NS["ftr"], "lst": NS["lst"]})
    hdr.append(E("voucherType", "receipt", "vch"))
    cash = E("cashAccount", ns="vch"); cash.append(E("ids", outlet_cfg["cashAccount_ids"], "typ")); hdr.append(cash)

    # Number generation – resolved with precedence (outlet-specific → mapping → global)
    # ALWAYS generate number as it's required by Pohoda XML schema
    cfg = load_config()
    nr = (
        outlet_cfg.get("voucher_numberRequested")
        or outlet_cfg.get("numberRequested")
        or (cfg.get("voucher_numberRequested_by_outlet", {}) or {}).get(outlet_name or "")
        or cfg.get("voucher_numberRequested")
    )
    
    # If no custom number configured, generate 4-character prefix based on outlet
    if not nr:
        # Mapping outlets to 4-character prefixes
        outlet_prefixes = {
            "Bistro": "BisP",
            "CDL": "CdLP", 
            "B&G": "BaGP",
            "Restaurant": "MOLP",
            "Molo2": "MOLP"
        }
        prefix = outlet_prefixes.get(outlet_name, "UNKN")
        nr = prefix
    
    # ALWAYS add number element (required by Pohoda XML schema)
    num = E("number", ns="vch")
    num.append(E("ids", nr, "typ"))
    hdr.append(num)

    dt_txt = day.strftime("%Y-%m-%d")
    for nm in ("date", "datePayment", "dateTax"):
        hdr.append(E(nm, dt_txt, "vch"))

    acc = E("accounting", ns="vch"); acc.append(E("ids", outlet_cfg["accounts"]["vch"]["high"], "typ")); hdr.append(acc)
    clv = E("classificationVAT", ns="vch"); clv.append(E("ids", "UD", "typ")); hdr.append(clv)

    # header text – keep minimal; can be overridden by config
    header_text = outlet_cfg.get("voucher_header_text", "Tržby hotově")
    hdr.append(E("text", header_text, "vch"))

    # myIdentity (company) – to replicate sample structure
    ident = cfg.get("company_identity", {
        "company": "Lipno Gastro Services s.r.o.",
        "city": "Praha",
        "street": "Radlická",
        "number": "751/113e",
        "zip": "158 00",
        "ico": "17126240",
        "dic": "CZ17126240"
    })
    my = E("myIdentity", ns="vch")
    addr = E("address", ns="typ")
    addr.append(E("company", ident.get("company",""), "typ"))
    addr.append(E("city", ident.get("city",""), "typ"))
    addr.append(E("street", ident.get("street",""), "typ"))
    addr.append(E("number", ident.get("number",""), "typ"))
    addr.append(E("zip", ident.get("zip",""), "typ"))
    addr.append(E("ico", ident.get("ico",""), "typ"))
    addr.append(E("dic", ident.get("dic",""), "typ"))
    my.append(addr)
    hdr.append(my)

    centre = E("centre", ns="vch"); centre.append(E("ids", outlet_cfg["centre"], "typ")); hdr.append(centre)
    hdr.append(E("lock2", "false", "vch")); hdr.append(E("markRecord", "false", "vch"))

    # labels (e.g., Zelená)
    labels = cfg.get("labels", ["Zelená"]) or []
    if labels:
        labs = E("labels", ns="vch")
        for lb in labels:
            lab = E("label", ns="typ"); lab.append(E("ids", lb, "typ")); labs.append(lab)
        hdr.append(labs)

    v.append(hdr)

    # detail
    det = E("voucherDetail", ns="vch", nsmap={"rsp": NS["rsp"], "rdc": NS["rdc"], "typ": NS["typ"], "ftr": NS["ftr"], "lst": NS["lst"]})

    def add_item(rate_key: str):
        base = amounts.get(f"base_{rate_key}", 0.0)
        vat  = amounts.get(f"vat_{rate_key}", 0.0)
        # Always include all VAT sections (high, low, none) even if amounts are zero
        it = E("voucherItem", ns="vch")
        item_text = outlet_cfg["item_texts"]["cash"][rate_key]
        it.append(E("text", item_text, "vch"))
        it.append(E("quantity", "1.0", "vch"))
        it.append(E("coefficient", "1.0", "vch"))
        it.append(E("payVAT", "false", "vch"))
        it.append(E("rateVAT", rate_key, "vch"))
        it.append(E("discountPercentage", "0.0", "vch"))
        cur = E("homeCurrency", ns="vch")
        cur.append(E("unitPrice", _fmt(base), "typ"))
        cur.append(E("price", _fmt(base), "typ"))
        cur.append(E("priceVAT", _fmt(vat), "typ"))
        cur.append(E("priceSum", _fmt(base+vat), "typ"))
        it.append(cur)
        acc = E("accounting", ns="vch"); acc.append(E("ids", outlet_cfg["accounts"]["vch"][rate_key], "typ")); it.append(acc)
        if rate_key == "none":
            cl = E("classificationVAT", ns="vch"); cl.append(E("ids", "UN", "typ")); cl.append(E("classificationVATType", "nonSubsume", "typ")); it.append(cl)
        it.append(E("PDP", "false", "vch"))
        det.append(it)

    for rk in ("high","low","none"):
        add_item(rk)
    v.append(det)

    # summary
    sum_el = E("voucherSummary", ns="vch", nsmap={"rsp": NS["rsp"], "rdc": NS["rdc"], "typ": NS["typ"], "ftr": NS["ftr"], "lst": NS["lst"]})
    sum_el.append(E("roundingDocument", "math2one", "vch"))
    sum_el.append(E("roundingVAT", "none", "vch"))
    sum_el.append(E("typeCalculateVATInclusivePrice", "VATNewMethod", "vch"))
    add_sum_home_currency(sum_el, amounts, "vch")
    v.append(sum_el)
    return v


def build_datapack(day: date, methods: Dict[str, Dict[str, float]], outlet_cfg: dict) -> ET.ElementTree:
    root = E("dataPack", ns="dat", attrib={
        "version": "2.0",
        "id": "Usr01",
        "ico": "",
        "key": str(uuid.uuid4()),
        "programVersion": "MoloXML 1.0",
        "application": "Molo XML Generator",
        "note": f"Uživatelský export, Datum = {day.strftime('%d.%m.%Y')}"
    })

    def add_item(child: ET.Element):
        dpi = E("dataPackItem", ns="dat", attrib={"version": "2.0", "id": "Usr01 (001)"})
        dpi.append(child)
        root.append(dpi)

    # cash → voucher
    if any(methods.get("cash", {}).get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
        add_item(build_voucher(methods.get("cash", {}), day, outlet_cfg))

    # card → invoice
    if any(methods.get("card", {}).get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
        add_item(build_invoice("card", methods.get("card", {}), day, outlet_cfg))

    # voucher → invoice
    if any(methods.get("voucher", {}).get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
        add_item(build_invoice("voucher", methods.get("voucher", {}), day, outlet_cfg))

    return ET.ElementTree(root)

# --------------------------------------------------------------------------------------
# Naming & datapack wrapper
# --------------------------------------------------------------------------------------

def _compute_datapack_key(day: date, outlet: str, doc_type: str, cfg: dict) -> str:
    # 1) explicit fixed key in config
    fixed = cfg.get("fixed_datapack_key") or cfg.get("datapack_key")
    if isinstance(fixed, str) and fixed:
        return fixed
    # 2) mapping by outlet in config
    by_outlet = cfg.get("datapack_key_by_outlet", {}) or {}
    if isinstance(by_outlet, dict):
        val = by_outlet.get(outlet)
        if isinstance(val, str) and val:
            return val
    # 3) deterministic UUIDv5 based on day/outlet/doc_type
    seed = cfg.get("datapack_key_seed", "MoloXML-datapack-key")
    name = f"{seed}|{day.isoformat()}|{outlet}|{doc_type}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, name))


def datapack_with(child: ET.Element, day: date, outlet: str, doc_type: str, note_override: Optional[str] = None) -> ET.ElementTree:
    cfg = load_config()
    # Build note text
    if note_override is not None:
        note = note_override
    else:
        # prefer outlet-specific mapping; fallback to global; ensure B&G → "bar" default if unspecified
        by_outlet = cfg.get("note_text_by_outlet", {}) or {}
        outlet_text = by_outlet.get(outlet)
        if not outlet_text and outlet == "B&G":
            outlet_text = "bar"
        note_extra = outlet_text or cfg.get("note_text", None)
        note = f"Uživatelský export, Datum = {day.strftime('%d.%m.%Y')}" + (f", Text = {note_extra}" if note_extra else "")

    root = E("dataPack", ns="dat", attrib={
        "version": "2.0",
        "id": "Usr01",
        "ico": cfg.get("ico", ""),
        "key": _compute_datapack_key(day, outlet, doc_type, cfg),
        "programVersion": cfg.get("programVersion", "MoloXML 1.0"),
        "application": cfg.get("application", "Molo XML Generator"),
        "note": note
    }, nsmap={"dat": NS["dat"]})
    dpi = E("dataPackItem", ns="dat", attrib={"version": "2.0", "id": "Usr01 (001)"})
    dpi.append(child)
    root.append(dpi)
    return ET.ElementTree(root)

def format_filename(doc_type: str, day: date, outlet: str, method_label: Optional[str] = None) -> str:
    cfg = load_config()
    naming = cfg["naming"]
    ident = yymmdd_hhmmss()
    date_label = f"{day.day}.{day.month}.{day.year}"
    if doc_type == "pokladna":
        patt = naming["pokladna"]
        return patt.replace("{DD.M.YYYY}", date_label).replace("{OUTLET}", outlet).replace("{ID}", ident)
    else:
        patt = naming["ostatni"]
        return patt.replace("{DD.M.YYYY}", date_label).replace("{METHOD_LABEL}", method_label or "").replace("{OUTLET}", outlet).replace("{ID}", ident)


# --------------------------------------------------------------------------------------
# Helper: suggest outlet from filename
# --------------------------------------------------------------------------------------

def suggest_outlet_from_filename(filename: str) -> Optional[str]:
    name = filename.lower()
    patterns = [
        ("bistro", "Bistro"),
        ("restaurant", "Restaurant"),
        ("restaurace", "Restaurant"),
        ("bar & grill", "B&G"),
        ("bar a grill", "B&G"),
        ("b&g", "B&G"),
        ("cdl", "CDL"),
        ("chata", "CDL"),
        ("molo2", "Molo2"),
        ("molo 2", "Molo2"),
    ]
    for pat, outlet in patterns:
        if pat in name:
            return outlet
    return None

# --------------------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------------------

class DropFrame(QtWidgets.QFrame):
    fileDropped = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        
        # Create compact professional dropzone layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Upload icon and text in horizontal layout for compactness
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.setSpacing(12)
        
        # Upload icon (smaller)
        icon_label = QtWidgets.QLabel("📁")
        icon_label.setStyleSheet("font-size: 24px; color: #5F6368;")
        content_layout.addWidget(icon_label)
        
        # Text container
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Main text (smaller)
        main_text = QtWidgets.QLabel("Přetáhněte Excel soubor sem")
        main_text.setStyleSheet("font-size: 12px; font-weight: 600; color: #1A1B1F;")
        text_layout.addWidget(main_text)
        
        # Sub text (smaller)
        sub_text = QtWidgets.QLabel("nebo použijte tlačítko níže • .xlsx")
        sub_text.setStyleSheet("font-size: 10px; color: #5F6368;")
        text_layout.addWidget(sub_text)
        
        content_layout.addLayout(text_layout)
        layout.addLayout(content_layout)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QtGui.QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.fileDropped.emit(path)

class DayPicker(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setHorizontalSpacing(6); self.grid.setVerticalSpacing(6)
        self.checks: Dict[int, QtWidgets.QCheckBox] = {}

    def set_days(self, days: List[int]):
        # clear
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.setParent(None)
        self.checks.clear()
        # layout 7 columns
        row = 0; col = 0
        for d in days:
            cb = QtWidgets.QCheckBox(str(d))
            self.checks[d] = cb
            self.grid.addWidget(cb, row, col)
            col += 1
            if col >= 7:
                col = 0; row += 1

    def selected_days(self) -> List[int]:
        return sorted([d for d, cb in self.checks.items() if cb.isChecked()])

    def mark_all(self, checked: bool = True):
        for cb in self.checks.values():
            cb.setChecked(checked)

    def mark_weekends(self, month: int, year: int):
        for d, cb in self.checks.items():
            wd = date(year, month, d).weekday()
            cb.setChecked(wd >= 5)

    def mark_workdays(self, month: int, year: int):
        for d, cb in self.checks.items():
            wd = date(year, month, d).weekday()
            cb.setChecked(wd < 5)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(900, 600)
        
        # Apply professional styling
        self.setStyleSheet(get_professional_stylesheet())
        
        self.cfg = load_config()
        self.adapter = ExcelAdapter(self.cfg)
        self.xlsx_path: Optional[Path] = None
        self.month_year: Optional[Tuple[int,int]] = None

        # Create compact professional layout (original structure with modern styling)
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Top row: Outlet selection
        top_layout = QtWidgets.QHBoxLayout()
        outlet_lbl = QtWidgets.QLabel("Provoz:")
        outlet_lbl.setObjectName("section_header")
        self.outlet = QtWidgets.QComboBox()
        self.outlet.addItems(["Bistro", "Restaurant", "CDL", "B&G", "Molo2"])
        top_layout.addWidget(outlet_lbl)
        top_layout.addWidget(self.outlet)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # Dropzone
        self.drop = DropFrame()
        self.drop.fileDropped.connect(self.on_file_dropped)
        main_layout.addWidget(self.drop)
        
        # Browse button - compact, not full width
        browse_layout = QtWidgets.QHBoxLayout()
        pick_btn = QtWidgets.QPushButton("📁 Vybrat soubor...")
        pick_btn.clicked.connect(self.pick_file)
        pick_btn.setObjectName("secondary")
        pick_btn.setMaximumWidth(150)
        browse_layout.addWidget(pick_btn)
        browse_layout.addStretch()
        main_layout.addLayout(browse_layout)
        
        # Day info
        self.day_info = QtWidgets.QLabel("Detekováno: —")
        self.day_info.setObjectName("info")
        main_layout.addWidget(self.day_info)
        
        # Day selection controls - compact row above picker
        day_controls_layout = QtWidgets.QHBoxLayout()
        day_controls_layout.addWidget(QtWidgets.QLabel("Vyberte dny:"))
        day_controls_layout.addStretch()
        
        # Compact control buttons
        btn_all = QtWidgets.QPushButton("✓ Vše")
        btn_all.clicked.connect(lambda: self.picker.mark_all(True))
        btn_all.setMaximumWidth(60)
        btn_all.setMaximumHeight(28)
        
        btn_clear = QtWidgets.QPushButton("✗ Clear")
        btn_clear.clicked.connect(lambda: self.picker.mark_all(False))
        btn_clear.setMaximumWidth(60)
        btn_clear.setMaximumHeight(28)
        
        day_controls_layout.addWidget(btn_all)
        day_controls_layout.addWidget(btn_clear)
        main_layout.addLayout(day_controls_layout)
        
        # Day picker grid (now without side controls)
        self.picker = DayPicker()
        main_layout.addWidget(self.picker)
        
        # Output row
        output_layout = QtWidgets.QHBoxLayout()
        output_layout.addWidget(QtWidgets.QLabel("Výstup:"))
        # Load output directory from config, fallback to default
        saved_output_dir = self.cfg.get("output_dir", str(OUTPUT_DIR))
        self.out_dir = QtWidgets.QLineEdit(saved_output_dir)
        output_layout.addWidget(self.out_dir, 1)
        out_btn = QtWidgets.QPushButton("📁 Změnit...")
        out_btn.clicked.connect(self.pick_output_dir)
        output_layout.addWidget(out_btn)
        main_layout.addLayout(output_layout)
        
        # Action buttons row
        action_layout = QtWidgets.QHBoxLayout()
        gen_btn = QtWidgets.QPushButton("🚀 Generovat XML")
        gen_btn.clicked.connect(self.generate)
        gen_btn.setObjectName("primary")
        action_layout.addWidget(gen_btn)
        action_layout.addStretch()
        
        open_btn = QtWidgets.QPushButton("📂 Otevřít složku")
        open_btn.clicked.connect(self.open_output)
        open_btn.setObjectName("secondary")
        action_layout.addWidget(open_btn)
        main_layout.addLayout(action_layout)
        
        # Status section
        status_lbl = QtWidgets.QLabel("📋 Stav:")
        status_lbl.setObjectName("section_header")
        main_layout.addWidget(status_lbl)
        
        self.status = QtWidgets.QTextEdit()
        self.status.setReadOnly(True)
        self.status.setMaximumHeight(120)  # Compact height
        main_layout.addWidget(self.status)

        # Apply modern effects to interactive elements
        ModernEffects.add_hover_effect(gen_btn)
        ModernEffects.add_click_effect(gen_btn)
        ModernEffects.add_hover_effect(pick_btn)
        ModernEffects.add_hover_effect(out_btn)
        ModernEffects.add_hover_effect(open_btn)
        ModernEffects.add_hover_effect(btn_all)
        ModernEffects.add_hover_effect(btn_clear)
        
        self.append_status("Připraveno.")
        self.append_status(f"XML soubory se ukládají do: {OUTPUT_DIR}")
        self.append_status(f"Konfigurace a logy: {APP_DATA_DIR}")

    def append_status(self, msg: str, status_type: str = "info"):
        """Add status message with color coding"""
        # Color-coded status messages
        if "Chyba" in msg or "Error" in msg:
            color = COLORS["error"]
        elif "Hotovo" in msg or "vytvořeno" in msg:
            color = COLORS["success"]
        elif "Varování" in msg or "Warning" in msg:
            color = COLORS["warning"]
        else:
            color = COLORS["text_primary"]
            
        # Add with HTML formatting for color
        self.status.append(f'<span style="color: {color};">• {msg}</span>')
        write_log(msg)

    def pick_file(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Vyber Excel", str(Path.home()), "Excel (*.xlsx)")
        if fn:
            self.on_file_selected(Path(fn))

    def on_file_dropped(self, path: str):
        p = Path(path)
        if p.suffix.lower() != ".xlsx":
            QtWidgets.QMessageBox.warning(self, APP_NAME, "Podporuji pouze .xlsx soubory.")
            return
        self.on_file_selected(p)

    def on_file_selected(self, p: Path):
        self.xlsx_path = p
        self.setWindowTitle(f"{APP_NAME} — {p.name}")
        
        # Try to detect month/year from Excel content first, then from filename
        try:
            my = self.adapter.detect_month_year_from_excel(p)
            if not my:
                my = parse_month_year_from_filename(p)
            
            if not my:
                QtWidgets.QMessageBox.warning(self, APP_NAME, "Nelze odvodit měsíc/rok ani z obsahu Excelu ani z názvu souboru.\n\nUjisti se, že Excel obsahuje data ve formátu den.měsíc v prvním sloupci\nnebo má název ve formátu *_M_YYYY.xlsx")
                return
                
            self.month_year = my
            month, year = my
        except PermissionError:
            QtWidgets.QMessageBox.warning(
                self, APP_NAME,
                "Soubor nelze otevřít (Permission denied).\n\nMožné příčiny:\n- Je otevřený v Excelu → zavřít\n- Je v OneDrive a není dostupný offline → v Průzkumníku zvol 'Vždy ponechat na tomto zařízení'\n- Zkopíruj soubor třeba do 'Dokumenty/' a načti znovu."
            )
            self.append_status(f"Permission denied: {p}")
            return
        except Exception as ex:
            QtWidgets.QMessageBox.warning(self, APP_NAME, f"Chyba při čtení Excelu: {ex}")
            self.append_status(f"Chyba při čtení: {ex}")
            return
        # Offer auto-switch of outlet if filename suggests a different one
        suggested = suggest_outlet_from_filename(p.name)
        if suggested and suggested != self.outlet.currentText():
            reply = QtWidgets.QMessageBox.question(
                self, APP_NAME,
                f"Zdá se, že soubor patří k provozu ‘{suggested}’, ale vybrán je ‘{self.outlet.currentText()}’.\nPřepnout na ‘{suggested}’?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes,
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.outlet.setCurrentText(suggested)
        days = self.adapter.available_days(p, month, year)
        self.picker.set_days(days)
        self.day_info.setText(f"Detekováno: Měsíc/Rok = {month:02d}/{year} | Dny: {', '.join(map(str, days)) if days else '—'}")
        self.append_status(f"Načten soubor: {p}")

    def pick_output_dir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Výstupní složka", self.out_dir.text())
        if d:
            self.out_dir.setText(d)
            # Save the new output directory to config
            self.cfg["output_dir"] = d
            save_config(self.cfg)
            self.append_status(f"Výstupní složka změněna na: {d}")

    def open_output(self):
        path = self.out_dir.text()
        try:
            os.startfile(path)  # Windows only
        except Exception:
            QtWidgets.QMessageBox.information(self, APP_NAME, f"Složku otevři ručně: {path}")

    def mark_weekends(self):
        if not self.month_year: return
        m, y = self.month_year
        self.picker.mark_weekends(m, y)

    def mark_workdays(self):
        if not self.month_year: return
        m, y = self.month_year
        self.picker.mark_workdays(m, y)

    def generate(self):
        # Always reload config to pick up edits (e.g., numberRequested) without restarting the app
        self.cfg = load_config()
        self.adapter = ExcelAdapter(self.cfg)

        if not self.xlsx_path or not self.month_year:
            QtWidgets.QMessageBox.warning(self, APP_NAME, "Nahraj nejprve Excel.")
            return
        sel = self.picker.selected_days()
        if not sel:
            QtWidgets.QMessageBox.information(self, APP_NAME, "Nevybral jsi žádné dny.")
            return
        outlet = self.outlet.currentText()
        write_log(f"DEBUG: Selected outlet: {outlet}")
        write_log(f"DEBUG: Available outlets in config: {list(self.cfg.get('outlets', {}).keys())}")
        outlet_cfg = self.cfg["outlets"][outlet]
        write_log(f"DEBUG: Outlet config loaded: {outlet_cfg.get('centre', 'MISSING')}")
        out_dir = Path(self.out_dir.text()); out_dir.mkdir(parents=True, exist_ok=True)

        # iterate days
        month, year = self.month_year
        success = 0; files: List[str] = []
        for d in sel:
            day = date(year, month, d)
            try:
                write_log(f"DEBUG: Processing day {day}")
                methods = self.adapter.read_day(self.xlsx_path, day)
                write_log(f"DEBUG: Methods found: {list(methods.keys())}")
                # CASH
                cash_amounts = methods.get("cash", {})
                write_log(f"DEBUG: Cash amounts: {cash_amounts}")
                if any(cash_amounts.get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
                    tree = datapack_with(build_voucher(cash_amounts, day, outlet_cfg, outlet_name=outlet), day, outlet, doc_type="voucher")
                    fname = format_filename("pokladna", day, outlet)
                    fpath = out_dir / fname
                    tree.write(str(fpath), encoding=DEFAULT_CONFIG["global_rules"]["encoding"], xml_declaration=True)
                    files.append(fname); success += 1
                # CARD
                card_amounts = methods.get("card", {})
                if any(card_amounts.get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
                    # compute Celkem for note (total gross) and keep outlet Text mapping
                    total = (card_amounts.get("base_high",0)+card_amounts.get("vat_high",0)+
                             card_amounts.get("base_low",0)+card_amounts.get("vat_low",0)+
                             card_amounts.get("base_none",0)+card_amounts.get("vat_none",0))
                    # For invoices, note format is: "Uživatelský export, Datum = DD.MM.YYYY, Text = method"
                    base_note = f"Uživatelský export, Datum = {day.strftime('%d.%m.%Y')}"
                    note_override = f"{base_note}, Text = kartou"
                    tree = datapack_with(build_invoice("card", card_amounts, day, outlet_cfg), day, outlet, doc_type="invoice_card", note_override=note_override)
                    fname = format_filename("ostatni", day, outlet, method_label="kartou")
                    fpath = out_dir / fname
                    tree.write(str(fpath), encoding=DEFAULT_CONFIG["global_rules"]["encoding"], xml_declaration=True)
                    files.append(fname); success += 1
                # VOUCHER
                voucher_amounts = methods.get("voucher", {})
                if any(voucher_amounts.get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
                    total = (voucher_amounts.get("base_high",0)+voucher_amounts.get("vat_high",0)+
                             voucher_amounts.get("base_low",0)+voucher_amounts.get("vat_low",0)+
                             voucher_amounts.get("base_none",0)+voucher_amounts.get("vat_none",0))
                    # For invoices, note format is: "Uživatelský export, Datum = DD.MM.YYYY, Text = method"
                    base_note = f"Uživatelský export, Datum = {day.strftime('%d.%m.%Y')}"
                    note_override = f"{base_note}, Text = voucher"
                    tree = datapack_with(build_invoice("voucher", voucher_amounts, day, outlet_cfg), day, outlet, doc_type="invoice_voucher", note_override=note_override)
                    fname = format_filename("ostatni", day, outlet, method_label="voucherem")
                    fpath = out_dir / fname
                    tree.write(str(fpath), encoding=DEFAULT_CONFIG["global_rules"]["encoding"], xml_declaration=True)
                    files.append(fname); success += 1
                # CASHLESS
                cashless_amounts = methods.get("cashless", {})
                if any(cashless_amounts.get(k, 0.0) for k in ["base_high","vat_high","base_low","vat_low","base_none","vat_none"]):
                    total = (cashless_amounts.get("base_high",0)+cashless_amounts.get("vat_high",0)+
                             cashless_amounts.get("base_low",0)+cashless_amounts.get("vat_low",0)+
                             cashless_amounts.get("base_none",0)+cashless_amounts.get("vat_none",0))
                    # For invoices, note format is: "Uživatelský export, Datum = DD.MM.YYYY, Text = method"
                    base_note = f"Uživatelský export, Datum = {day.strftime('%d.%m.%Y')}"
                    note_override = f"{base_note}, Text = cashless"
                    tree = datapack_with(build_invoice("cashless", cashless_amounts, day, outlet_cfg), day, outlet, doc_type="invoice_cashless", note_override=note_override)
                    fname = format_filename("ostatni", day, outlet, method_label="cashless")
                    fpath = out_dir / fname
                    tree.write(str(fpath), encoding=DEFAULT_CONFIG["global_rules"]["encoding"], xml_declaration=True)
                    files.append(fname); success += 1

                self.append_status(f"{day.strftime('%d.%m.%Y')}: vytvořeno {len(files)} soubor(ů) zatím…")
            except Exception as ex:
                tb = traceback.format_exc()
                self.append_status(f"Chyba pro {day}: {ex}")
                write_log(tb)

        if success:
            self.append_status(f"Hotovo. Vytvořeno {success} souborů. Poslední: {files[-1] if files else ''}")
            QtWidgets.QMessageBox.information(self, APP_NAME, f"Hotovo. Vytvořeno {success} souborů.")
        else:
            self.append_status("Nic nebylo vygenerováno (součty nulové nebo nebyly vybrány dny).")
            QtWidgets.QMessageBox.information(self, APP_NAME, "Nebyl vygenerován žádný soubor.")

 # --------------------------------------------------------------------------------------
 # Entry
 # --------------------------------------------------------------------------------------

def main():
    ensure_dirs()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()