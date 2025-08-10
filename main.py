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

def get_modern_stylesheet() -> str:
    """Return complete modern stylesheet for the application"""
    return f"""
    /* Main Application Window */
    QMainWindow {{
        background-color: {COLORS['background']};
        font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
        font-size: 10pt;
        color: {COLORS['text_primary']};
    }}
    
    /* Cards and Panels */
    QFrame {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
    }}
    
    /* Dropzone Frame - Special styling */
    DropFrame {{
        background-color: {COLORS['dropzone_bg']};
        border: 2px dashed {COLORS['dropzone_border']};
        border-radius: 16px;
        min-height: 120px;
        padding: 24px;
        margin: 12px;
        font-size: 11pt;
        color: {COLORS['text_secondary']};
    }}
    
    DropFrame:hover {{
        background-color: {COLORS['dropzone_hover']};
        border-color: {COLORS['primary_green']};
        color: {COLORS['primary_green']};
    }}
    
    /* Modern Buttons */
    QPushButton {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 500;
        font-size: 9pt;
        color: {COLORS['text_primary']};
        min-height: 16px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['primary_green_light']};
        border-color: {COLORS['primary_green']};
        color: {COLORS['primary_green_dark']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['primary_green']};
        color: white;
        border-color: {COLORS['primary_green_dark']};
    }}
    
    /* Primary Action Button */
    QPushButton#primary {{
        background-color: {COLORS['primary_green']};
        color: white;
        border: none;
        font-weight: 600;
        font-size: 11pt;
        padding: 12px 24px;
        min-height: 20px;
    }}
    
    QPushButton#primary:hover {{
        background-color: {COLORS['primary_green_hover']};
    }}
    
    QPushButton#primary:pressed {{
        background-color: {COLORS['primary_green_dark']};
    }}
    
    /* Dropdown ComboBox */
    QComboBox {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 10pt;
        color: {COLORS['text_primary']};
        min-height: 16px;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['primary_green']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid {COLORS['text_secondary']};
        margin-right: 8px;
    }}
    
    /* Input Fields */
    QLineEdit {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 10pt;
        color: {COLORS['text_primary']};
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['primary_green']};
        outline: none;
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: 10pt;
        font-weight: 500;
    }}
    
    QLabel#header {{
        font-size: 14pt;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin-bottom: 8px;
    }}
    
    QLabel#subtitle {{
        color: {COLORS['text_secondary']};
        font-size: 9pt;
        font-weight: 400;
    }}
    
    /* Checkboxes */
    QCheckBox {{
        color: {COLORS['text_primary']};
        font-size: 10pt;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['border']};
        border-radius: 4px;
        background-color: {COLORS['card_bg']};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['primary_green']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary_green']};
        border-color: {COLORS['primary_green']};
        image: none;
    }}
    
    QCheckBox::indicator:checked:hover {{
        background-color: {COLORS['primary_green_hover']};
    }}
    
    /* Text Areas */
    QTextEdit {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 12px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 9pt;
        color: {COLORS['text_primary']};
        line-height: 1.4;
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {COLORS['background']};
        width: 8px;
        border-radius: 4px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_hover']};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_muted']};
    }}
    
    /* Status Messages */
    QLabel#status_success {{
        color: {COLORS['success']};
        font-weight: 600;
    }}
    
    QLabel#status_error {{
        color: {COLORS['error']};
        font-weight: 600;
    }}
    
    QLabel#status_warning {{
        color: {COLORS['warning']};
        font-weight: 600;
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
        "voucher": {"ids": "Šekem",      "paymentType": "cheque"}
    },
    "outlets": {
        # Bistro
        "Bistro": {
            "centre": "3", "cashAccount_ids": "Bistro",
            "voucher_header_text": "Tržby hotově Molo Bistro",
            "accounts": {
                "inv": {"high": "315000/602116", "low": "315000/602114", "none": "315000/602117"},
                "vch": {"high": "211000/602116", "low": "211000/602114", "none": "211000/602117"}
            },
            "item_texts": {
                "cash":    {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":    {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher": {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"}
            }
        },
        # Restaurant
        "Restaurant": {
            "centre": "1", "cashAccount_ids": "MOLO",
            "accounts": {
                "inv": {"high": "315000/602112", "low": "315000/602110", "none": "315000/602113"},
                "vch": {"high": "211000/602112", "low": "211000/602110", "none": "211000/602113"}
            },
            "item_texts": {
                "cash":    {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":    {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher": {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"}
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
                "card": "Tržby Café du Lac - kartou"
            },
            "item_texts": {
                "cash":    {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":    {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher": {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"}
            }
        },
        # B&G
        "B&G": {
            "centre": "1", "cashAccount_ids": "BaG",
            "accounts": {
                "inv": {"high": "315000/602112", "low": "315000/602110", "none": "315000/602113"},
                "vch": {"high": "211000/602112", "low": "211000/602110", "none": "211000/602113"}
            },
            "item_texts": {
                "cash":    {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card":    {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"},
                "voucher": {"high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem"}
            }
        },
        # Molo2
        "Molo2": {
            "centre": "2", "cashAccount_ids": "MOLO",
            "accounts": {
                "inv": {"high": "315000/602112", "low": "315000/602110", "none": "315000/602113"},
                "vch": {"high": "211000/602112", "low": "211000/602110", "none": "211000/602113"}
            },
            "item_texts": {
                "cash": {"high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově"},
                "card": {"high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou"}
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
        methods = {"cash": {}, "card": {}, "voucher": {}}
        for method_key in ["cash", "card", "voucher"]:
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

    # number + symVar always present
    nr = outlet_cfg.get(f"invoice_numberRequested_{method}") or outlet_cfg.get("invoice_numberRequested")
    if not nr:
        nr = f"{day:%y%m%d}{datetime.now():%H%M%S}"
    num = E("number", ns="inv"); num.append(E("numberRequested", nr, "typ")); hdr.append(num)
    hdr.append(E("symVar", nr, "inv"))

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
    else:
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
    
    # If no custom number configured, generate default pattern
    if not nr:
        now = datetime.now()
        prefix = outlet_cfg.get("cashAccount_ids", "UNK")
        nr = f"{prefix}P{now:%H%M%S}"
    
    # ALWAYS add number element (required by Pohoda XML schema)
    num = E("number", ns="vch")
    num.append(E("numberRequested", nr, "typ"))
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
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setStyleSheet("QFrame { border: 2px dashed #888; border-radius: 12px; }")
        self.label = QtWidgets.QLabel("⇩  Přetáhni soubor sem  ⇩", alignment=QtCore.Qt.AlignCenter)
        lay = QtWidgets.QVBoxLayout(self); lay.addWidget(self.label)

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
        
        # Apply modern styling
        self.setStyleSheet(get_modern_stylesheet())
        
        self.cfg = load_config()
        self.adapter = ExcelAdapter(self.cfg)
        self.xlsx_path: Optional[Path] = None
        self.month_year: Optional[Tuple[int,int]] = None

        # Top controls
        outlet_lbl = QtWidgets.QLabel("Vyberte provoz:")
        outlet_lbl.setObjectName("header")
        self.outlet = QtWidgets.QComboBox(); self.outlet.addItems(["Bistro","Restaurant","CDL","B&G","Molo2"]) 

        self.drop = DropFrame(); self.drop.fileDropped.connect(self.on_file_dropped)
        pick_btn = QtWidgets.QPushButton("Vybrat soubor…"); pick_btn.clicked.connect(self.pick_file)

        # Day controls
        self.day_info = QtWidgets.QLabel("Detekováno: —")
        self.picker = DayPicker()
        btn_all = QtWidgets.QPushButton("Vše"); btn_all.clicked.connect(lambda: self.picker.mark_all(True))
        btn_weekend = QtWidgets.QPushButton("Víkendy"); btn_weekend.clicked.connect(self.mark_weekends)
        btn_work = QtWidgets.QPushButton("Prac. dny"); btn_work.clicked.connect(self.mark_workdays)
        btn_clear = QtWidgets.QPushButton("Clear"); btn_clear.clicked.connect(lambda: self.picker.mark_all(False))

        # Output
        self.out_dir = QtWidgets.QLineEdit(str(OUTPUT_DIR));
        out_btn = QtWidgets.QPushButton("Změnit…"); out_btn.clicked.connect(self.pick_output_dir)
        gen_btn = QtWidgets.QPushButton("Generovat XML"); gen_btn.clicked.connect(self.generate)
        gen_btn.setObjectName("primary")  # Apply primary styling
        open_btn = QtWidgets.QPushButton("Otevřít složku"); open_btn.clicked.connect(self.open_output)

        # Status / log
        self.status = QtWidgets.QTextEdit(); self.status.setReadOnly(True)

        # Layout
        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)
        top = QtWidgets.QHBoxLayout(); top.addWidget(outlet_lbl); top.addWidget(self.outlet); top.addStretch(); v.addLayout(top)
        v.addWidget(self.drop)
        v.addWidget(pick_btn)
        v.addWidget(self.day_info)
        # picker panel
        hp = QtWidgets.QHBoxLayout(); hp.addWidget(self.picker); side = QtWidgets.QVBoxLayout();
        side.addWidget(btn_all); side.addWidget(btn_weekend); side.addWidget(btn_work); side.addWidget(btn_clear); side.addStretch(); hp.addLayout(side)
        v.addLayout(hp)
        # output row
        orow = QtWidgets.QHBoxLayout(); orow.addWidget(QtWidgets.QLabel("Výstup:")); orow.addWidget(self.out_dir); orow.addWidget(out_btn); v.addLayout(orow)
        # actions
        ab = QtWidgets.QHBoxLayout(); ab.addWidget(gen_btn); ab.addStretch(); ab.addWidget(open_btn); v.addLayout(ab)
        status_lbl = QtWidgets.QLabel("Stav zpracování:")
        status_lbl.setObjectName("header")
        v.addWidget(status_lbl)
        v.addWidget(self.status)

        # Apply modern effects to interactive elements
        ModernEffects.add_hover_effect(gen_btn)
        ModernEffects.add_click_effect(gen_btn)
        ModernEffects.add_hover_effect(pick_btn)
        ModernEffects.add_hover_effect(out_btn)
        ModernEffects.add_hover_effect(open_btn)
        ModernEffects.add_hover_effect(btn_all)
        ModernEffects.add_hover_effect(btn_weekend)
        ModernEffects.add_hover_effect(btn_work)
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