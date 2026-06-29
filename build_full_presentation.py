# -*- coding: utf-8 -*-
"""Build presentation.html = full KP (kp.html) + team slides; index.html = deploy root."""
import re
import subprocess
import sys
from pathlib import Path

from team_content import TEAM_CSS, build_team_slides_html, copy_almaty_samples, copy_team_assets

ROOT = Path(__file__).parent
INDEX = ROOT / "kp.html"
OUT = ROOT / "presentation.html"
DEPLOY_INDEX = ROOT / "index.html"
TEAM_MARK_START = "<!-- TEAM_START -->"
TEAM_MARK_END = "<!-- TEAM_END -->"
BUDGET_START = "<!-- BUDGET_START -->"

JS_PAUSE = """
  function pauseVideos(){
    document.querySelectorAll('video').forEach(v=>v.pause());
  }"""

JS_GO_PATCH_OLD = """  function go(i){
    cur=Math.max(0,Math.min(total-1,i));
    slides.forEach((s,j)=>s.classList.toggle('active',j===cur));
    dots.forEach((d,j)=>d.classList.toggle('on',j===cur));
    progress.style.width=(cur/(total-1)*100)+'%';
  }"""

JS_GO_PATCH_NEW = """  function go(i){
    cur=Math.max(0,Math.min(total-1,i));
    slides.forEach((s,j)=>s.classList.toggle('active',j===cur));
    dots.forEach((d,j)=>d.classList.toggle('on',j===cur));
    progress.style.width=(cur/(total-1)*100)+'%';
    pauseVideos();
  }"""

JS_CLICK_PATCH_OLD = """  document.getElementById('deck').addEventListener('click',e=>{
    if(e.target.closest('a,button'))return;"""

JS_CLICK_PATCH_NEW = """  document.getElementById('deck').addEventListener('click',e=>{
    if(e.target.closest('a,button,video'))return;"""


def refresh_budget_in_index():
    script = ROOT / "build_budget_html.py"
    if script.exists():
        subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)


def build():
    copy_team_assets()
    copy_almaty_samples()
    text = INDEX.read_text(encoding="utf-8")

    if TEAM_CSS.strip() not in text:
        text = text.replace("/* end slide */", TEAM_CSS + "\n/* end slide */", 1)

    team_block = build_team_slides_html(intro=True)

    if TEAM_MARK_START in text:
        text = re.sub(
            re.escape(TEAM_MARK_START) + r".*?" + re.escape(TEAM_MARK_END),
            team_block.strip(),
            text,
            flags=re.DOTALL,
        )
    else:
        text = text.replace(f"\n  {BUDGET_START}", f"\n{team_block}  {BUDGET_START}", 1)

    text = re.sub(
        r"<title>.*?</title>",
        "<title>Image & Video Production — КП · 8BIT-MEDIA</title>",
        text,
        count=1,
    )

    if "function pauseVideos" not in text:
        text = text.replace("  let cur=0;", JS_PAUSE + "\n  let cur=0;", 1)
        text = text.replace(JS_GO_PATCH_OLD, JS_GO_PATCH_NEW)
        text = text.replace(JS_CLICK_PATCH_OLD, JS_CLICK_PATCH_NEW)

    OUT.write_text(text, encoding="utf-8")
    DEPLOY_INDEX.write_text(text, encoding="utf-8")
    slides = text.count('<section class="slide')
    print(f"Built {OUT} — {slides} slides")
    print(f"Deployed {DEPLOY_INDEX} (GitHub Pages root)")


def main():
    refresh_budget_in_index()
    build()


if __name__ == "__main__":
    main()
