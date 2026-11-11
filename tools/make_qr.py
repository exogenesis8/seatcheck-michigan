#!/usr/bin/env python3
"""Make a slide-ready QR code for the student website.

    .venv/bin/pip install "qrcode[pil]"
    .venv/bin/python tools/make_qr.py [URL]

Writes handouts/SeatCheck-QR.png (with title and link) and handouts/SeatCheck-QR-plain.png (code only).
"""
import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

URL = sys.argv[1] if len(sys.argv) > 1 else "https://exogenesis8.github.io/seatcheck-michigan/"
OUT = Path(__file__).resolve().parent.parent / "handouts"
BRAND = (15, 92, 140)  # matches the app header
INK = (27, 36, 48)
FONT_DIR = Path("/System/Library/Fonts/Supplemental")


def font(name, size):
    try:
        return ImageFont.truetype(str(FONT_DIR / name), size)
    except OSError:
        return ImageFont.load_default(size)


def main():
    OUT.mkdir(exist_ok=True)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=24, border=4)
    qr.add_data(URL)
    qr.make(fit=True)
    code = qr.make_image(fill_color=INK, back_color="white").convert("RGB")
    code.save(OUT / "SeatCheck-QR-plain.png")

    w = max(code.width + 160, 1200)
    title_f, sub_f, url_f = font("Arial Bold.ttf", 88), font("Arial.ttf", 44), font("Arial Bold.ttf", 40)
    h = 60 + 100 + 60 + 40 + code.height + 40 + 60 + 60
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 14], fill=BRAND)

    def center(text, y, f, fill):
        tw = d.textlength(text, font=f)
        d.text(((w - tw) / 2, y), text, font=f, fill=fill)

    center("SeatCheck Michigan", 60, title_f, BRAND)
    center("Scan to check your child's car seat", 175, sub_f, INK)
    img.paste(code, ((w - code.width) // 2, 260))
    center(URL.replace("https://", "").rstrip("/"), 260 + code.height + 30, url_f, INK)
    img.save(OUT / "SeatCheck-QR.png")
    print(f"QR for {URL}\n  {OUT / 'SeatCheck-QR.png'} ({w}x{h})\n  {OUT / 'SeatCheck-QR-plain.png'}")


if __name__ == "__main__":
    main()
