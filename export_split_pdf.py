# -*- coding: utf-8 -*-
"""Export split photo/video HTML decks to high-quality image-based PDFs."""
from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import img2pdf
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent
OUT_DIR = ROOT / "split-kp" / "pdf"
DECKS = (
    ("photo", ROOT / "split-kp" / "photo" / "index.html", OUT_DIR / "KP-Photo-8BIT.pdf"),
    ("video", ROOT / "split-kp" / "video" / "index.html", OUT_DIR / "KP-Video-8BIT.pdf"),
)
VIEWPORT = {"width": 1280, "height": 720}
# 3× retina → 3840×2160 px per slide (max practical quality for 1280×720 layout)
DEVICE_SCALE = 3
SLIDE_WAIT_MS = 450
FONT_WAIT_MS = 1200


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


def start_server(port: int) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    server.daemon_threads = True

    def run():
        with server:
            server.serve_forever()

    threading.Thread(target=run, daemon=True).start()
    return server


def find_free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


SLIDE_JS = """
(i) => {
  const slides = [...document.querySelectorAll('.slide')];
  slides.forEach((s, j) => s.classList.toggle('active', j === i));
  document.querySelectorAll('video').forEach(v => { v.pause(); v.currentTime = 0; });
}
"""


async def export_deck(page_url: str, out_pdf: Path, tmp_dir: Path) -> int:
    tmp_dir.mkdir(parents=True, exist_ok=True)
    pngs: list[Path] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=DEVICE_SCALE,
            color_scheme="dark",
        )
        page = await context.new_page()
        await page.add_style_tag(
            content="#progress,#dots,#hint{display:none!important;}"
        )
        await page.goto(page_url, wait_until="networkidle", timeout=120_000)
        await page.wait_for_timeout(FONT_WAIT_MS)

        slide_count = await page.evaluate("document.querySelectorAll('.slide').length")
        for i in range(slide_count):
            await page.evaluate(SLIDE_JS, i)
            await page.wait_for_timeout(SLIDE_WAIT_MS)
            slide = page.locator(".slide.active")
            png = tmp_dir / f"slide_{i + 1:03d}.png"
            await slide.screenshot(path=str(png), type="png", animations="disabled")
            pngs.append(png)
            print(f"    slide {i + 1}/{slide_count}")

        await browser.close()

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with open(out_pdf, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in pngs]))

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return len(pngs)


async def main_async():
    # Ensure decks exist
    if not (ROOT / "split-kp" / "photo" / "index.html").exists():
        subprocess.run([sys.executable, str(ROOT / "build_split_presentations.py")], check=True, cwd=ROOT)

    port = find_free_port()
    os_cwd = Path.cwd()
    import os

    os.chdir(ROOT)
    server = start_server(port)
    time.sleep(0.4)

    try:
        for name, html_path, pdf_path in DECKS:
            if not html_path.exists():
                raise FileNotFoundError(html_path)
            rel = html_path.relative_to(ROOT).as_posix()
            url = f"http://127.0.0.1:{port}/{rel}"
            tmp = OUT_DIR / f"_tmp_{name}"
            print(f"Exporting {name} -> {pdf_path.name}")
            count = await export_deck(url, pdf_path, tmp)
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            print(f"  Done: {count} slides | {size_mb:.1f} MB | {DEVICE_SCALE}x ({VIEWPORT['width']*DEVICE_SCALE}x{VIEWPORT['height']*DEVICE_SCALE}px/slide)")
    finally:
        server.shutdown()
        os.chdir(os_cwd)


def main():
    asyncio.run(main_async())
    print(f"\nPDF files: {OUT_DIR}")


if __name__ == "__main__":
    main()
