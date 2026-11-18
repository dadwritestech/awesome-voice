"""Record docs/demo.gif: type sloppy prose into the slop-score page and let the marks land.

Needs the page served locally (python -m http.server 8765 --directory docs),
Python Playwright with Chromium, and ffmpeg on PATH.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/"
OUT = Path(__file__).resolve().parent.parent / "docs" / "demo.gif"
TEXT = (
    "In today's fast-paced world, our tool is designed to seamlessly streamline "
    "your workflow. Whether you're a beginner or an expert, it's not just a CLI "
    "— it's a game-changer. Let's dive in!"
)


def main():
    tmp = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1200, "height": 720},
                                  record_video_dir=str(tmp), record_video_size={"width": 1200, "height": 720})
        page = ctx.new_page()
        page.goto(URL)
        page.wait_for_timeout(1200)
        page.click("#input")
        page.keyboard.type(TEXT, delay=28)
        page.wait_for_timeout(4000)
        video = page.video.path()
        ctx.close()
        browser.close()
    palette = tmp / "palette.png"
    vf = "fps=12,scale=900:-1:flags=lanczos"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vf", vf + ",palettegen=max_colors=96", str(palette)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", str(palette),
                    "-lavfi", vf + "[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4", str(OUT)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
