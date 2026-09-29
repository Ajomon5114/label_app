import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import io
import copy
import xml.etree.ElementTree as ET
import tempfile
import sys
import threading
import sqlite3
import json
from datetime import datetime
import calendar
import re

# ── Ensure sharp DPI scaling on Windows (Fix for PyInstaller EXEs) ──
if sys.platform.startswith("win"):
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# ── Patch reportlab config to bypass Cairo ──
import reportlab.rl_config as rl_config

rl_config.renderPMBackend = "invalid_so_it_fails_gracefully"

import pymupdf
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# ── CustomTkinter Appearance ──────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    ASSET_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = BASE_DIR

import json

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
NETWORK_DIR = BASE_DIR
FTP_HOST = ""
FTP_USER = ""
FTP_PASS = ""
FTP_UPLOAD_DIR = "/public_html/assets/docs/"
FTP_PUBLIC_URL = "https://www.biomedingredients.com/assets/docs/"
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
            if "network_dir" in cfg and cfg["network_dir"]:
                NETWORK_DIR = cfg["network_dir"]
            if "ftp_host" in cfg:
                FTP_HOST = cfg["ftp_host"]
            if "ftp_user" in cfg:
                FTP_USER = cfg["ftp_user"]
            if "ftp_pass" in cfg:
                FTP_PASS = cfg["ftp_pass"]
            if "ftp_upload_dir" in cfg:
                FTP_UPLOAD_DIR = cfg["ftp_upload_dir"]
            if "ftp_public_url" in cfg:
                FTP_PUBLIC_URL = cfg["ftp_public_url"]
    except:
        pass


LABELS_DIR = os.path.join(NETWORK_DIR, "labels")
DB_PATH = os.path.join(NETWORK_DIR, "label_history.db")
MONTHLY_DATA_DIR = os.path.join(NETWORK_DIR, "Monthly Data")

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

TEMPLATE_CONFIGS_DEFAULT = {
    "Label 1 FSSAI.svg": {
        "preview_scale": 1.0,
        "fields": {
            "product": (103, 72, 10),
            "batch": (103, 88.2, 8),
            "fssai": (103, 105.1, 8),
            "mfg_date": (103, 121.5, 8),
            "exp_date": (239.5, 121.5, 8),
            "net_wt": (146, 137.7, 8),
            "gross_wt": (254, 137.7, 8),
            "drum": (265, 162, 8),
            "drum_label_text": (235, 162, 8),
            "origin": (72, 160.5, 8),
        },
        "static_labels": [
            ("Product:", 38, 71.5, 8),
            ("Batch No:", 38, 88.2, 8),
            ("FSSAI No:", 38, 105.1, 8),
            ("Mfg. Date:", 38, 121.5, 8),
            ("Expiry Date:", 178, 121.5, 8),
            ("Net Wt:", 103, 137.7, 8),
            ("Gross Wt:", 205, 137.7, 8),
            ("Quantity:", 38, 137.7, 8),
            ("Origin:", 45, 160.5, 8),
            ("www.biomedingredients.com", 22, 177, 8),
        ],
        "form_sections": [
            (
                "PRODUCT INFORMATION",
                [
                    ("Product Name", "product"),
                    ("Batch No", "batch"),
                    ("FSSAI No", "fssai"),
                ],
            ),
            ("DATES", [("Mfg. Date", "mfg_date"), ("Expiry Date", "exp_date")]),
            (
                "WEIGHT & QUANTITY",
                [
                    ("Total Quantity (Kg)", "total_quantity"),
                    ("Drum Capacity (Kg)", "drum_capacity"),
                ],
            ),
            ("ORIGIN", [("Origin", "origin")]),
        ],
        "qr_options": {"x": 254, "y_offset": 55, "size": 45},
    },
    "Label 2 FSSAI & USFDA.svg": {
        "preview_scale": 1.0,
        "fields": {
            "product": (103, 72, 10),
            "batch": (103, 88.2, 8),
            "fssai": (103, 105.1, 8),
            "usfda": (243, 105.1, 8),
            "mfg_date": (103, 121.5, 8),
            "exp_date": (239.5, 121.5, 8),
            "net_wt": (146, 137.7, 8),
            "gross_wt": (254, 137.7, 8),
            "drum": (265, 162, 8),
            "drum_label_text": (235, 162, 8),
            "origin": (72, 160.5, 8),
        },
        "static_labels": [
            ("Product:", 38, 71.5, 8),
            ("Batch No:", 38, 88.2, 8),
            ("FSSAI No:", 38, 105.1, 8),
            ("USFDA", 201, 105.1, 8),
            ("Mfg. Date:", 38, 121.5, 8),
            ("Expiry Date:", 178, 121.5, 8),
            ("Net Wt:", 103, 137.7, 8),
            ("Gross Wt:", 205, 137.7, 8),
            ("Quantity:", 38, 137.7, 8),
            ("Origin:", 45, 160.5, 8),
            ("www.biomedingredients.com", 22, 177, 8),
        ],
        "form_sections": [
            (
                "PRODUCT INFORMATION",
                [
                    ("Product Name", "product"),
                    ("Batch No", "batch"),
                    ("FSSAI No", "fssai"),
                    ("USFDA No", "usfda"),
                ],
            ),
            ("DATES", [("Mfg. Date", "mfg_date"), ("Expiry Date", "exp_date")]),
            (
                "WEIGHT & QUANTITY",
                [
                    ("Total Quantity (Kg)", "total_quantity"),
                    ("Drum Capacity (Kg)", "drum_capacity"),
                ],
            ),
            ("ORIGIN", [("Origin", "origin")]),
        ],
        "qr_options": {"x": 254, "y_offset": 55, "size": 45},
    },
    "other labels.svg": {
        "preview_scale": 1.0,
        "fields": {
            "product": (108, 78, 12),
            "batch": (108, 104, 10),
            "fssai": (108, 131, 10),
            "usfda": (315, 131, 10),
            "mfg_date": (108, 157, 10),
            "exp_date": (326, 157, 10),
            "net_wt": (174, 184, 10),
            "gross_wt": (334, 184, 10),
            "drum": (348, 215, 10),
            "drum_label_text": (310, 215, 10),
            "customer_name": (211, 33, 16, "center"),
            # "origin": (85, 215, 10),
        },
        "static_labels": [
            ("Product:", 34, 77, 10),
            ("Batch No:", 34, 104, 10),
            ("FSSAI No:", 34, 131, 10),
            ("USFDA", 240, 131, 10),
            ("Mfg. Date:", 34, 157, 10),
            ("Expiry Date:", 220, 157, 10),
            ("Quantity:", 34, 184, 10),
            ("Net Wt:", 108, 184, 10),
            ("Gross Wt:", 260, 184, 10),
            # ("Origin:", 34, 215, 10),
        ],
        "form_sections": [
            (
                "PRODUCT INFORMATION",
                [
                    ("Product Name", "product"),
                    ("Batch No", "batch"),
                    ("FSSAI No", "fssai"),
                    ("USFDA No", "usfda"),
                ],
            ),
            ("DATES", [("Mfg. Date", "mfg_date"), ("Expiry Date", "exp_date")]),
            (
                "WEIGHT & QUANTITY",
                [
                    ("Total Quantity (Kg)", "total_quantity"),
                    ("Drum Capacity (Kg)", "drum_capacity"),
                ],
            ),
            # ("ORIGIN", [("Origin", "origin")]),
        ],
        "qr_options": {"x": 350, "y_offset": 55, "size": 43},
        "bg_color": "#FFFFFF",
        "logo_options": {
            "hide": True,
            "x": 28,
            "y_offset": 52,
            "w": 40,
            "h": 36,
            "draw_bg": False,
        },
    },
}

import json
import copy

TEMPLATE_CONFIGS = copy.deepcopy(TEMPLATE_CONFIGS_DEFAULT)

TARE_WEIGHTS = {"Plastic Drum": 3.0, "Paper Drum": 4.0, "Custom Weight": 0.0}
DRUM_CAPACITY = 25.0
TEXT_FILL = "#1a1a1a"
FONT_FAMILY = "Arial, Helvetica, sans-serif"


def list_svg_templates():
    if not os.path.isdir(LABELS_DIR):
        return []
    return sorted(f for f in os.listdir(LABELS_DIR) if f.lower().endswith(".svg"))


def load_svg_text(filename):
    path = os.path.join(LABELS_DIR, filename)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def draw_native_labels(c, config, values, x_offset, y_offset, label_h, scale):
    static_color = config.get("static_text_color", TEXT_FILL)
    c.setFillColor(HexColor(static_color))
    for static_data in config["static_labels"]:
        label_text, svg_x, svg_y, fs = static_data[:4]
        c.setFont("Helvetica-Bold", fs * scale)
        text_x = x_offset + (svg_x * scale)
        text_y = y_offset + label_h - (svg_y * scale) - (fs * scale * 0.3)
        c.drawString(text_x, text_y, label_text)

    dynamic_color = config.get("dynamic_text_color", TEXT_FILL)
    c.setFillColor(HexColor(dynamic_color))
    for key, field_data in config["fields"].items():
        svg_x, svg_y, fs = field_data[:3]
        align = field_data[3] if len(field_data) > 3 else "left"
        text = values.get(key, "")
        if not text:
            continue
        c.setFont("Helvetica-Bold", fs * scale)
        text_x = x_offset + (svg_x * scale)

        if key == "product":
            # Custom vertical alignment for the product field
            text_y = y_offset + label_h - (svg_y * scale) - (fs * scale * 0.25)
        else:
            text_y = y_offset + label_h - (svg_y * scale) - (fs * scale * 0.3)

        if align == "center":
            c.drawCentredString(text_x, text_y, str(text))
        else:
            c.drawString(text_x, text_y, str(text))


def draw_qr_code(
    c, values, label_w, label_h, scale, qr_options, x_offset=0, y_offset=0
):
    try:
        import qrcode
        from reportlab.lib.utils import ImageReader
        from io import BytesIO

        import base64
        import json

        # Filter out empty values and unwanted keys
        unwanted_keys = {
            "net_wt",
            "gross_wt",
            "drum_capacity",
            "drum",
            "drum_label_text",
            "custom_tare",
            "last_drum_label_text",
        }
        clean_values = {
            k: v
            for k, v in values.items()
            if v and str(v).strip() and k not in unwanted_keys
        }
        if not clean_values:
            return

        json_str = json.dumps(clean_values)
        b64_data = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")

        # This is the URL where the qr_viewer.html will be hosted.
        # You will need to upload qr_viewer.html to your website!
        base_url = "https://www.biomedingredients.com/qr_viewer.html"
        qr_text = f"{base_url}?d={b64_data}"

        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        qr_reader = ImageReader(buf)

        qr_size = qr_options.get("size", 45) * scale
        qr_x = x_offset + (qr_options.get("x", 355) * scale)
        qr_y = y_offset + label_h - (qr_options.get("y_offset", 52) * scale)

        c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)
    except Exception as e:
        print("QR Code Error:", e)


def calculate_drums(total_qty_str, drum_type, drum_cap_str="25", custom_tare_str="0.0"):
    try:
        total = float(total_qty_str)
    except:
        total = 0.0

    try:
        capacity = float(drum_cap_str)
        if capacity <= 0:
            capacity = 25.0
    except:
        capacity = 25.0

    if drum_type == "Custom Weight":
        try:
            tare = float(custom_tare_str)
        except:
            tare = 0.0
    elif drum_type in ["Plastic Drum", "Paper Drum"]:
        tare = TARE_WEIGHTS.get(drum_type, 0.0)
    else:
        tare = None

    drums = []
    while total > 0:
        if total >= capacity:
            net = capacity
            total -= capacity
        else:
            net = total
            total = 0

        if tare is None:
            gross = 0.0
        else:
            gross = net + tare

        drums.append({"net": net, "gross": gross})

    if not drums:
        drums.append({"net": 0.0, "gross": 0.0 if tare is None else tare})
    return drums


def export_pdf(svg_filename: str, labels_values: list, out_path: str):
    from reportlab.lib.units import mm as mm_unit
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    raw_svg = load_svg_text(svg_filename)
    root = ET.fromstring(raw_svg)
    for g in root.findall(f".//{{{SVG_NS}}}g[@id='text-overlay']"):
        root.remove(g)
    clean_svg = ET.tostring(root, encoding="unicode", xml_declaration=False)
    if not clean_svg.startswith("<svg") and "<svg" in clean_svg:
        clean_svg = clean_svg[clean_svg.index("<svg") :]

    tmp_svg = tempfile.mktemp(suffix=".svg")
    with open(tmp_svg, "w", encoding="utf-8") as fh:
        fh.write(clean_svg)

    try:
        base_drawing = svg2rlg(tmp_svg)
        if base_drawing is None:
            raise RuntimeError("svg2rlg returned None — SVG may be malformed.")
    finally:
        if os.path.exists(tmp_svg):
            os.remove(tmp_svg)

    c = canvas.Canvas(out_path, pagesize=A4)
    margin = 10 * mm_unit
    page_w, page_h = A4
    avail_w = page_w - 2 * margin
    spacing = 0 * mm_unit
    avail_h = (page_h - 2 * margin - 2 * spacing) / 3

    logo_path = os.path.join(LABELS_DIR, "BMI Logo.png")
    has_logo = os.path.exists(logo_path)
    config = TEMPLATE_CONFIGS.get(svg_filename, list(TEMPLATE_CONFIGS.values())[0])

    scale_w = avail_w / base_drawing.width
    scale_h = avail_h / base_drawing.height
    scale = min(scale_w, scale_h)
    label_w = base_drawing.width * scale
    label_h = base_drawing.height * scale

    for i, values in enumerate(labels_values):
        drawing = copy.deepcopy(base_drawing)
        drawing.width = label_w
        drawing.height = label_h
        drawing.transform = (scale, 0, 0, scale, 0, 0)

        x = (page_w - label_w) / 2
        total_content_h = 3 * label_h + 2 * spacing
        start_y = (page_h + total_content_h) / 2 - label_h
        pos_index = i % 3
        y = start_y - pos_index * (label_h + spacing)

        bg_color_hex = config.get("bg_color", "#FFFFFF")
        c.setFillColor(HexColor(bg_color_hex))
        c.rect(x, y, label_w, label_h, fill=1, stroke=0)

        renderPDF.draw(drawing, c, x, y)
        draw_native_labels(c, config, values, x, y, label_h, scale)

        logo_options = config.get("logo_options", {})
        if has_logo and not logo_options.get("hide", False):
            logo_x = x + (logo_options.get("x", 18) * scale)
            logo_y = y + label_h - (logo_options.get("y_offset", 52) * scale)
            logo_w = logo_options.get("w", 45) * scale
            logo_h = logo_options.get("h", 40) * scale

            if logo_options.get("draw_bg", True):
                c.setFillColorRGB(1, 1, 1)
                bg_x = x + (logo_options.get("bg_x", 10) * scale)
                bg_y = logo_y - (logo_options.get("bg_y_offset", 2) * scale)
                bg_w = logo_options.get("bg_w", 48) * scale
                bg_h = logo_options.get("bg_h", 45) * scale
                c.rect(bg_x, bg_y, bg_w, bg_h, fill=1, stroke=0)

            c.drawImage(
                logo_path, logo_x, logo_y, width=logo_w, height=logo_h, mask="auto"
            )

        draw_qr_code(
            c,
            values,
            label_w,
            label_h,
            scale,
            config.get("qr_options", {}),
            x_offset=x,
            y_offset=y,
        )

        if pos_index == 2 and i != len(labels_values) - 1:
            c.showPage()
    c.save()


class DatePickerDialog(ctk.CTkToplevel):
    def __init__(self, master, current_date_str, callback, title="Select Date"):
        super().__init__(master)
        self.title(title)
        self.geometry("340x380")
        self.resizable(False, False)
        self.callback = callback
        self.transient(master)
        self.grab_set()

        self.update_idletasks()
        try:
            mx = master.winfo_rootx()
            my = master.winfo_rooty()
            mw = master.winfo_width()
            mh = master.winfo_height()
            x = mx + max(0, (mw - 340) // 2)
            y = my + max(0, (mh - 380) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        now = datetime.now()
        self.sel_year, self.sel_month, self.sel_day = now.year, now.month, now.day
        for fmt in (
            "%d-%b-%Y",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d %b %Y",
        ):
            try:
                dt = datetime.strptime(str(current_date_str).strip(), fmt)
                self.sel_year, self.sel_month, self.sel_day = dt.year, dt.month, dt.day
                break
            except Exception:
                pass

        self.view_year = self.sel_year
        self.view_month = self.sel_month
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(12, 6))

        nav_font = ctk.CTkFont(size=12, weight="bold")
        ctk.CTkButton(
            header,
            text="<<",
            width=32,
            height=28,
            font=nav_font,
            fg_color="#2B2B2B",
            text_color="#E0E0E0",
            hover_color="#E5E7EB",
            command=lambda: self._shift_year(-1),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            header,
            text="<",
            width=32,
            height=28,
            font=nav_font,
            fg_color="#2B2B2B",
            text_color="#E0E0E0",
            hover_color="#E5E7EB",
            command=lambda: self._shift_month(-1),
        ).pack(side="left", padx=2)

        self.title_lbl = ctk.CTkLabel(
            header, font=ctk.CTkFont(size=14, weight="bold"), text_color="#E0E0E0"
        )
        self.title_lbl.pack(side="left", expand=True)

        ctk.CTkButton(
            header,
            text=">",
            width=32,
            height=28,
            font=nav_font,
            fg_color="#2B2B2B",
            text_color="#E0E0E0",
            hover_color="#E5E7EB",
            command=lambda: self._shift_month(1),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            header,
            text=">>",
            width=32,
            height=28,
            font=nav_font,
            fg_color="#2B2B2B",
            text_color="#E0E0E0",
            hover_color="#E5E7EB",
            command=lambda: self._shift_year(1),
        ).pack(side="left", padx=2)

        week_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=6)
        week_frame.pack(fill="x", padx=12, pady=4)
        for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ctk.CTkLabel(
                week_frame,
                text=d,
                width=42,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#4B5563",
            ).grid(row=0, column=i, padx=1, pady=3)

        self.cal_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cal_frame.pack(fill="both", expand=True, padx=12, pady=2)
        self._render_days()

        sc_frame = ctk.CTkFrame(self, fg_color="transparent")
        sc_frame.pack(fill="x", padx=12, pady=(6, 12))

        btn_f = ctk.CTkFont(size=11, weight="bold")
        ctk.CTkButton(
            sc_frame,
            text="Today",
            width=62,
            height=28,
            font=btn_f,
            fg_color="#EFF6FF",
            text_color="#60A5FA",
            hover_color="#DBEAFE",
            command=self._set_today,
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            sc_frame,
            text="+1 Y",
            width=46,
            height=28,
            font=btn_f,
            fg_color="#2B2B2B",
            text_color="#CCCCCC",
            hover_color="#E5E7EB",
            command=lambda: self._add_years(1),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            sc_frame,
            text="+2 Y",
            width=46,
            height=28,
            font=btn_f,
            fg_color="#2B2B2B",
            text_color="#CCCCCC",
            hover_color="#E5E7EB",
            command=lambda: self._add_years(2),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            sc_frame,
            text="+3 Y",
            width=46,
            height=28,
            font=btn_f,
            fg_color="#2B2B2B",
            text_color="#CCCCCC",
            hover_color="#E5E7EB",
            command=lambda: self._add_years(3),
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            sc_frame,
            text="Close",
            width=56,
            height=28,
            font=btn_f,
            fg_color="transparent",
            text_color="#888888",
            hover_color="#FEE2E2",
            command=self.destroy,
        ).pack(side="right", padx=2)

    def _render_days(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()

        month_name = calendar.month_name[self.view_month]
        self.title_lbl.configure(text=f"{month_name} {self.view_year}")

        month_cal = calendar.monthcalendar(self.view_year, self.view_month)
        for r, week in enumerate(month_cal):
            for c, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(self.cal_frame, text="", width=42, height=30).grid(
                        row=r, column=c, padx=1, pady=1
                    )
                else:
                    is_selected = (
                        day == self.sel_day
                        and self.view_month == self.sel_month
                        and self.view_year == self.sel_year
                    )
                    btn = ctk.CTkButton(
                        self.cal_frame,
                        text=str(day),
                        width=42,
                        height=30,
                        corner_radius=6,
                        font=ctk.CTkFont(
                            size=12, weight="bold" if is_selected else "normal"
                        ),
                        fg_color="#2563EB" if is_selected else "#FFFFFF",
                        text_color="#FFFFFF" if is_selected else "#E0E0E0",
                        hover_color="#1D4ED8" if is_selected else "#E5E7EB",
                        command=lambda d=day: self._select_day(d),
                    )
                    btn.grid(row=r, column=c, padx=1, pady=1)

    def _shift_month(self, delta):
        self.view_month += delta
        if self.view_month > 12:
            self.view_month = 1
            self.view_year += 1
        elif self.view_month < 1:
            self.view_month = 12
            self.view_year -= 1
        self._render_days()

    def _shift_year(self, delta):
        self.view_year += delta
        self._render_days()

    def _select_day(self, day):
        dt = datetime(self.view_year, self.view_month, day)
        self.callback(dt.strftime("%d-%b-%Y"))
        self.destroy()

    def _set_today(self):
        now = datetime.now()
        self.callback(now.strftime("%d-%b-%Y"))
        self.destroy()

    def _add_years(self, num_years):
        try:
            target_year = self.sel_year + num_years
            dt = datetime(target_year, self.sel_month, self.sel_day)
        except ValueError:
            dt = datetime(target_year, self.sel_month, 28)
        self.callback(dt.strftime("%d-%b-%Y"))
        self.destroy()


class LabelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("")
        
        # Responsive sizing: 85% of screen width/height, ensuring it fits perfectly on any display/scaling
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        app_w = int(screen_w * 0.85)
        app_h = int(screen_h * 0.85)
        
        # Keep minimum sizes so UI elements don't get squashed
        self.minsize(900, 600)
        self.geometry(f"{app_w}x{app_h}")

        # ─── APP ICON LOGIC ───
        ico_path = os.path.join(ASSET_DIR, "app_icon_logo.ico")
        try:
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception as e:
            print(f"Failed to load app icon: {e}")
        # ──────────────────────

        self._templates = list_svg_templates()
        if not self._templates:
            if not os.path.exists(LABELS_DIR):
                os.makedirs(LABELS_DIR)
            messagebox.showerror(
                "No Templates Found",
                f"No SVG files found in:\n{LABELS_DIR}\n\nA 'labels' folder has been created for you. Please add .svg template files inside it and restart the app.",
            )
            self.destroy()
            sys.exit(0)

        self._selected_tpl = ctk.StringVar(value=self._templates[0])
        self.vars = {
            "customer_name": ctk.StringVar(value=""),
            "product": ctk.StringVar(value=""),
            "batch": ctk.StringVar(value=""),
            "fssai": ctk.StringVar(value="10622999000028"),
            "usfda": ctk.StringVar(value="12099156850"),
            "mfg_date": ctk.StringVar(value=""),
            "exp_date": ctk.StringVar(value=""),
            "total_quantity": ctk.StringVar(value=""),
            "drum_capacity": ctk.StringVar(value=""),
            "drum_type": ctk.StringVar(value="Packaging Item"),
            "custom_tare": ctk.StringVar(value=""),
            "origin": ctk.StringVar(value=""),
            "last_gross_wt": ctk.StringVar(value=""),
            "last_drum_label_text": ctk.StringVar(value=""),
            "coa_url": ctk.StringVar(value=""),
            "spec_url": ctk.StringVar(value=""),
        }

        self._render_after_id = None
        self._resize_after_id = None
        self._is_rendering = False

        for v in self.vars.values():
            v.trace_add("write", self._on_change_debounced)

        self._init_db()
        self._build_ui()
        self._on_change_debounced()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color="#181818")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        long_logo_path = os.path.join(ASSET_DIR, "app_logo.png")
        if os.path.exists(long_logo_path):
            try:
                # Load the logo and crop empty transparent space so it can be larger
                img_obj = Image.open(long_logo_path).convert("RGBA")
                bbox = img_obj.getbbox()
                if bbox:
                    img_obj = img_obj.crop(bbox)

                # Calculate height maintaining aspect ratio
                aspect = img_obj.height / img_obj.width
                img_w = 160
                img_h = int(img_w * aspect)
                self.long_logo_ctk = ctk.CTkImage(
                    light_image=img_obj, dark_image=img_obj, size=(img_w, img_h)
                )

                header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=(20, 30))

                logo_lbl = ctk.CTkLabel(header_frame, text="", image=self.long_logo_ctk)
                logo_lbl.pack(anchor="w")
            except Exception as e:
                print(f"Failed to load app_logo: {e}")
                header_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
                header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=(20, 30))
                ctk.CTkLabel(
                    header_frame,
                    text=f"LOGO ERR:\n{e}",
                    text_color="red",
                    font=header_font,
                ).pack(side="left", padx=(0, 5))
        else:
            header_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
            header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(20, 30))
            ctk.CTkLabel(
                header_frame, text="BMI", text_color="#60A5FA", font=header_font
            ).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(header_frame, text="Labels", font=header_font).pack(
                side="left"
            )

        # SEARCH BAR
        search_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 30))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search products...",
            placeholder_text_color="#888888",
            height=38,
            fg_color="#333333",
            border_width=1,
            border_color="#444444",
            text_color="#ffffff",
            corner_radius=6,
            font=ctk.CTkFont(size=14),
        )
        self.search_entry.pack(fill="x")

        # ESSENTIAL SECTION
        ctk.CTkLabel(
            sidebar,
            text="Essential",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 10))

        # Navigation Accordion Container
        self.nav_scroll = ctk.CTkScrollableFrame(
            sidebar, fg_color="transparent", bg_color="transparent"
        )
        self.nav_scroll.pack(fill="both", expand=True, padx=5, pady=0)
        self.accordion_frames = []

        def create_accordion(title, populate_func):
            container = ctk.CTkFrame(self.nav_scroll, fg_color="transparent")
            container.pack(fill="x", pady=2)

            content_frame = ctk.CTkFrame(container, fg_color="#1a1a1a")

            def toggle():
                if content_frame.winfo_ismapped():
                    content_frame.pack_forget()
                    btn.configure(
                        text=title + "", fg_color="#c9c9c9", text_color="black"
                    )
                else:
                    # Close other accordions? (Optional, let's keep them independent for now)
                    btn.configure(
                        text=title + "", fg_color="#2563EB", text_color="white"
                    )
                    content_frame.pack(fill="x", padx=(15, 0), pady=(0, 5))
                    # Clear and populate
                    for w in content_frame.winfo_children():
                        w.destroy()
                    populate_func(content_frame)

            btn = ctk.CTkButton(
                container,
                text=title + "",
                anchor="w",
                fg_color="transparent",
                text_color="#AAAAAA",
                hover_color="#c9c9c9",
                height=38,
                corner_radius=6,
                font=ctk.CTkFont(size=14),
            )
            btn.pack(fill="x", padx=10)

            def on_enter(e, b=btn):
                if not content_frame.winfo_ismapped():
                    b.configure(text_color="black", fg_color="#c9c9c9")

            def on_leave(e, b=btn):
                if not content_frame.winfo_ismapped():
                    b.configure(text_color="#AAAAAA", fg_color="transparent")

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.bind("<ButtonRelease-1>", lambda e: toggle())
            if hasattr(btn, "_text_label") and btn._text_label:
                btn._text_label.bind("<Enter>", on_enter)
                btn._text_label.bind("<Leave>", on_leave)
                btn._text_label.bind("<ButtonRelease-1>", lambda e: toggle())

            self.accordion_frames.append(container)

        # Populate functions
        def pop_recent(frame):
            import sqlite3

            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute(
                    "SELECT id, data, saved_at FROM label_history ORDER BY saved_at DESC LIMIT 20"
                )
                rows = c.fetchall()
                if not rows:
                    ctk.CTkLabel(
                        frame,
                        text="No recent labels.",
                        text_color="#888",
                        font=ctk.CTkFont(size=12),
                    ).pack(pady=10)
                    return
                for row in rows:
                    import json

                    try:
                        data = json.loads(row[1])
                        prod_name = data.get("product", "Unknown Product")
                        cust = data.get("customer_name", "")
                        label_text = (
                            f"📄 {prod_name} - {cust}" if cust else f"📄 {prod_name}"
                        )
                        btn = ctk.CTkButton(
                            frame,
                            text=label_text,
                            anchor="w",
                            fg_color="transparent",
                            text_color="#DDDDDD",
                            hover_color="#333333",
                            height=28,
                            font=ctk.CTkFont(size=12),
                            command=lambda r=row: self._load_from_history(r[0]),
                        )
                        btn.pack(fill="x", pady=1)
                    except:
                        pass
            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", text_color="red").pack()

            ctk.CTkButton(
                frame,
                text="Show More...",
                anchor="center",
                fg_color="#333333",
                text_color="white",
                hover_color="#444444",
                height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                command=self.open_recent_window,
            ).pack(fill="x", pady=(5, 0))

        def pop_cust(frame):
            import sqlite3

            def _load_latest_for_customer(cust_name):
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        c = conn.cursor()
                        # First try to load from customer_bookmarks data
                        c.execute(
                            "SELECT data FROM customer_bookmarks WHERE customer_name=?",
                            (cust_name,),
                        )
                        cb_row = c.fetchone()
                        if cb_row and cb_row[0]:
                            import json

                            data = json.loads(cb_row[0])
                            for k, v in data.items():
                                if k in self.vars:
                                    self.vars[k].set(v)
                            if "template" in data and hasattr(self, "_selected_tpl"):
                                self._selected_tpl.set(data["template"])
                            self._build_form()
                            self._on_change_debounced()
                        else:
                            # Fallback to history
                            c.execute(
                                "SELECT id FROM label_history WHERE json_extract(data, '$.customer_name') = ? ORDER BY saved_at DESC LIMIT 1",
                                (cust_name,),
                            )
                            row = c.fetchone()
                            if row:
                                self._load_from_history(row[0])
                            else:
                                # Just set the customer name if nothing else exists
                                if "customer_name" in self.vars:
                                    self.vars["customer_name"].set(cust_name)
                                    self._build_form()
                                    self._on_change_debounced()
                except Exception as e:
                    print(f"Error loading latest for customer: {e}")

            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()

                c.execute(
                    "CREATE TABLE IF NOT EXISTS customer_bookmarks (customer_name TEXT PRIMARY KEY, data TEXT)"
                )
                try:
                    c.execute("ALTER TABLE customer_bookmarks ADD COLUMN data TEXT")
                except:
                    pass
                c.execute("SELECT customer_name FROM customer_bookmarks")
                bookmarked = {row[0] for row in c.fetchall()}

                c.execute(
                    "SELECT DISTINCT json_extract(data, '$.customer_name') FROM label_history ORDER BY 1 ASC"
                )
                raw_customers = [row[0] for row in c.fetchall()]
                unique_customers = []
                for rc in raw_customers:
                    cust_name = str(rc).strip() if rc else ""
                    if not cust_name:
                        cust_name = "Unknown"
                    if cust_name not in unique_customers:
                        unique_customers.append(cust_name)

                if not unique_customers:
                    ctk.CTkLabel(
                        frame,
                        text="No customers found.",
                        text_color="#888",
                        font=ctk.CTkFont(size=12),
                    ).pack(pady=10)
                    return

                unique_customers.sort(key=lambda x: x.lower())

                for cust in unique_customers:
                    btn = ctk.CTkButton(
                        frame,
                        text="🏢 " + str(cust),
                        anchor="w",
                        fg_color="transparent",
                        text_color="#DDDDDD",
                        hover_color="#333333",
                        height=28,
                        font=ctk.CTkFont(size=12),
                        command=lambda cu=cust: _load_latest_for_customer(cu),
                    )
                    btn.pack(fill="x", pady=1)
            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", text_color="red").pack()

            ctk.CTkButton(
                frame,
                text="Show More...",
                anchor="center",
                fg_color="#333333",
                text_color="white",
                hover_color="#444444",
                height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                command=self.open_customer_history_window,
            ).pack(fill="x", pady=(5, 0))

        def pop_batch(frame):
            import sqlite3

            def _load_latest_for_batch(batch_name):
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        c = conn.cursor()
                        c.execute(
                            "SELECT id FROM label_history WHERE json_extract(data, '$.batch') = ? ORDER BY saved_at DESC LIMIT 1",
                            (batch_name,),
                        )
                        row = c.fetchone()
                        if row:
                            self._load_from_history(row[0])
                except Exception as e:
                    print(f"Error loading latest for batch: {e}")

            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute(
                    "SELECT DISTINCT json_extract(data, '$.batch') FROM label_history ORDER BY 1 DESC LIMIT 20"
                )
                raw_batches = [row[0] for row in c.fetchall()]
                unique_batches = []
                for rb in raw_batches:
                    batch_name = str(rb).strip() if rb else ""
                    if not batch_name:
                        batch_name = "Unknown"
                    if batch_name not in unique_batches:
                        unique_batches.append(batch_name)

                if not unique_batches:
                    ctk.CTkLabel(
                        frame,
                        text="No batches found.",
                        text_color="#888",
                        font=ctk.CTkFont(size=12),
                    ).pack(pady=10)
                    return
                for batch in unique_batches:
                    btn = ctk.CTkButton(
                        frame,
                        text="📦 " + str(batch),
                        anchor="w",
                        fg_color="transparent",
                        text_color="#DDDDDD",
                        hover_color="#333333",
                        height=28,
                        font=ctk.CTkFont(size=12),
                        command=lambda b=batch: _load_latest_for_batch(b),
                    )
                    btn.pack(fill="x", pady=1)
            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", text_color="red").pack()

            ctk.CTkButton(
                frame,
                text="Show More...",
                anchor="center",
                fg_color="#333333",
                text_color="white",
                hover_color="#444444",
                height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                command=self.open_batch_history_window,
            ).pack(fill="x", pady=(5, 0))

        def pop_bookmark(frame):
            import sqlite3

            try:
                conn = sqlite3.connect(DB_PATH)
                rows = conn.execute(
                    "SELECT id, name, saved_at FROM label_bookmarks ORDER BY name ASC"
                ).fetchall()
                conn.close()
                if not rows:
                    ctk.CTkLabel(
                        frame,
                        text="No bookmarks saved.",
                        text_color="#888",
                        font=ctk.CTkFont(size=12),
                    ).pack(pady=10)
                    return
                for row in rows:
                    row_id, name, saved_at = row

                    row_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    row_frame.pack(fill="x", pady=1)

                    btn = ctk.CTkButton(
                        row_frame,
                        text="☆ " + name,
                        anchor="w",
                        fg_color="transparent",
                        text_color="#DDDDDD",
                        hover_color="#333333",
                        height=28,
                        font=ctk.CTkFont(size=12),
                        command=lambda r=row_id: self._load_bookmark(r),
                    )
                    btn.pack(side="left", fill="x", expand=True)

                    del_btn = ctk.CTkButton(
                        row_frame,
                        text="✕",
                        width=28,
                        height=28,
                        fg_color="transparent",
                        text_color="#ef4444",
                        hover_color="#333333",
                        command=lambda r=row_id: self._delete_bookmark(r, frame),
                    )
                    del_btn.pack(side="right")

            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", text_color="red").pack()

        create_accordion("🕒 Recent", pop_recent)
        create_accordion("😊 Customer", pop_cust)
        create_accordion("📚 Batch", pop_batch)
        create_accordion("☆ Bookmark", pop_bookmark)

        self.search_results_container = ctk.CTkFrame(
            self.nav_scroll, fg_color="transparent"
        )

        def on_search(*args):
            query = self.search_entry.get().strip().lower()
            if not query:
                self.search_results_container.pack_forget()
                for f in self.accordion_frames:
                    f.pack(fill="x", pady=2)
                return

            for f in self.accordion_frames:
                f.pack_forget()

            self.search_results_container.pack(fill="both", expand=True)
            for w in self.search_results_container.winfo_children():
                w.destroy()

            import sqlite3

            try:
                conn = sqlite3.connect(DB_PATH)
                rows = conn.execute(
                    "SELECT id, product, json_extract(data, '$.customer_name'), json_extract(data, '$.batch') FROM label_history WHERE lower(product) LIKE ? OR lower(data) LIKE ? ORDER BY saved_at DESC LIMIT 20",
                    (f"%{query}%", f"%{query}%"),
                ).fetchall()
                conn.close()

                if not rows:
                    ctk.CTkLabel(
                        self.search_results_container,
                        text="No matches found.",
                        text_color="#888",
                        font=ctk.CTkFont(size=12),
                    ).pack(pady=10)
                else:
                    for r_id, prod, cust, batch in rows:
                        parts = []
                        if prod and str(prod).strip():
                            parts.append(str(prod).strip())
                        if cust and str(cust).strip():
                            parts.append(str(cust).strip())
                        if batch and str(batch).strip():
                            parts.append(f"({str(batch).strip()})")

                        btn_text = "📄 " + " - ".join(parts) if parts else "📄 Unknown"
                        if len(btn_text) > 45:
                            btn_text = btn_text[:42] + "..."

                        btn = ctk.CTkButton(
                            self.search_results_container,
                            text=btn_text,
                            anchor="w",
                            fg_color="transparent",
                            text_color="#DDDDDD",
                            hover_color="#333333",
                            height=28,
                            font=ctk.CTkFont(size=12),
                            command=lambda rid=r_id: self._load_from_history(rid),
                        )
                        btn.pack(fill="x", pady=1)
            except Exception as e:
                print("Search error:", e)

        self.search_entry.bind("<KeyRelease>", on_search)

        # FOOTER
        footer_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=30)

        ctk.CTkLabel(
            footer_frame,
            text="Made in India",
            text_color="#888888",
            font=ctk.CTkFont(size=13),
            anchor="w",
        ).pack(fill="x")

        ctk.CTkButton(
            footer_frame,
            text="⚙️ Bio Med Ingredients Pvt. Ltd.",
            text_color="#AAAAAA",
            fg_color="transparent",
            hover_color="#2A2A2A",
            command=self.open_settings_window,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(5, 0))

        # Hidden variables to preserve application logic
        hidden_frame = ctk.CTkFrame(sidebar, width=0, height=0)
        self.history_month_var = ctk.StringVar(value="Current Month")
        self.history_month_combo = ctk.CTkOptionMenu(
            hidden_frame, variable=self.history_month_var, values=["Current Month"]
        )
        self.history_list_frame = ctk.CTkScrollableFrame(hidden_frame)
        self._refresh_history_panel()

        # 2. MAIN AREA
        main_area = ctk.CTkFrame(self, fg_color="#181818", corner_radius=0)
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.grid_rowconfigure(0, weight=1)
        main_area.grid_columnconfigure(0, weight=3, minsize=250)
        main_area.grid_columnconfigure(1, weight=0)  # Separator
        main_area.grid_columnconfigure(2, weight=6, minsize=350)

        # FORM PANE
        form_pane = ctk.CTkFrame(
            main_area,
            corner_radius=0,
            fg_color="#1A1A1A",
        )
        form_pane.grid(row=0, column=0, sticky="nsew")
        form_pane.grid_propagate(False)

        # Vertical Separator
        vertical_sep = ctk.CTkFrame(main_area, width=1, fg_color="#3a3a3a")
        vertical_sep.grid(row=0, column=1, sticky="ns", pady=10)
        # TEMPLATE TABS (MOCKUP STYLE)
        top_tabs_frame = ctk.CTkFrame(form_pane, fg_color="transparent")
        top_tabs_frame.pack(fill="x", padx=10, pady=(20, 15))

        self.tab_buttons = []
        tab_names = ["EU regulation", "US regulation", "Other"]

        def _select_tab_ui(idx, name):
            for i, b in enumerate(self.tab_buttons):
                b.configure(
                    fg_color="#3A3A3A" if i == idx else "#1E1E1E",
                    text_color="#ffffff" if i == idx else "#666666",
                    border_width=0,
                )
            if idx < len(self._templates):
                self._selected_tpl.set(self._templates[idx])
            else:
                self._selected_tpl.set(self._templates[0])
            self._on_template_change()

        for i, t_name in enumerate(tab_names):
            btn = ctk.CTkButton(
                top_tabs_frame,
                text=t_name,
                fg_color="#3A3A3A" if i == 0 else "#1E1E1E",
                text_color="#ffffff" if i == 0 else "#666666",
                hover_color="#444444",
                border_width=0,
                corner_radius=6,
                height=36,
                command=lambda x=i, t=t_name: _select_tab_ui(x, t),
            )
            btn.pack(side="left", padx=5, expand=True, fill="x")
            self.tab_buttons.append(btn)

        self.scroll_frame = ctk.CTkScrollableFrame(form_pane, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self._build_form()

        # PREVIEW PANE
        self.preview_pane = ctk.CTkFrame(main_area, corner_radius=0, fg_color="#181818")
        self.preview_pane.grid(row=0, column=2, sticky="nsew")
        self.preview_pane.grid_propagate(False)
        self.preview_pane.grid_columnconfigure(0, weight=1)
        self.preview_pane.grid_rowconfigure(1, weight=1)
        
        self.preview_pane.bind("<Configure>", self._on_preview_pane_resize)

        # Top Toolbar
        top_toolbar = ctk.CTkFrame(self.preview_pane, fg_color="transparent")
        top_toolbar.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        # Grid View Button (Export Dialog)
        self.grid_btn = ctk.CTkButton(
            top_toolbar,
            text="☷",
            width=36,
            height=36,
            corner_radius=6,
            border_width=1,
            border_color="#3a3a3a",
            fg_color="#2a2a2a",
            hover_color="#333333",
            text_color="#E0E0E0",
            font=ctk.CTkFont(size=18),
            command=self._open_export_menu,
        )
        self.grid_btn.pack(side="right")
        # Filter Button
        filter_btn = ctk.CTkButton(
            top_toolbar,
            text="⊶ Filter",
            command=self.open_filter_window,
            width=80,
            height=36,
            corner_radius=6,
            border_width=1,
            border_color="#3a3a3a",
            fg_color="#2a2a2a",
            hover_color="#333333",
            text_color="#E0E0E0",
            font=ctk.CTkFont(size=13),
        )
        filter_btn.pack(side="right", padx=(0, 10))

        # Center Wrapper
        center_wrapper = ctk.CTkFrame(self.preview_pane, fg_color="transparent")
        center_wrapper.grid(row=1, column=0, sticky="nsew")

        # Preview Container
        preview_container = ctk.CTkFrame(
            center_wrapper,
            fg_color="#222222",
            border_width=1,
            border_color="#3a3a3a",
            corner_radius=12,
        )
        preview_container.pack(padx=20, pady=(10, 10))

        self.preview_lbl = ctk.CTkLabel(
            preview_container,
            text="Rendering...",
            font=("Segoe UI", 14),
            text_color="#888888",
        )
        self.preview_lbl.pack(expand=True, fill="both", padx=20, pady=20)

        # Actions Bar
        actions_frame = ctk.CTkFrame(center_wrapper, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 10))

        btn_font = ctk.CTkFont(family="Segoe UI", size=13)
        ctk.CTkButton(
            actions_frame,
            text="↻ Reset View",
            command=self.reset,
            font=btn_font,
            border_width=1,
            border_color="#3a3a3a",
            fg_color="#333333",
            hover_color="#444444",
            width=100,
            height=32,
            corner_radius=6,
        ).pack(side="left")

        ctk.CTkButton(
            actions_frame,
            text="💾 Save",
            command=self.manual_save_to_db,
            font=btn_font,
            border_width=1,
            border_color="#2563EB",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            width=100,
            height=32,
            corner_radius=6,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            actions_frame,
            text="🖨 Print",
            command=self.print_pdf,
            font=btn_font,
            border_width=1,
            border_color="#3a3a3a",
            fg_color="#333333",
            hover_color="#444444",
            width=80,
            height=32,
            corner_radius=6,
        ).pack(side="right")

        ctk.CTkButton(
            actions_frame,
            text="📄 Save PDF",
            command=self.save_pdf,
            font=btn_font,
            border_width=1,
            border_color="#3a3a3a",
            fg_color="#333333",
            hover_color="#444444",
            width=80,
            height=32,
            corner_radius=6,
        ).pack(side="right", padx=10)

        pages_frame = ctk.CTkFrame(
            actions_frame,
            fg_color="#333333",
            corner_radius=6,
            height=32,
            border_width=1,
            border_color="#3a3a3a",
        )
        pages_frame.pack(side="right")
        pages_frame.pack_propagate(False)
        pages_frame.configure(width=100)
        ctk.CTkLabel(
            pages_frame, text="📄 Pages", font=btn_font, text_color="#E0E0E0"
        ).pack(side="left", padx=(10, 5), pady=4)

        self.pages_lbl = ctk.CTkLabel(
            pages_frame,
            text="00",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#181818",
            text_color="#E0E0E0",
            width=25,
            height=20,
            corner_radius=4,
        )
        self.pages_lbl.pack(side="right", padx=(0, 5), pady=5)

        # Separator
        separator = ctk.CTkFrame(self.preview_pane, height=1, fg_color="#3a3a3a")
        separator.grid(row=3, column=0, sticky="ew", padx=20, pady=10)

        # Folders
        folders_frame = ctk.CTkFrame(self.preview_pane, fg_color="transparent")
        folders_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Generate a solid folder icon using PIL
        if not hasattr(self, "_folder_img"):
            from PIL import ImageDraw

            img = Image.new("RGBA", (140, 110), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Folder tab
            draw.rounded_rectangle([(10, 5), (55, 30)], radius=7, fill="#666666")
            # Folder body
            draw.rounded_rectangle([(10, 20), (130, 105)], radius=10, fill="#555555")
            self._folder_img = ctk.CTkImage(
                light_image=img, dark_image=img, size=(95, 75)
            )

        recent_labels = []
        try:
            import sqlite3

            conn = sqlite3.connect(DB_PATH)
            cur = conn.execute(
                "SELECT id, json_extract(data, '$.customer_name'), product, batch FROM label_history ORDER BY id DESC LIMIT 5"
            )
            for row in cur.fetchall():
                recent_labels.append(
                    {
                        "id": row[0],
                        "customer": row[1] if row[1] else "",
                        "title": row[2] if row[2] else "Unknown",
                        "date": f"Batch: {row[3]}" if row[3] else "-",
                    }
                )
            conn.close()
        except Exception as e:
            print(f"Error loading recent labels: {e}")

        while len(recent_labels) < 5:
            recent_labels.append({"title": "No Label", "date": "-"})

        for folder_data in recent_labels:
            f_container = ctk.CTkFrame(folders_frame, fg_color="transparent")
            f_container.pack(side="left", expand=True, fill="both")

            # Inner container to allow left-alignment of contents while remaining centered in the column
            inner = ctk.CTkFrame(f_container, fg_color="transparent")
            inner.pack(anchor="center")

            def make_cmd(rid):
                return lambda e: self._load_from_history(rid)

            cmd = make_cmd(folder_data["id"]) if "id" in folder_data else lambda e: None

            folder_icon = ctk.CTkLabel(
                inner,
                text="",
                image=self._folder_img,
                cursor="hand2" if "id" in folder_data else "arrow",
            )
            folder_icon.pack(anchor="w")
            folder_icon.bind("<Button-1>", cmd)

            title_lbl = ctk.CTkLabel(
                inner,
                text=(
                    str(folder_data["title"])
                    if len(str(folder_data["title"])) > 15
                    else folder_data["title"]
                ),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#777777",
                cursor="hand2" if "id" in folder_data else "arrow",
            )
            title_lbl.pack(anchor="w", padx=10, pady=(2, 0))
            title_lbl.bind("<Button-1>", cmd)

            if "customer" in folder_data and folder_data["customer"]:
                cust_lbl = ctk.CTkLabel(
                    inner,
                    text=(
                        str(folder_data["customer"])
                        if len(str(folder_data["customer"])) > 18
                        else folder_data["customer"]
                    ),
                    font=ctk.CTkFont(size=11),
                    text_color="#888888",
                    cursor="hand2" if "id" in folder_data else "arrow",
                )
                cust_lbl.pack(anchor="w", padx=10)
                cust_lbl.bind("<Button-1>", cmd)

            date_lbl = ctk.CTkLabel(
                inner,
                text=(
                    str(folder_data["date"])
                    if len(str(folder_data["date"])) > 18
                    else folder_data["date"]
                ),
                font=ctk.CTkFont(size=11),
                text_color="#555555",
                cursor="hand2" if "id" in folder_data else "arrow",
            )
            date_lbl.pack(anchor="w", padx=10)
            date_lbl.bind("<Button-1>", cmd)

            inner.bind("<Button-1>", cmd)
            f_container.bind("<Button-1>", cmd)

    def _build_form(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        form_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=5, pady=5)

        main_col = ctk.CTkFrame(form_container, fg_color="transparent")
        main_col.pack(side="left", fill="both", expand=True, padx=(0, 20))

        def add_section(title):
            ctk.CTkLabel(
                main_col,
                text=title,
                text_color="#E0E0E0",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(anchor="w", padx=10, pady=(15, 6))

        def add_field(label, var):
            entry = ctk.CTkEntry(
                main_col,
                placeholder_text=label,
                height=36,
                font=ctk.CTkFont(size=13),
                fg_color="#333333",
                border_width=1,
                border_color="#3a3a3a",
                corner_radius=6,
                text_color="#E0E0E0",
                placeholder_text_color="#888888",
            )
            if var.get():
                entry.insert(0, var.get())

            def sync_var(event=None):
                var.set(entry.get())

            entry.bind("<KeyRelease>", sync_var)
            entry.bind("<FocusOut>", sync_var)

            entry.pack(fill="x", padx=10, pady=6)
            return entry

        def add_date_field(label, var):
            frame = ctk.CTkFrame(
                main_col,
                fg_color="#333333",
                border_width=1,
                border_color="#3a3a3a",
                corner_radius=6,
                height=36,
            )
            frame.pack(fill="x", padx=10, pady=6)
            frame.pack_propagate(False)

            entry = ctk.CTkEntry(
                frame,
                placeholder_text=label,
                fg_color="transparent",
                border_width=0,
                text_color="#E0E0E0",
                placeholder_text_color="#888888",
                font=ctk.CTkFont(size=13),
            )
            if var.get():
                entry.insert(0, var.get())

            entry.pack(side="left", fill="both", expand=True, padx=(5, 0))

            def sync_var(event):
                var.set(entry.get())

            entry.bind("<KeyRelease>", sync_var)

            def on_focus_out(event):
                raw = entry.get().strip()
                for fmt in (
                    "%d-%b-%Y",
                    "%d-%m-%Y",
                    "%d/%m/%Y",
                    "%Y-%m-%d",
                    "%d.%m.%Y",
                    "%d %b %Y",
                ):
                    try:
                        dt = datetime.strptime(raw, fmt)
                        formatted = dt.strftime("%d-%b-%Y")
                        if formatted != raw:
                            entry.delete(0, "end")
                            entry.insert(0, formatted)
                            var.set(formatted)
                        break
                    except Exception:
                        pass

            entry.bind("<FocusOut>", on_focus_out)

            def open_picker():
                def on_select(val):
                    entry.delete(0, "end")
                    entry.insert(0, val)
                    var.set(val)

                DatePickerDialog(
                    self, entry.get() or var.get(), on_select, title=f"Select {label}"
                )

            ctk.CTkButton(
                frame,
                text="📅",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color="#3a3a3a",
                text_color="#888888",
                font=ctk.CTkFont(size=16),
                command=open_picker,
            ).pack(side="right", padx=5)

        # ---- RENDER TEMPLATE SPECIFIC FIELDS ----
        tpl_name = self._selected_tpl.get()
        config = TEMPLATE_CONFIGS.get(tpl_name, list(TEMPLATE_CONFIGS.values())[0])

        PLACEHOLDERS = {
            "product": "Product Name",
            "batch": "Batch No.",
            "mfg_date": "Manufacturing Date",
            "exp_date": "Expire Date",
            "total_quantity": "Total Quantity",
            "drum_capacity": "Packaging Capacity",
        }

        for section_title, fields in config.get("form_sections", []):
            if section_title.upper() != "PRODUCT INFORMATION":
                pass

            if section_title.upper() == "PRODUCT INFORMATION":
                add_section(section_title)

                cust_frame = ctk.CTkFrame(main_col, fg_color="transparent")
                cust_frame.pack(fill="x", padx=10, pady=6)

                cust_entry = ctk.CTkEntry(
                    cust_frame,
                    placeholder_text="Customer Name",
                    height=36,
                    font=ctk.CTkFont(size=13),
                    fg_color="#333333",
                    border_width=1,
                    border_color="#3a3a3a",
                    corner_radius=6,
                    text_color="#E0E0E0",
                    placeholder_text_color="#888888",
                )
                cust_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
                if self.vars["customer_name"].get():
                    cust_entry.insert(0, self.vars["customer_name"].get())

                def sync_cust(e=None):
                    self.vars["customer_name"].set(cust_entry.get())
                    if hasattr(self, "_update_customer_star"):
                        self._update_customer_star()

                cust_entry.bind("<KeyRelease>", sync_cust)
                cust_entry.bind("<FocusOut>", sync_cust)

                self._cust_star_btn = ctk.CTkButton(
                    cust_frame,
                    text="☆",
                    width=36,
                    height=36,
                    fg_color="#333333",
                    hover_color="#444444",
                    text_color="#AAAAAA",
                    font=ctk.CTkFont(size=20),
                    command=self._toggle_customer_bookmark,
                )
                self._cust_star_btn.pack(side="right")
                # Wait for init to finish before calling _update_customer_star
                self.after(100, self._update_customer_star)

            for field_label, var_name in fields:
                display_label = PLACEHOLDERS.get(var_name, field_label)

                if var_name == "product":
                    product_names = self._get_product_names()
                    combo_values = ["+ Create New Product..."] + product_names
                    current_product = self.vars["product"].get().strip()

                    self._product_combo = ctk.CTkComboBox(
                        main_col,
                        values=combo_values,
                        state="readonly",
                        height=36,
                        font=ctk.CTkFont(size=13),
                        fg_color="#333333",
                        border_width=1,
                        border_color="#3a3a3a",
                        corner_radius=6,
                        text_color="#E0E0E0",
                        button_color="#333333",
                        button_hover_color="#444444",
                        dropdown_fg_color="#2B2B2B",
                        dropdown_text_color="#E0E0E0",
                        command=self._on_product_selected,
                    )
                    if current_product:
                        self._product_combo.set(current_product)
                    else:
                        self._product_combo.set(display_label)  # Use as placeholder

                    self._product_combo.pack(fill="x", padx=10, pady=6)
                elif var_name in ("mfg_date", "exp_date"):
                    add_date_field(display_label, self.vars[var_name])
                elif var_name in self.vars:
                    add_field(display_label, self.vars[var_name])

        self.drum_type_combo = ctk.CTkOptionMenu(
            main_col,
            variable=self.vars["drum_type"],
            values=["Plastic Drum", "Paper Drum", "Custom Weight"],
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color="#333333",
            text_color="#E0E0E0",
            button_color="#333333",
            button_hover_color="#444444",
            command=self._on_template_change,
        )
        self.drum_type_combo.pack(fill="x", padx=10, pady=6)

        if self.vars["drum_type"].get() == "Custom Weight":
            add_field("Custom Gross Wt (Kg)", self.vars["custom_tare"])

        self.last_label_frame = ctk.CTkFrame(main_col, fg_color="transparent")
        ctk.CTkButton(
            self.last_label_frame,
            text="Edit Last Page (Optional)",
            fg_color="#333333",
            hover_color="#444444",
            text_color="#E0E0E0",
            anchor="w",
            height=36,
            corner_radius=6,
            font=ctk.CTkFont(size=13),
        ).pack(fill="x", pady=(15, 6), padx=10)

        def add_field_to_frame(label_text, var):
            entry = ctk.CTkEntry(
                self.last_label_frame,
                placeholder_text=label_text,
                height=36,
                font=ctk.CTkFont(size=13),
                fg_color="#333333",
                border_width=1,
                border_color="#3a3a3a",
                corner_radius=6,
                text_color="#E0E0E0",
                placeholder_text_color="#888888",
            )
            if var.get():
                entry.insert(0, var.get())

            def sync_var(event=None):
                var.set(entry.get())

            entry.bind("<KeyRelease>", sync_var)
            entry.bind("<FocusOut>", sync_var)

            entry.pack(fill="x", padx=10, pady=6)
            return entry

        self.entry_last_gross = add_field_to_frame(
            "Custom Gross Weight", self.vars["last_gross_wt"]
        )
        self.entry_last_field_name = add_field_to_frame(
            "Packaging Details", self.vars["last_drum_label_text"]
        )

        # ---- DOCUMENT UPLOAD SECTION (COA / SPEC) ----
        ctk.CTkLabel(
            main_col,
            text="📄 Attach Documents (COA / Spec)",
            text_color="#AAAAAA",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(fill="x", padx=10, pady=(15, 4))

        def _upload_doc(doc_type):
            import ftplib
            from tkinter import filedialog, messagebox

            if not FTP_HOST or not FTP_USER:
                messagebox.showwarning(
                    "FTP Not Configured",
                    "Please go to Settings and fill in your FTP credentials first.",
                    parent=self,
                )
                return

            pdf_path = filedialog.askopenfilename(
                title=f"Select {doc_type} PDF",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                parent=self,
            )
            if not pdf_path:
                return

            product = self.vars["product"].get().strip().replace(" ", "_")[:20]
            batch = self.vars["batch"].get().strip().replace("/", "-")[:15]
            filename = f"{product}_{batch}_{doc_type}.pdf".replace(" ", "_")
            remote_path = FTP_UPLOAD_DIR.rstrip("/") + "/" + filename

            try:
                ftp = ftplib.FTP()
                ftp.connect(FTP_HOST, 21, timeout=15)
                ftp.login(FTP_USER, FTP_PASS)
                with open(pdf_path, "rb") as f:
                    ftp.storbinary(f"STOR {remote_path}", f)
                ftp.quit()

                url_var = (
                    self.vars["coa_url"] if doc_type == "COA" else self.vars["spec_url"]
                )
                url_var.set(filename)  # Only store filename
                messagebox.showinfo(
                    "Upload Successful",
                    f"{doc_type} uploaded successfully!\n\nFilename: {filename}",
                    parent=self,
                )
                _refresh_doc_buttons()
            except Exception as ex:
                messagebox.showerror(
                    "Upload Failed",
                    f"Could not upload {doc_type}:\n{ex}",
                    parent=self,
                )

        def _clear_doc(doc_type):
            url_var = (
                self.vars["coa_url"] if doc_type == "COA" else self.vars["spec_url"]
            )
            url_var.set("")
            _refresh_doc_buttons()

        self._doc_btn_frame = ctk.CTkFrame(main_col, fg_color="transparent")
        self._doc_btn_frame.pack(fill="x", padx=10, pady=4)

        def _refresh_doc_buttons():
            for w in self._doc_btn_frame.winfo_children():
                w.destroy()
            for doc_type, url_var in [
                ("COA", self.vars["coa_url"]),
                ("Spec", self.vars["spec_url"]),
            ]:
                row = ctk.CTkFrame(self._doc_btn_frame, fg_color="transparent")
                row.pack(fill="x", pady=3)
                has_url = bool(url_var.get().strip())
                btn_color = "#1a6b3c" if has_url else "#333333"
                btn_text = (
                    f"✅ {doc_type} Uploaded" if has_url else f"📎 Upload {doc_type}"
                )
                ctk.CTkButton(
                    row,
                    text=btn_text,
                    fg_color=btn_color,
                    hover_color="#444444",
                    text_color="#E0E0E0",
                    anchor="w",
                    height=34,
                    corner_radius=6,
                    font=ctk.CTkFont(size=12),
                    command=lambda dt=doc_type: _upload_doc(dt),
                ).pack(side="left", fill="x", expand=True, padx=(0, 5))
                if has_url:
                    ctk.CTkButton(
                        row,
                        text="✕",
                        width=34,
                        height=34,
                        fg_color="#4a1a1a",
                        hover_color="#6a2a2a",
                        text_color="#ff8080",
                        corner_radius=6,
                        font=ctk.CTkFont(size=14),
                        command=lambda dt=doc_type: _clear_doc(dt),
                    ).pack(side="right")

        _refresh_doc_buttons()

    def _on_template_change(self, *args):
        self._build_form()
        self._on_change_debounced()

    def _get_all_labels_values(self) -> list:
        drums = calculate_drums(
            self.vars.get("total_quantity", ctk.StringVar(value="100")).get().strip(),
            self.vars.get("drum_type", ctk.StringVar(value="Plastic Drum"))
            .get()
            .strip(),
            self.vars.get("drum_capacity", ctk.StringVar(value="25")).get().strip(),
            self.vars.get("custom_tare", ctk.StringVar(value="0.0")).get().strip(),
        )
        dt = len(drums)
        labels = []
        for i, d in enumerate(drums):
            net = f"{d['net']:.2f} Kg"
            gross = f"{d['gross']:.2f} Kg"
            dn = f"{(i+1):02d}"

            label_data = {}
            for k, v in self.vars.items():
                if k == "origin":
                    label_data[k] = v.get().strip().upper()
                else:
                    label_data[k] = v.get().strip()
            label_data["net_wt"] = net
            label_data["gross_wt"] = gross
            label_data["drum"] = f"{dn}/{dt:02d}"
            label_data["drum_label_text"] = "#Drum:"
            label_data["coa_url"] = (
                self.vars.get("coa_url", ctk.StringVar()).get().strip()
            )
            label_data["spec_url"] = (
                self.vars.get("spec_url", ctk.StringVar()).get().strip()
            )
            labels.append(label_data)

        if labels:
            last_idx = -1
            if (
                self.vars.get("last_gross_wt")
                and self.vars["last_gross_wt"].get().strip()
            ):
                try:
                    custom_val = float(
                        self.vars["last_gross_wt"]
                        .get()
                        .strip()
                        .lower()
                        .replace("kg", "")
                        .strip()
                    )
                    current_net = float(
                        labels[last_idx]["net_wt"].replace(" Kg", "").strip()
                    )
                    final_gross = current_net + custom_val
                    labels[last_idx]["gross_wt"] = f"{final_gross:.2f} Kg"
                except Exception:
                    pass
            if (
                self.vars.get("last_drum_label_text")
                and self.vars["last_drum_label_text"].get().strip()
            ):
                labels[last_idx]["drum_label_text"] = (
                    self.vars["last_drum_label_text"].get().strip()
                )

        return labels

    def _on_change_debounced(self, *_):
        if self._render_after_id:
            self.after_cancel(self._render_after_id)
        if hasattr(self, "_save_after_id") and self._save_after_id:
            self.after_cancel(self._save_after_id)
        self._save_after_id = self.after(3000, self._save_to_history)

        try:
            total_qty = float(
                self.vars.get("total_quantity", ctk.StringVar(value="100"))
                .get()
                .strip()
            )
            cap = float(
                self.vars.get("drum_capacity", ctk.StringVar(value="25")).get().strip()
            )
            if cap > 0 and (total_qty % cap != 0) and total_qty > 0:
                if (
                    hasattr(self, "last_label_frame")
                    and not self.last_label_frame.winfo_manager()
                ):
                    self.last_label_frame.pack(fill="x", pady=5)
            else:
                if (
                    hasattr(self, "last_label_frame")
                    and self.last_label_frame.winfo_manager()
                ):
                    self.last_label_frame.pack_forget()
        except:
            if (
                hasattr(self, "last_label_frame")
                and self.last_label_frame.winfo_manager()
            ):
                self.last_label_frame.pack_forget()

        self._render_after_id = self.after(400, self._render_preview)

    def _render_preview(self):
        if self._is_rendering:
            self._on_change_debounced()
            return
        self._is_rendering = True
        tpl = self._selected_tpl.get()
        if not tpl:
            self._is_rendering = False
            return

        labels_values = self._get_all_labels_values()
        if hasattr(self, "pages_lbl"):
            self.pages_lbl.configure(text=f"{len(labels_values):02d}")
        config = TEMPLATE_CONFIGS.get(tpl, list(TEMPLATE_CONFIGS.values())[0])

        def render_thread():
            try:
                from reportlab.lib.units import mm as mm_unit
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4

                if (
                    not hasattr(self, "_cached_tpl_name")
                    or self._cached_tpl_name != tpl
                ):
                    raw_svg = load_svg_text(tpl)
                    root = ET.fromstring(raw_svg)
                    for g in root.findall(f".//{{{SVG_NS}}}g[@id='text-overlay']"):
                        root.remove(g)
                    clean_svg = ET.tostring(
                        root, encoding="unicode", xml_declaration=False
                    )
                    if "<svg" in clean_svg:
                        clean_svg = clean_svg[clean_svg.index("<svg") :]

                    tmp_svg = tempfile.mktemp(suffix=".svg")
                    with open(tmp_svg, "w", encoding="utf-8") as fh:
                        fh.write(clean_svg)
                    self._cached_drawing = svg2rlg(tmp_svg)
                    os.remove(tmp_svg)
                    self._cached_tpl_name = tpl

                drawing = copy.deepcopy(self._cached_drawing)
                margin = 10 * mm_unit
                page_w, page_h = A4
                avail_w = page_w - 2 * margin
                spacing = 0 * mm_unit
                avail_h = (page_h - 2 * margin - 2 * spacing) / 3

                scale_w = avail_w / drawing.width
                scale_h = avail_h / drawing.height
                scale = min(scale_w, scale_h)

                label_w = drawing.width * scale
                label_h = drawing.height * scale
                drawing.width = label_w
                drawing.height = label_h
                drawing.transform = (scale, 0, 0, scale, 0, 0)

                pdf_bytes = io.BytesIO()
                c = canvas.Canvas(pdf_bytes, pagesize=(label_w, label_h))

                bg_color_hex = config.get("bg_color", "#FFFFFF")
                c.setFillColor(HexColor(bg_color_hex))
                c.rect(0, 0, label_w, label_h, fill=1, stroke=0)

                renderPDF.draw(drawing, c, 0, 0)

                values = labels_values[0] if labels_values else {}
                draw_native_labels(c, config, values, 0, 0, label_h, scale)

                logo_path = os.path.join(LABELS_DIR, "BMI Logo.png")
                has_logo = os.path.exists(logo_path)
                logo_options = config.get("logo_options", {})
                if has_logo and not logo_options.get("hide", False):
                    logo_x = logo_options.get("x", 18) * scale
                    logo_y = label_h - (logo_options.get("y_offset", 52) * scale)
                    logo_w = logo_options.get("w", 45) * scale
                    logo_h = logo_options.get("h", 40) * scale

                    if logo_options.get("draw_bg", True):
                        c.setFillColorRGB(1, 1, 1)
                        bg_x = logo_options.get("bg_x", 10) * scale
                        bg_y = logo_y - (logo_options.get("bg_y_offset", 2) * scale)
                        bg_w = logo_options.get("bg_w", 48) * scale
                        bg_h = logo_options.get("bg_h", 45) * scale
                        c.rect(bg_x, bg_y, bg_w, bg_h, fill=1, stroke=0)

                    c.drawImage(
                        logo_path,
                        logo_x,
                        logo_y,
                        width=logo_w,
                        height=logo_h,
                        mask="auto",
                    )

                draw_qr_code(
                    c, values, label_w, label_h, scale, config.get("qr_options", {})
                )

                c.save()
                pdf_bytes.seek(0)

                doc = pymupdf.open("pdf", pdf_bytes.read())
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=300)
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                doc.close()

                self.after(0, self._update_preview_ui, img)
            except Exception as e:
                self.after(0, self._update_preview_error, str(e))

        threading.Thread(target=render_thread, daemon=True).start()

    def _update_preview_ui(self, pil_img):
        self._current_pil_img = pil_img
        self._resize_preview_image()

    def _on_preview_pane_resize(self, event):
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(100, self._resize_preview_image)

    def _resize_preview_image(self, event=None):
        if not hasattr(self, "_current_pil_img") or not self._current_pil_img:
            return
            
        scaling = self._get_window_scaling() if hasattr(self, "_get_window_scaling") else 1.0

        # Ask the preview pane exactly how much physical space it has
        pane_w = self.preview_pane.winfo_width() / scaling
        pane_h = self.preview_pane.winfo_height() / scaling
        
        # If the window is still launching and width is invalid, guess based on screen size
        if pane_w <= 10 or pane_h <= 10:
            app_w = (self.winfo_screenwidth() / scaling) * 0.85
            app_h = (self.winfo_screenheight() / scaling) * 0.85
            pane_w = app_w - 620
            pane_h = app_h - 100
            
        # Give some padding so the image doesn't touch the absolute edges
        available_w = pane_w - 60
        available_h = pane_h - 120 # Account for toolbar and padding
        
        if available_w < 200: available_w = 200
        if available_h < 200: available_h = 200

        img_ratio = self._current_pil_img.width / self._current_pil_img.height
        
        max_w_for_h = available_h * img_ratio
        
        constant_w = min(available_w, max_w_for_h)
        
        if constant_w > 1200:
            constant_w = 1200

        new_w = int(constant_w)
        new_h = int(constant_w / img_ratio)

        ctk_img = ctk.CTkImage(
            light_image=self._current_pil_img, dark_image=self._current_pil_img, size=(new_w, new_h)
        )
        self.preview_lbl.configure(image=ctk_img, text="")
        self.preview_lbl._image_ref = ctk_img
        self._is_rendering = False

    def _update_preview_error(self, err_msg):
        self.preview_lbl.configure(
            image="", text=f"Error rendering preview:\n{err_msg}"
        )
        self._is_rendering = False

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS label_bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                saved_at TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS label_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                month TEXT NOT NULL,
                saved_at TEXT NOT NULL,
                data TEXT NOT NULL,
                batch TEXT NOT NULL,
                UNIQUE(product, batch)
            )
        """
        )

        cols = [
            c[1] for c in conn.execute("PRAGMA table_info(label_history)").fetchall()
        ]

        if cols and "month" not in cols:
            conn.execute("DROP TABLE label_history")

        # Force migration if the old UNIQUE(product, month) constraint is still in the schema
        try:
            schema = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='label_history'"
            ).fetchone()[0]
            if (
                "UNIQUE(product, month)" in schema
                or "UNIQUE(product, month)" in schema.replace(" ", "")
            ):
                conn.execute("ALTER TABLE label_history RENAME TO label_history_old")
                conn.execute(
                    """
                    CREATE TABLE label_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product TEXT NOT NULL,
                        month TEXT NOT NULL,
                        saved_at TEXT NOT NULL,
                        data TEXT NOT NULL,
                        batch TEXT NOT NULL,
                        UNIQUE(product, batch)
                    )
                """
                )
                conn.execute(
                    """
                    INSERT INTO label_history (id, product, month, saved_at, data, batch)
                    SELECT id, product, month, saved_at, data,
                           CASE WHEN json_extract(data, '$.batch') IS NULL THEN '' ELSE json_extract(data, '$.batch') END
                    FROM label_history_old
                """
                )
                conn.execute("DROP TABLE label_history_old")
        except Exception as e:
            print("Migration error 2:", e)

    def _update_customer_star(self):
        import sqlite3

        if not hasattr(self, "_cust_star_btn"):
            return
        cust = self.vars["customer_name"].get().strip()
        if not cust:
            self._cust_star_btn.configure(text="☆", text_color="#AAAAAA")
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute(
                    "CREATE TABLE IF NOT EXISTS customer_bookmarks (customer_name TEXT PRIMARY KEY, data TEXT)"
                )
                try:
                    c.execute("ALTER TABLE customer_bookmarks ADD COLUMN data TEXT")
                except:
                    pass
                c.execute(
                    "SELECT 1 FROM customer_bookmarks WHERE customer_name=?", (cust,)
                )
                if c.fetchone():
                    self._cust_star_btn.configure(text="★", text_color="#F59E0B")
                else:
                    self._cust_star_btn.configure(text="☆", text_color="#AAAAAA")
        except:
            pass

    def _toggle_customer_bookmark(self):
        import sqlite3

        cust = self.vars["customer_name"].get().strip()
        if not cust:
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute(
                    "CREATE TABLE IF NOT EXISTS customer_bookmarks (customer_name TEXT PRIMARY KEY, data TEXT)"
                )
                try:
                    c.execute("ALTER TABLE customer_bookmarks ADD COLUMN data TEXT")
                except:
                    pass

                c.execute(
                    "SELECT 1 FROM customer_bookmarks WHERE customer_name=?", (cust,)
                )
                if c.fetchone():
                    c.execute(
                        "DELETE FROM customer_bookmarks WHERE customer_name=?", (cust,)
                    )
                    c.execute(
                        "DELETE FROM label_bookmarks WHERE json_extract(data, '$.customer_name') = ?",
                        (cust,),
                    )
                else:
                    import json

                    data = {k: v.get() for k, v in self.vars.items()}
                    data["template"] = self._selected_tpl.get()
                    json_data = json.dumps(data)
                    prod_name = self.vars["product"].get().strip() or "Unknown Product"
                    bookmark_name = f"{cust} - {prod_name}"
                    c.execute(
                        "INSERT INTO customer_bookmarks (customer_name, data) VALUES (?, ?)",
                        (cust, json_data),
                    )
                    c.execute(
                        "INSERT INTO label_bookmarks (name, saved_at, data) VALUES (?, datetime('now', 'localtime'), ?)",
                        (bookmark_name, json_data),
                    )
                conn.commit()
            self._update_customer_star()
            self._refresh_history_panel()
        except Exception as e:
            print("Bookmark error:", e)

        count = conn.execute("SELECT COUNT(*) FROM label_history").fetchone()[0]
        if count == 0:
            init_data = {
                "customer_name": "",
                "product": "Phosphatidylserine 80%",
                "batch": "YL-29-20260805",
                "fssai": "10622999000028",
                "usfda": "12099156850",
                "mfg_date": "05-Aug-2026",
                "exp_date": "04-Aug-2028",
                "total_quantity": "100",
                "drum_capacity": "25",
                "drum_type": "Plastic Drum",
                "custom_tare": "0.0",
                "origin": "MADE IN INDIA",
                "last_gross_wt": "",
                "last_drum_label_text": "#Drum:",
                "template": "Label 1 FSSAI.svg",
            }
            conn.execute(
                "INSERT INTO label_history (product, month, saved_at, data) VALUES (?, ?, ?, ?)",
                (
                    "Phosphatidylserine 80%",
                    datetime.now().strftime("%Y-%m"),
                    datetime.now().strftime("%d-%b-%Y %H:%M"),
                    json.dumps(init_data),
                ),
            )
        conn.commit()
        conn.close()

    def manual_save_to_db(self):
        from tkinter import messagebox
        import sqlite3, json
        from datetime import datetime

        data = {k: v.get() for k, v in self.vars.items()}
        data["template"] = self._selected_tpl.get()
        product = data.get("product", "").strip()
        batch = data.get("batch", "").strip()

        if len(product) < 3 or product.startswith("+ Create"):
            messagebox.showwarning(
                "Incomplete",
                "Please enter a valid Product Name to save to the database.",
            )
            return

        saved_at = datetime.now().strftime("%d-%b-%Y %H:%M")
        current_month = datetime.now().strftime("%Y-%m")
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                """
                INSERT INTO label_history (product, month, saved_at, data, batch)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(product, batch) DO UPDATE SET saved_at=excluded.saved_at, data=excluded.data, month=excluded.month
                """,
                (product, current_month, saved_at, json.dumps(data), batch),
            )
            conn.commit()
            conn.close()
            self._refresh_history_panel()
            self._refresh_product_dropdown()
            messagebox.showinfo("Saved", f"Successfully saved '{product}' to database!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def _save_to_history(self):
        data = {k: v.get() for k, v in self.vars.items()}
        data["template"] = self._selected_tpl.get()
        product = data.get("product", "").strip()
        batch = data.get("batch", "").strip()

        if len(product) < 3 or product.startswith("+ Create") or len(batch) < 2:
            return

        saved_at = datetime.now().strftime("%d-%b-%Y %H:%M")
        current_month = datetime.now().strftime("%Y-%m")

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                """
                INSERT INTO label_history (product, month, saved_at, data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(product, month) DO UPDATE SET saved_at=excluded.saved_at, data=excluded.data
            """,
                (product, current_month, saved_at, json.dumps(data)),
            )
            conn.commit()
            conn.close()
            self._refresh_history_panel()
            self._refresh_product_dropdown()
        except Exception as e:
            print(f"History save error: {e}")

    def _auto_save_monthly_pdf(self):
        """Automatically saves the generated PDF to the Monthly Data folder inside a subfolder named after the Customer."""
        tpl = self._selected_tpl.get()
        if not tpl:
            return

        prod_name = self.vars["product"].get().strip()
        if len(prod_name) < 2 or prod_name.startswith("+ Create"):
            return

        # Sanitize customer name for folder creation
        customer_name = self.vars.get("customer_name").get().strip()
        safe_customer_name = re.sub(r'[\\/*?:"<>|]', "", customer_name).strip()
        if not safe_customer_name:
            safe_customer_name = "General"

        # Sanitize product name for file creation
        safe_prod_name = re.sub(r'[\\/*?:"<>|]', "", prod_name).strip()
        if not safe_prod_name:
            safe_prod_name = "Untitled_Product"

        current_month = datetime.now().strftime("%Y-%m")

        # New Target Path: Monthly Data / YYYY-MM / Customer Name
        target_dir = os.path.join(MONTHLY_DATA_DIR, current_month, safe_customer_name)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        # File is named strictly by product name to naturally overwrite older versions in this directory
        file_path = os.path.join(target_dir, f"{safe_prod_name}.pdf")

        try:
            export_pdf(tpl, self._get_all_labels_values(), file_path)
        except Exception as e:
            print(f"Background auto-save failed: {e}")

    def _create_new_product(self):
        dialog = ctk.CTkInputDialog(
            text="Enter new product name:", title="Create New Product"
        )
        new_name = dialog.get_input()

        if not new_name or not new_name.strip():
            self._refresh_product_dropdown()
            return

        new_name = new_name.strip()
        if new_name == "+ Create New Product...":
            self._refresh_product_dropdown()
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT id FROM label_history WHERE product=?", (new_name,)
            ).fetchone()
            conn.close()
            if row:
                messagebox.showinfo(
                    "Product Exists",
                    f"'{new_name}' already exists in history. Loading it now.",
                )
                self._load_from_history(row[0])
                return
        except Exception as e:
            print(f"DB check error: {e}")

        # Retain previous values for the new product
        prev_customer = self.vars["customer_name"].get().strip()
        prev_fssai = self.vars["fssai"].get().strip()
        prev_usfda = self.vars["usfda"].get().strip()
        prev_drum_cap = self.vars["drum_capacity"].get().strip()
        prev_origin = self.vars["origin"].get().strip()
        prev_drum_type = self.vars["drum_type"].get().strip()
        prev_tare = self.vars["custom_tare"].get().strip()

        self.vars["product"].set(new_name)
        self.vars["customer_name"].set(prev_customer)
        self.vars["fssai"].set(prev_fssai if prev_fssai else "10622999000028")
        self.vars["usfda"].set(prev_usfda if prev_usfda else "12099156850")
        self.vars["drum_capacity"].set(prev_drum_cap if prev_drum_cap else "25")
        self.vars["origin"].set(prev_origin if prev_origin else "MADE IN INDIA")
        self.vars["drum_type"].set(prev_drum_type if prev_drum_type else "Plastic Drum")
        self.vars["custom_tare"].set(prev_tare if prev_tare else "0.0")

        # Clear batch specific fields for the new product
        self.vars["batch"].set("")
        self.vars["coa_url"].set("")
        self.vars["spec_url"].set("")
        self.vars["last_gross_wt"].set("")
        self.vars["last_drum_label_text"].set("#Drum:")

        self._build_form()

        self._save_to_history()
        self._refresh_product_dropdown()
        self._refresh_history_panel()
        self._on_change_debounced()

    def _rename_product(self):
        curr_name = self.vars["product"].get().strip()
        if not curr_name or curr_name.startswith("+ Create"):
            return

        dialog = ctk.CTkInputDialog(
            text=f"Rename '{curr_name}' to:", title="Rename Product"
        )
        new_name = dialog.get_input()
        if not new_name or not new_name.strip() or new_name.strip() == curr_name:
            return
        new_name = new_name.strip()

        try:
            conn = sqlite3.connect(DB_PATH)
            exists = conn.execute(
                "SELECT id FROM label_history WHERE product=?", (new_name,)
            ).fetchone()
            if exists:
                conn.close()
                messagebox.showwarning(
                    "Exists", f"Product '{new_name}' already exists."
                )
                return
            conn.execute(
                "UPDATE label_history SET product=? WHERE product=?",
                (new_name, curr_name),
            )
            conn.commit()
            conn.close()
            self.vars["product"].set(new_name)
            self._save_to_history()
            self._refresh_product_dropdown()
            self._refresh_history_panel()
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename product:\n{e}")

    def _load_from_history(self, row_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.execute("SELECT data FROM label_history WHERE id=?", (row_id,))
            row = cur.fetchone()
            conn.close()
            if not row:
                return
            data = json.loads(row[0])

            # Always keep document URLs empty when loading from history
            # The user wants to manually upload them every time.
            self.vars["coa_url"].set("")
            self.vars["spec_url"].set("")

            if "template" in data and data["template"] in self._templates:
                self._selected_tpl.set(data["template"])
            for k, v in data.items():
                if k in self.vars:
                    if k in ("coa_url", "spec_url"):
                        continue
                    # Fallback for FSSAI and USFDA if they are saved as empty
                    if k == "fssai" and not v.strip():
                        self.vars[k].set("10622999000028")
                    elif k == "usfda" and not v.strip():
                        self.vars[k].set("12099156850")
                    else:
                        self.vars[k].set(v)
            self._on_template_change()
            if hasattr(self, "_product_combo"):
                self._product_combo.set(self.vars["product"].get())
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load history entry:\n{e}")

    def _refresh_history_panel(self, *_):
        if not hasattr(self, "history_list_frame"):
            return

        for w in self.history_list_frame.winfo_children():
            w.destroy()

        try:
            conn = sqlite3.connect(DB_PATH)
            months = conn.execute(
                "SELECT DISTINCT month FROM label_history ORDER BY month DESC"
            ).fetchall()
            month_list = (
                [m[0] for m in months] if months else [datetime.now().strftime("%Y-%m")]
            )

            current_sel = self.history_month_var.get()
            if current_sel not in month_list and current_sel != "Current Month":
                self.history_month_var.set(
                    month_list[0] if month_list else datetime.now().strftime("%Y-%m")
                )

            self.history_month_combo.configure(values=month_list)

            selected_month = self.history_month_var.get()
            if selected_month == "Current Month":
                selected_month = datetime.now().strftime("%Y-%m")

            rows = conn.execute(
                "SELECT id, product, saved_at FROM label_history WHERE month=? ORDER BY saved_at DESC LIMIT 20",
                (selected_month,),
            ).fetchall()
            conn.close()
        except Exception as e:
            rows = []

        if not rows:
            ctk.CTkLabel(
                self.history_list_frame,
                text="No history for this month",
                text_color="#777777",
                font=ctk.CTkFont(size=11),
            ).pack(anchor="w", padx=5, pady=4)
            return

        for row_id, product, saved_at in rows:
            item_frame = ctk.CTkFrame(
                self.history_list_frame, fg_color="#2B2B2B", corner_radius=6
            )
            item_frame.pack(fill="x", pady=2)

            text_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(
                text_frame,
                text=product[:22],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#E0E0E0",
                anchor="w",
            ).pack(anchor="w", padx=8, pady=(4, 0))
            ctk.CTkLabel(
                text_frame,
                text=saved_at,
                font=ctk.CTkFont(size=10),
                text_color="#888888",
                anchor="w",
            ).pack(anchor="w", padx=8, pady=(0, 4))

            ctk.CTkButton(
                item_frame,
                text="✕",
                width=28,
                height=28,
                corner_radius=6,
                fg_color="#FEE2E2",
                hover_color="#FECACA",
                text_color="#EF4444",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda rid=row_id: self._delete_from_history(rid),
            ).pack(side="right", padx=6, pady=6)

            text_frame.bind(
                "<Button-1>", lambda e, rid=row_id: self._load_from_history(rid)
            )
            for child in text_frame.winfo_children():
                child.bind(
                    "<Button-1>", lambda e, rid=row_id: self._load_from_history(rid)
                )

    def _delete_from_history(self, row_id):
        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT product FROM label_history WHERE id=?", (row_id,)
            ).fetchone()
            deleted_prod = row[0] if row else ""
            conn.close()
            product_name = deleted_prod if deleted_prod else "this entry"
        except Exception:
            product_name = "this entry"
            deleted_prod = ""

        confirmed = messagebox.askyesno(
            "Delete Entry",
            f"Delete '{product_name}' from history?\n\nThis cannot be undone.",
        )
        if not confirmed:
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM label_history WHERE id=?", (row_id,))
            conn.commit()
            conn.close()
            self._refresh_history_panel()

            if deleted_prod and self.vars["product"].get().strip() == deleted_prod:
                remaining = self._get_product_names()
                if remaining:
                    conn = sqlite3.connect(DB_PATH)
                    first_row = conn.execute(
                        "SELECT id FROM label_history WHERE product=?", (remaining[0],)
                    ).fetchone()
                    conn.close()
                    if first_row:
                        self._load_from_history(first_row[0])
                else:
                    self.reset()
            else:
                self._refresh_product_dropdown()
        except Exception as e:
            messagebox.showerror("Delete Error", f"Could not delete entry:\n{e}")

    def _get_product_names(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT DISTINCT product FROM label_history ORDER BY product"
            ).fetchall()
            conn.close()
            return [r[0] for r in rows]
        except Exception:
            return []

    def _refresh_product_dropdown(self):
        if hasattr(self, "_product_combo"):
            names = self._get_product_names()
            values = ["+ Create New Product..."] + names
            self._product_combo.configure(values=values)
            curr = self.vars["product"].get().strip()
            if curr in names:
                self._product_combo.set(curr)
            elif names:
                self._product_combo.set(names[0])
            else:
                self._product_combo.set("+ Create New Product...")

    def _on_product_selected(self, selected_product):
        if selected_product == "+ Create New Product...":
            self._create_new_product()
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT id FROM label_history WHERE product=? ORDER BY saved_at DESC LIMIT 1",
                (selected_product,),
            ).fetchone()
            conn.close()
            if row:
                self._load_from_history(row[0])
        except Exception as e:
            print(f"Product select error: {e}")

    def print_pdf(self):
        tpl = self._selected_tpl.get()
        if not tpl:
            messagebox.showwarning("No Template", "Please select a template first.")
            return

        try:
            # Silently auto-save to the Monthly Data -> Customer folder before printing
            self._auto_save_monthly_pdf()

            tmp_pdf = tempfile.mktemp(suffix=".pdf")
            export_pdf(tpl, self._get_all_labels_values(), tmp_pdf)
            os.startfile(tmp_pdf)
        except Exception as ex:
            messagebox.showerror("Error", f"Could not open print preview:\n{ex}")

    def save_pdf(self):
        tpl = self._selected_tpl.get()
        if not tpl:
            messagebox.showwarning("No Template", "Please select a template first.")
            return

        # Silently auto-save to the Monthly Data -> Customer folder
        self._auto_save_monthly_pdf()

        prod = self.vars["product"].get().replace(" ", "_")[:20]
        bat = self.vars["batch"].get().replace("/", "-")[:15]
        default_name = f"BMI_{prod}_{bat}.pdf"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=default_name,
        )
        if not path:
            return
        try:
            export_pdf(tpl, self._get_all_labels_values(), path)
            messagebox.showinfo("Saved", f"PDF saved successfully!\n\n{path}")
            os.startfile(path)
        except Exception as ex:
            messagebox.showerror("Error", f"Could not save PDF:\n{ex}")

    def _open_export_menu(self):
        import tkinter as tk

        menu = tk.Menu(
            self,
            tearoff=0,
            font=("Segoe UI", 11),
            bg="#2a2a2a",
            fg="#E0E0E0",
            activebackground="#333333",
            activeforeground="#FFFFFF",
        )
        menu.add_command(
            label="📥Export to CSV (Excel)", command=self._export_history_csv
        )
        x = self.grid_btn.winfo_rootx()
        y = self.grid_btn.winfo_rooty() + self.grid_btn.winfo_height()
        menu.tk_popup(x, y)

    def _export_history_csv(self):
        import sqlite3, json, csv, os
        from tkinter import filedialog, messagebox

        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT product, month, saved_at, data FROM label_history ORDER BY saved_at DESC"
            ).fetchall()
            conn.close()
            if not rows:
                messagebox.showinfo(
                    "No Data", "There is no history data to export.", parent=self
                )
                return
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="Label_History_Export.csv",
                parent=self,
            )
            if not path:
                return
            all_keys = ["Date Saved", "Month", "Product Name"]
            parsed_rows = []
            for prod, month, saved_at, data_str in rows:
                try:
                    data = json.loads(data_str)
                except:
                    data = {}
                row_dict = {
                    "Date Saved": saved_at,
                    "Month": month,
                    "Product Name": prod,
                }
                for k, v in data.items():
                    nice_key = k.replace("_", " ").title()
                    if nice_key not in all_keys:
                        all_keys.append(nice_key)
                    row_dict[nice_key] = v
                parsed_rows.append(row_dict)
            with open(path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=all_keys)
                writer.writeheader()
                writer.writerows(parsed_rows)
            messagebox.showinfo(
                "Export Success",
                f"Successfully exported {len(rows)} records to:\n{path}",
                parent=self,
            )
            os.startfile(path)
        except Exception as e:
            messagebox.showerror(
                "Export Error", f"Failed to export CSV:\n{e}", parent=self
            )

    def reset(self):
        self.vars["customer_name"].set("")
        self.vars["product"].set("")
        self.vars["batch"].set("")
        self.vars["fssai"].set("10622999000028")
        self.vars["usfda"].set("12099156850")
        self.vars["mfg_date"].set("")
        self.vars["exp_date"].set("")
        self.vars["total_quantity"].set("")
        self.vars["drum_capacity"].set("")
        self.vars["drum_type"].set("Packaging Item")
        self.vars["custom_tare"].set("")
        self.vars["origin"].set("")
        self.vars["last_gross_wt"].set("")
        self.vars["last_drum_label_text"].set("")
        if hasattr(self, "_templates") and len(self._templates) > 0:
            self._selected_tpl.set(self._templates[0])
        self._build_form()
        self._on_change_debounced()

    def _on_sidebar_click(self, btn_text):
        if "Recent" in btn_text:
            self.open_recent_window()
        elif "Customer" in btn_text:
            self.open_customer_history_window()
        elif "Batch" in btn_text:
            self.open_batch_history_window()
        elif "Bookmark" in btn_text:
            self.open_bookmark_window()
        else:
            from tkinter import messagebox

            messagebox.showinfo(
                "Coming Soon", f"{btn_text.strip()} feature is coming soon!"
            )

    def _refresh_bookmark_accordion(self, frame):
        for w in frame.winfo_children():
            w.destroy()
        # pop_bookmark is a local function in _build_sidebar, so we can't easily call it.
        # But wait! We can just define pop_bookmark as a class method!
        pass  # Not used, we'll re-render inline or the user can just close/open the accordion.

    def _save_current_as_bookmark(self, frame):
        from tkinter import simpledialog, messagebox

        name = simpledialog.askstring(
            "Save Bookmark",
            "Enter a name for this configuration:",
            parent=self,
        )
        if not name or not name.strip():
            return
        name = name.strip()
        import json, sqlite3

        data = {k: v.get() for k, v in self.vars.items()}
        data["template"] = self._selected_tpl.get()
        json_data = json.dumps(data)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO label_bookmarks (name, saved_at, data) VALUES (?, datetime('now', 'localtime'), ?)",
                (name, json_data),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f'Bookmark "{name}" saved successfully!')
            # Re-render accordion
            for w in frame.winfo_children():
                w.destroy()
            self._render_bookmarks_in_frame(frame)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bookmark: {e}")

    def _delete_bookmark(self, row_id, frame):
        from tkinter import messagebox

        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this bookmark?",
            parent=self,
        ):
            import sqlite3

            try:
                conn = sqlite3.connect(DB_PATH)
                row = conn.execute(
                    "SELECT data FROM label_bookmarks WHERE id=?", (row_id,)
                ).fetchone()
                if row:
                    import json

                    try:
                        data = json.loads(row[0])
                        cust_name = data.get("customer_name")
                        if cust_name:
                            conn.execute(
                                "DELETE FROM customer_bookmarks WHERE customer_name=?",
                                (cust_name,),
                            )
                    except:
                        pass
                conn.execute("DELETE FROM label_bookmarks WHERE id=?", (row_id,))
                conn.commit()
                conn.close()
                self._update_customer_star()
                for w in frame.winfo_children():
                    w.destroy()
                self._render_bookmarks_in_frame(frame)
            except Exception as e:
                print("Error deleting bookmark:", e)

    def _load_bookmark(self, row_id):
        import sqlite3, json

        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT data FROM label_bookmarks WHERE id=?", (row_id,)
            ).fetchone()
            conn.close()
            if row:
                data = json.loads(row[0])

                # Always keep document URLs empty when loading bookmarks
                self.vars["coa_url"].set("")
                self.vars["spec_url"].set("")

                for k, v in data.items():
                    if k in self.vars:
                        if k in ("coa_url", "spec_url"):
                            continue
                        self.vars[k].set(v)
                if "template" in data:
                    self._selected_tpl.set(data["template"])
                self._build_form()
                self._on_change_debounced()
        except Exception as e:
            print("Error loading bookmark:", e)

    def _render_bookmarks_in_frame(self, frame):
        import sqlite3

        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute(
                "SELECT id, name, saved_at FROM label_bookmarks ORDER BY name ASC"
            ).fetchall()
            conn.close()
            if not rows:
                ctk.CTkLabel(
                    frame,
                    text="No bookmarks saved.",
                    text_color="#888",
                    font=ctk.CTkFont(size=12),
                ).pack(pady=10)
                return
            for row in rows:
                row_id, name, saved_at = row

                row_frame = ctk.CTkFrame(frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=1)

                btn = ctk.CTkButton(
                    row_frame,
                    text="☆ " + name,
                    anchor="w",
                    fg_color="transparent",
                    text_color="#DDDDDD",
                    hover_color="#333333",
                    height=28,
                    font=ctk.CTkFont(size=12),
                    command=lambda r=row_id: self._load_bookmark(r),
                )
                btn.pack(side="left", fill="x", expand=True)

                del_btn = ctk.CTkButton(
                    row_frame,
                    text="✕",
                    width=28,
                    height=28,
                    fg_color="transparent",
                    text_color="#ef4444",
                    hover_color="#333333",
                    command=lambda r=row_id: self._delete_bookmark(r, frame),
                )
                del_btn.pack(side="right")
        except Exception as e:
            ctk.CTkLabel(frame, text=f"Error: {e}", text_color="red").pack()

    def open_batch_history_window(self):
        if hasattr(self, "batch_win") and self.batch_win.winfo_exists():
            self.batch_win.deiconify()
            self.batch_win.lift()
            self._refresh_batch_history_panel()
            return

        self.batch_win = ctk.CTkToplevel(self)
        self.batch_win.title("Batch History")
        self.batch_win.geometry("500x700")
        self.batch_win.attributes("-topmost", True)
        self.batch_win.after(
            200,
            lambda: self.batch_win.iconbitmap(
                os.path.join(ASSET_DIR, "app_icon_logo.ico")
            ),
        )

        lbl = ctk.CTkLabel(
            self.batch_win,
            text="All Batches",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        lbl.pack(pady=10)

        self.batch_list_frame = ctk.CTkScrollableFrame(self.batch_win)
        self.batch_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._refresh_batch_history_panel()

        def on_close():
            self.batch_win.withdraw()

        self.batch_win.protocol("WM_DELETE_WINDOW", on_close)

    def _refresh_batch_history_panel(self, *_):
        if not hasattr(self, "batch_list_frame"):
            return
        for w in self.batch_list_frame.winfo_children():
            w.destroy()

        import sqlite3

        try:
            conn = sqlite3.connect(DB_PATH)
            batches = conn.execute(
                "SELECT DISTINCT json_extract(data, '$.batch') FROM label_history ORDER BY 1 ASC"
            ).fetchall()
            batch_list = []
            if batches:
                for b in batches:
                    name = b[0]
                    if not name or str(name).strip() == "":
                        if "Unknown" not in batch_list:
                            batch_list.append("Unknown")
                    else:
                        if str(name).strip() not in batch_list:
                            batch_list.append(str(name).strip())

            if not batch_list:
                ctk.CTkLabel(
                    self.batch_list_frame,
                    text="No batches found in history",
                    text_color="#777777",
                ).pack(anchor="w", padx=5, pady=4)
                return

            def _load_batch(b_name):
                try:
                    conn2 = sqlite3.connect(DB_PATH)
                    if b_name == "Unknown":
                        row = conn2.execute(
                            "SELECT id FROM label_history WHERE json_extract(data, '$.batch') IS NULL OR json_extract(data, '$.batch') = '' ORDER BY saved_at DESC LIMIT 1"
                        ).fetchone()
                    else:
                        row = conn2.execute(
                            "SELECT id FROM label_history WHERE json_extract(data, '$.batch') = ? ORDER BY saved_at DESC LIMIT 1",
                            (b_name,),
                        ).fetchone()
                    conn2.close()
                    if row:
                        self._load_from_history(row[0])
                        self.batch_win.withdraw()
                except Exception as e:
                    print("Error loading batch:", e)

            for batch_name in batch_list:
                btn = ctk.CTkButton(
                    self.batch_list_frame,
                    text="📦 " + batch_name,
                    anchor="w",
                    fg_color="#2B2B2B",
                    text_color="#E0E0E0",
                    hover_color="#333333",
                    height=36,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    command=lambda b=batch_name: _load_batch(b),
                )
                btn.pack(fill="x", pady=2)

        except Exception as e:
            print("Error loading batch history:", e)

    def open_customer_history_window(self):
        if hasattr(self, "customer_win") and self.customer_win.winfo_exists():
            self.customer_win.deiconify()
            self.customer_win.lift()
            self._refresh_customer_history_panel()
            return

        self.customer_win = ctk.CTkToplevel(self)
        self.customer_win.title("Customer History")
        self.customer_win.geometry("500x700")
        self.customer_win.attributes("-topmost", True)
        self.customer_win.after(
            200,
            lambda: self.customer_win.iconbitmap(
                os.path.join(ASSET_DIR, "app_icon_logo.ico")
            ),
        )

        lbl = ctk.CTkLabel(
            self.customer_win,
            text="All Customers",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        lbl.pack(pady=10)

        self.customer_list_frame = ctk.CTkScrollableFrame(self.customer_win)
        self.customer_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._refresh_customer_history_panel()

        def on_close():
            self.customer_win.withdraw()

        self.customer_win.protocol("WM_DELETE_WINDOW", on_close)

    def _refresh_customer_history_panel(self, *_):
        if not hasattr(self, "customer_list_frame"):
            return
        for w in self.customer_list_frame.winfo_children():
            w.destroy()

        import sqlite3

        try:
            conn = sqlite3.connect(DB_PATH)
            # Get distinct customers
            customers = conn.execute(
                "SELECT DISTINCT json_extract(data, '$.customer_name') FROM label_history ORDER BY 1 ASC"
            ).fetchall()

            customer_list = []
            if customers:
                for c in customers:
                    name = c[0]
                    if not name or str(name).strip() == "":
                        if "Unknown" not in customer_list:
                            customer_list.append("Unknown")
                    else:
                        if str(name).strip() not in customer_list:
                            customer_list.append(str(name).strip())

            if not customer_list:
                ctk.CTkLabel(
                    self.customer_list_frame,
                    text="No customers found in history",
                    text_color="#777777",
                ).pack(anchor="w", padx=5, pady=4)
                return

            def _load_customer(c_name):
                try:
                    conn2 = sqlite3.connect(DB_PATH)
                    # First try to load from customer_bookmarks data
                    conn2.execute(
                        "SELECT data FROM customer_bookmarks WHERE customer_name=?",
                        (c_name,),
                    )
                    cb_row = conn2.fetchone()
                    if cb_row and cb_row[0]:
                        import json

                        data = json.loads(cb_row[0])
                        for k, v in data.items():
                            if k in self.vars:
                                self.vars[k].set(v)
                        if "template" in data:
                            self._selected_tpl.set(data["template"])
                        self._build_form()
                        self._on_change_debounced()
                        self.customer_win.withdraw()
                        conn2.close()
                        return

                    # Fallback to history
                    if c_name == "Unknown":
                        row = conn2.execute(
                            "SELECT id FROM label_history WHERE json_extract(data, '$.customer_name') IS NULL OR json_extract(data, '$.customer_name') = '' ORDER BY saved_at DESC LIMIT 1"
                        ).fetchone()
                    else:
                        row = conn2.execute(
                            "SELECT id FROM label_history WHERE json_extract(data, '$.customer_name') = ? ORDER BY saved_at DESC LIMIT 1",
                            (c_name,),
                        ).fetchone()
                    conn2.close()
                    if row:
                        self._load_from_history(row[0])
                        self.customer_win.withdraw()
                except Exception as e:
                    print("Error loading customer:", e)

            for cust_name in customer_list:
                btn = ctk.CTkButton(
                    self.customer_list_frame,
                    text="🏢 " + cust_name,
                    anchor="w",
                    fg_color="#2B2B2B",
                    text_color="#E0E0E0",
                    hover_color="#333333",
                    height=36,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    command=lambda c=cust_name: _load_customer(c),
                )
                btn.pack(fill="x", pady=2)

        except Exception as e:
            print("Error loading customer history:", e)

    def open_settings_window(self):
        if hasattr(self, "settings_win") and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return
        self.settings_win = ctk.CTkToplevel(self)
        self.settings_win.title("Settings")
        self.settings_win.geometry("520x620")
        self.settings_win.attributes("-topmost", True)
        self.settings_win.after(
            200,
            lambda: self.settings_win.iconbitmap(
                os.path.join(ASSET_DIR, "app_icon_logo.ico")
            ),
        )

        scroll = ctk.CTkScrollableFrame(self.settings_win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text="⚙️ App Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(10, 20), anchor="w", padx=10)

        # ---- NETWORK DIRECTORY ----
        ctk.CTkLabel(
            scroll,
            text="Shared Network Directory:",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(fill="x", padx=10, pady=(0, 4))
        dir_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        dir_frame.pack(fill="x", padx=10, pady=(0, 15))
        self.network_dir_var = ctk.StringVar(
            value=NETWORK_DIR if NETWORK_DIR != BASE_DIR else ""
        )
        entry = ctk.CTkEntry(
            dir_frame,
            textvariable=self.network_dir_var,
            placeholder_text="Leave empty to use app folder",
            placeholder_text_color="#888888",
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def browse():
            from tkinter import filedialog

            path = filedialog.askdirectory(
                parent=self.settings_win, title="Select Public Network Folder"
            )
            if path:
                self.network_dir_var.set(path)

        ctk.CTkButton(dir_frame, text="Browse...", width=80, command=browse).pack(
            side="right"
        )

        # ---- FTP SETTINGS ----
        ctk.CTkLabel(
            scroll,
            text="FTP / Document Upload Settings",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkLabel(
            scroll,
            text="Used for uploading COA & Specification PDFs to your website.",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w",
        ).pack(fill="x", padx=10, pady=(0, 8))

        def make_ftp_field(label_text, default_val, show=""):
            ctk.CTkLabel(
                scroll, text=label_text, anchor="w", font=ctk.CTkFont(size=12)
            ).pack(fill="x", padx=10, pady=(4, 0))
            var = ctk.StringVar(value=default_val)
            e = ctk.CTkEntry(
                scroll,
                textvariable=var,
                show=show,
                height=34,
                fg_color="#2a2a2a",
                border_color="#3a3a3a",
                placeholder_text_color="#888888",
            )
            e.pack(fill="x", padx=10, pady=(2, 6))
            return var

        self.ftp_host_var = make_ftp_field(
            "FTP Host (e.g. ftp.biomedingredients.com):", FTP_HOST
        )
        self.ftp_user_var = make_ftp_field("FTP Username:", FTP_USER)
        self.ftp_pass_var = make_ftp_field("FTP Password:", FTP_PASS, show="•")
        self.ftp_dir_var = make_ftp_field("Upload Folder on Server:", FTP_UPLOAD_DIR)
        self.ftp_url_var = make_ftp_field("Public URL Base:", FTP_PUBLIC_URL)

        def test_ftp():
            import ftplib
            from tkinter import messagebox

            try:
                ftp = ftplib.FTP()
                ftp.connect(self.ftp_host_var.get().strip(), 21, timeout=10)
                ftp.login(
                    self.ftp_user_var.get().strip(), self.ftp_pass_var.get().strip()
                )
                ftp.quit()
                messagebox.showinfo(
                    "FTP Test",
                    "✅ FTP connection successful!",
                    parent=self.settings_win,
                )
            except Exception as ex:
                messagebox.showerror(
                    "FTP Test Failed",
                    f"❌ Could not connect:\n{ex}",
                    parent=self.settings_win,
                )

        ctk.CTkButton(
            scroll,
            text="🔗 Test FTP Connection",
            fg_color="#1a4a6b",
            hover_color="#1a5a8b",
            font=ctk.CTkFont(size=12),
            height=36,
            command=test_ftp,
        ).pack(fill="x", padx=10, pady=(0, 15))

        def save():
            import json, os
            from tkinter import messagebox

            val = self.network_dir_var.get().strip()
            if val and not os.path.exists(val):
                messagebox.showerror(
                    "Error",
                    "The specified directory does not exist.",
                    parent=self.settings_win,
                )
                return
            cfg = {
                "network_dir": val,
                "ftp_host": self.ftp_host_var.get().strip(),
                "ftp_user": self.ftp_user_var.get().strip(),
                "ftp_pass": self.ftp_pass_var.get().strip(),
                "ftp_upload_dir": self.ftp_dir_var.get().strip(),
                "ftp_public_url": self.ftp_url_var.get().strip(),
            }
            with open(CONFIG_PATH, "w") as f:
                json.dump(cfg, f, indent=2)
            messagebox.showinfo(
                "Saved",
                "Settings saved! Restart the app to apply FTP settings.",
                parent=self.settings_win,
            )
            self.settings_win.destroy()

        ctk.CTkButton(
            scroll,
            text="💾 Save Settings",
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            command=save,
        ).pack(fill="x", padx=10, pady=(5, 20))

    def open_filter_window(self):
        if hasattr(self, "filter_win") and self.filter_win.winfo_exists():
            self.filter_win.deiconify()
            self.filter_win.lift()
            return

        self.filter_win = ctk.CTkToplevel(self)
        self.filter_win.title("Filter & Search Data")
        self.filter_win.geometry("900x650")
        self.filter_win.attributes("-topmost", True)
        self.filter_win.after(
            200,
            lambda: self.filter_win.iconbitmap(
                os.path.join(ASSET_DIR, "app_icon_logo.ico")
            ),
        )

        # Main layout: Left sidebar for filters, right area for results
        self.filter_win.grid_columnconfigure(1, weight=1)
        self.filter_win.grid_rowconfigure(0, weight=1)

        # Left Sidebar (Filters)
        filter_sidebar = ctk.CTkFrame(
            self.filter_win, width=280, corner_radius=0, fg_color="#1E1E1E"
        )
        filter_sidebar.grid(row=0, column=0, sticky="nsew")
        filter_sidebar.grid_propagate(False)

        ctk.CTkLabel(
            filter_sidebar,
            text="⚙️ Filter Options",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 15), padx=20, anchor="w")

        # Fetch unique values
        import sqlite3

        products = []
        customers = []
        batches = []
        dates = []
        mfg_dates = []
        drum_types = []
        try:
            conn = sqlite3.connect(DB_PATH)
            p_rows = conn.execute(
                "SELECT DISTINCT product FROM label_history WHERE product IS NOT NULL AND product != '' ORDER BY product"
            ).fetchall()
            products = [""] + [str(r[0]) for r in p_rows if r[0]]

            c_rows = conn.execute(
                "SELECT DISTINCT json_extract(data, '$.customer_name') FROM label_history WHERE json_extract(data, '$.customer_name') IS NOT NULL AND json_extract(data, '$.customer_name') != '' ORDER BY json_extract(data, '$.customer_name')"
            ).fetchall()
            customers = [""] + [str(r[0]) for r in c_rows if r[0]]

            b_rows = conn.execute(
                "SELECT DISTINCT batch FROM label_history WHERE batch IS NOT NULL AND batch != '' ORDER BY batch"
            ).fetchall()
            batches = [""] + [str(r[0]) for r in b_rows if r[0]]

            d_rows = conn.execute(
                "SELECT DISTINCT substr(saved_at, 1, 10) FROM label_history WHERE saved_at IS NOT NULL ORDER BY saved_at DESC"
            ).fetchall()
            dates = [""] + [str(r[0]) for r in d_rows if r[0]]

            mfg_rows = conn.execute(
                "SELECT DISTINCT json_extract(data, '$.mfg_date') FROM label_history WHERE json_extract(data, '$.mfg_date') IS NOT NULL AND json_extract(data, '$.mfg_date') != '' ORDER BY json_extract(data, '$.mfg_date')"
            ).fetchall()
            mfg_dates = [""] + [str(r[0]) for r in mfg_rows if r[0]]

            drum_rows = conn.execute(
                "SELECT DISTINCT json_extract(data, '$.drum_type') FROM label_history WHERE json_extract(data, '$.drum_type') IS NOT NULL AND json_extract(data, '$.drum_type') != '' ORDER BY json_extract(data, '$.drum_type')"
            ).fetchall()
            drum_types = [""] + [str(r[0]) for r in drum_rows if r[0]]

            conn.close()
        except:
            pass

        def trigger_filter(*args):
            run_filter()

        filters_scroll = ctk.CTkScrollableFrame(filter_sidebar, fg_color="transparent")
        filters_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # Helper for adding filters vertically
        def add_filter_ui(label_text, values_list):
            ctk.CTkLabel(
                filters_scroll,
                text=label_text,
                text_color="#AAAAAA",
                font=ctk.CTkFont(size=12, weight="bold"),
            ).pack(anchor="w", padx=10, pady=(10, 2))
            combo = ctk.CTkComboBox(
                filters_scroll,
                values=values_list,
                command=trigger_filter,
                height=35,
                corner_radius=6,
                border_color="#3A3A3A",
                button_color="#3A3A3A",
            )
            combo.set("")
            combo.pack(fill="x", padx=10, pady=(0, 5))
            combo.bind("<KeyRelease>", trigger_filter)
            return combo

        prod_entry = add_filter_ui("📦 Product", products)
        cust_entry = add_filter_ui("🏢 Customer", customers)
        batch_entry = add_filter_ui("🏷️ Batch", batches)
        date_entry = add_filter_ui("📅 Created Date", dates)

        def clear_filters():
            prod_entry.set("")
            cust_entry.set("")
            batch_entry.set("")
            date_entry.set("")
            run_filter()

        ctk.CTkButton(
            filter_sidebar,
            text="❌ Clear Filters",
            command=clear_filters,
            fg_color="#333333",
            hover_color="#444444",
            height=36,
            corner_radius=6,
        ).pack(fill="x", padx=20, pady=20)

        # Right Main Area (Results)
        results_container = ctk.CTkFrame(
            self.filter_win, fg_color="#121212", corner_radius=0
        )
        results_container.grid(row=0, column=1, sticky="nsew")

        # Results Header
        header_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.results_count_lbl = ctk.CTkLabel(
            header_frame,
            text="Found 0 matching labels",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.results_count_lbl.pack(side="left")

        def export_to_csv():
            if not hasattr(self, "current_filter_query"):
                return
            query, params = self.current_filter_query

            from tkinter import filedialog, messagebox
            import csv, sqlite3, json

            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Export Filtered Data",
            )
            if not filepath:
                return

            try:
                where_clause = query.split("FROM label_history")[1]
                export_query = (
                    "SELECT id, product, batch, saved_at, data FROM label_history"
                    + where_clause
                )

                conn = sqlite3.connect(DB_PATH)
                rows = conn.execute(export_query, params).fetchall()
                conn.close()

                parsed_rows = []
                json_keys = []
                for r in rows:
                    r_id, r_prod, r_batch, r_saved_at, r_data_json = r
                    r_data = {}
                    if r_data_json:
                        try:
                            r_data = json.loads(r_data_json)
                            for k in r_data.keys():
                                if k not in json_keys:
                                    json_keys.append(k)
                        except:
                            pass
                    parsed_rows.append((r_id, r_prod, r_batch, r_saved_at, r_data))

                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    headers = ["ID", "Product", "Batch", "Saved At"] + [
                        k.replace("_", " ").title() for k in json_keys
                    ]
                    writer.writerow(headers)

                    for r in parsed_rows:
                        r_id, r_prod, r_batch, r_saved_at, r_data = r

                        # Add a space before saved_at so Excel treats it as text and avoids the ###### error
                        formatted_saved_at = f" {r_saved_at}" if r_saved_at else ""

                        row_to_write = [r_id, r_prod, r_batch, formatted_saved_at]
                        for k in json_keys:
                            row_to_write.append(r_data.get(k, ""))

                        writer.writerow(row_to_write)

                messagebox.showinfo(
                    "Export Successful",
                    f"Successfully exported {len(rows)} records to CSV.",
                )
            except Exception as e:
                messagebox.showerror(
                    "Export Failed", f"Failed to export data:\n{str(e)}"
                )

        export_btn = ctk.CTkButton(
            header_frame,
            text="📥 Export CSV",
            width=120,
            height=32,
            command=export_to_csv,
            fg_color="#10B981",
            hover_color="#059669",
        )
        export_btn.pack(side="right")

        results_frame = ctk.CTkScrollableFrame(
            results_container, fg_color="transparent"
        )
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        def run_filter(*args):
            for widget in results_frame.winfo_children():
                widget.destroy()

            p_val = prod_entry.get().strip().lower()
            c_val = cust_entry.get().strip().lower()
            b_val = batch_entry.get().strip().lower()
            d_val = date_entry.get().strip().lower()

            query = "SELECT id, product, json_extract(data, '$.customer_name'), batch, saved_at, json_extract(data, '$.mfg_date'), json_extract(data, '$.drum_type') FROM label_history WHERE 1=1"
            params = []
            if p_val:
                query += " AND lower(product) LIKE ?"
                params.append(f"%{p_val}%")
            if c_val:
                query += " AND lower(json_extract(data, '$.customer_name')) LIKE ?"
                params.append(f"%{c_val}%")
            if b_val:
                query += " AND lower(batch) LIKE ?"
                params.append(f"%{b_val}%")
            if d_val:
                query += " AND lower(saved_at) LIKE ?"
                params.append(f"%{d_val}%")

            query += " ORDER BY saved_at DESC"

            self.current_filter_query = (query, params)

            import sqlite3

            try:
                conn = sqlite3.connect(DB_PATH)
                rows = conn.execute(query, params).fetchall()
                conn.close()

                self.results_count_lbl.configure(
                    text=f"Found {len(rows)} matching labels"
                )

                if not rows:
                    ctk.CTkLabel(
                        results_frame,
                        text="No matches found. Try adjusting your filters.",
                        text_color="#666666",
                        font=ctk.CTkFont(size=14),
                    ).pack(pady=40)
                else:
                    for row in rows:
                        r_id, prod, cust, batch, saved_at, mfg, drum = row

                        f = ctk.CTkFrame(
                            results_frame,
                            fg_color="#1E1E1E",
                            corner_radius=8,
                            border_width=1,
                            border_color="#333333",
                        )
                        f.pack(fill="x", pady=5, padx=5)

                        # Left side content
                        content_f = ctk.CTkFrame(f, fg_color="transparent")
                        content_f.pack(
                            side="left", fill="both", expand=True, padx=15, pady=12
                        )

                        title = str(prod) if prod else "Unknown Product"
                        ctk.CTkLabel(
                            content_f,
                            text=title,
                            anchor="w",
                            font=ctk.CTkFont(size=16, weight="bold"),
                            text_color="#E0E0E0",
                        ).pack(anchor="w")

                        # Details line
                        details = []
                        if cust:
                            details.append(f"🏢 {cust}")
                        if batch:
                            details.append(f"🏷️ {batch}")

                        details_str = "  |  ".join(details)
                        if not details_str:
                            details_str = "No additional details"

                        ctk.CTkLabel(
                            content_f,
                            text=details_str,
                            text_color="#888888",
                            font=ctk.CTkFont(size=12),
                        ).pack(anchor="w", pady=(3, 0))

                        # Date
                        ctk.CTkLabel(
                            content_f,
                            text=f"Saved: {saved_at}",
                            text_color="#666666",
                            font=ctk.CTkFont(size=11),
                        ).pack(anchor="w", pady=(2, 0))

                        # Right side button
                        def click_row(rid=r_id):
                            self._load_from_history(rid)
                            self.filter_win.withdraw()

                        btn = ctk.CTkButton(
                            f,
                            text="Load Label",
                            width=100,
                            height=36,
                            corner_radius=6,
                            font=ctk.CTkFont(weight="bold"),
                            fg_color="#2563EB",
                            hover_color="#1D4ED8",
                            command=lambda rid=r_id: click_row(rid),
                        )
                        btn.pack(side="right", padx=15, pady=15)

            except Exception as e:
                self.results_count_lbl.configure(text="Error querying database")
                ctk.CTkLabel(
                    results_frame, text=f"Error: {e}", text_color="#EF4444"
                ).pack(pady=20)

        run_filter()

        def on_close():
            self.filter_win.withdraw()

        self.filter_win.protocol("WM_DELETE_WINDOW", on_close)

    def open_recent_window(self):
        if hasattr(self, "recent_win") and self.recent_win.winfo_exists():
            self.recent_win.deiconify()
            self.recent_win.lift()
            self._refresh_history_panel()
            return

        self.recent_win = ctk.CTkToplevel(self)
        self.recent_win.title("Recent Labels")
        self.recent_win.geometry("500x700")
        self.recent_win.attributes("-topmost", True)
        self.recent_win.after(
            200,
            lambda: self.recent_win.iconbitmap(
                os.path.join(ASSET_DIR, "app_icon_logo.ico")
            ),
        )

        lbl = ctk.CTkLabel(
            self.recent_win,
            text="Generated Labels History",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        lbl.pack(pady=10)

        if hasattr(self, "history_month_combo") and self.history_month_combo:
            self.history_month_combo.destroy()
        if hasattr(self, "history_list_frame") and self.history_list_frame:
            self.history_list_frame.destroy()

        self.history_month_var = ctk.StringVar(value="Current Month")
        self.history_month_combo = ctk.CTkOptionMenu(
            self.recent_win,
            variable=self.history_month_var,
            values=["Current Month"],
            command=self._refresh_history_panel,
        )
        self.history_month_combo.pack(fill="x", padx=20, pady=(0, 10))

        self.history_list_frame = ctk.CTkScrollableFrame(self.recent_win)
        self.history_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._refresh_history_panel()

        def on_close():
            self.recent_win.withdraw()

        self.recent_win.protocol("WM_DELETE_WINDOW", on_close)


if __name__ == "__main__":
    app = LabelApp()
    app.mainloop()
