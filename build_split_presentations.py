# -*- coding: utf-8 -*-
"""Build separate photo and video KP decks in split-kp/ from the full presentation."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from build_budget_html import (
    photo_unit_pricing_slide,
    video_overview_slide,
)
from team_content import TEAM_CSS, BYD_REEL_LAND_HOSTED, build_team_slides_html, copy_almaty_samples, copy_team_assets

from budget_adjust import prepare_client_budget

ROOT = Path(__file__).parent
SRC = ROOT / "presentation.html"
BASE_HTML = ROOT / "kp.html"
OUT_ROOT = ROOT / "split-kp"
PHOTO_OUT = OUT_ROOT / "photo" / "index.html"
VIDEO_OUT = OUT_ROOT / "video" / "index.html"
DEPLOY_ROOT = OUT_ROOT / "deploy"
PHOTO_DEPLOY = DEPLOY_ROOT / "photo"
VIDEO_DEPLOY = DEPLOY_ROOT / "video"

PHOTO_TEAM_FILES = (
    "theo-portrait.png",
    "theo-brands.png",
    "portfolio-01.jpg",
    "portfolio-02.jpg",
    "portfolio-04.jpg",
    "portfolio-05.jpg",
)
VIDEO_TEAM_FILES = (
    "egor-portrait.png",
    "egor-brands.png",
    "egor-reel-poster.jpg",
    "egor-reel.mp4",
    "pavel-portrait.png",
    "pavel-brands.png",
    "pavel-reel-poster.jpg",
    "pavel-reel.mp4",
)

SLIDE_RE = re.compile(r"<section class=\"slide.*?</section>", re.DOTALL)
TEAM_RE = re.compile(r"<!-- TEAM_START -->.*?<!-- TEAM_END -->", re.DOTALL)

SPLIT_CSS = """
/* unit pricing (photo KP) */
.unit-pricing-grid{display:grid;grid-template-columns:1fr 1fr;gap:2vw;width:100%;max-width:920px;margin:2.2vh auto 0}
.unit-price-card{border:1px solid var(--line);border-radius:16px;padding:2.2vh 1.8vw;background:rgba(0,0,0,.35);backdrop-filter:blur(12px)}
.unit-price-card.accent{border-color:rgba(0,122,255,.35);box-shadow:0 0 40px rgba(0,122,255,.12)}
.unit-num{font-family:var(--mono);font-size:.68rem;letter-spacing:.16em;color:var(--accent);margin-bottom:1vh}
.unit-lbl{font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--grey);margin-bottom:1.2vh}
.unit-amt{font-family:var(--display);font-size:clamp(1.6rem,3.2vw,2.6rem);font-weight:700;line-height:1;margin-bottom:.6vh}
.unit-sub{font-family:var(--mono);font-size:.68rem;color:var(--grey);margin-bottom:1.4vh}
.unit-list{font-size:.78rem;gap:.55vh}
.unit-total-bar{display:flex;justify-content:space-between;align-items:center;gap:2vw;margin-top:2vh;padding:1.4vh 1.6vw;border:1px solid var(--line);border-radius:12px;max-width:920px;margin-left:auto;margin-right:auto;font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase}
.unit-total-bar .val{color:var(--white);font-weight:500}
@media(max-width:900px){.unit-pricing-grid{grid-template-columns:1fr}}
"""

PHOTO_COVER = {
    "title": "Image & Video Production — Фото · 8BIT-MEDIA",
    "kicker": "Static Photography",
    "h1": 'Фото<br><span class="acc">производство</span>',
    "pills": (
        '<span class="pill">90 фото · 5 категорий</span>'
        '<span class="pill">≥10 000×7 000 px</span>'
        '<span class="pill">Сдача · 01.09.2026</span>'
    ),
}

VIDEO_COVER = {
    "title": "Image & Video Production — Видео · 8BIT-MEDIA",
    "kicker": "Dynamic Video Production",
    "h1": 'Видео<br><span class="acc">производство</span>',
    "pills": (
        '<span class="pill">4 ролика · 4K UHD</span>'
        '<span class="pill">TVC + Overview</span>'
        '<span class="pill">Сдача · 01.09.2026</span>'
    ),
}


def load_budget_data():
    raw = json.loads((ROOT / "estimate_data.json").read_text(encoding="utf-8"))
    return prepare_client_budget(raw)


def ensure_full_presentation():
    copy_team_assets()
    copy_almaty_samples()
    if not SRC.exists() or SRC.stat().st_mtime < max(
        (ROOT / "kp.html").stat().st_mtime,
        (ROOT / "team_content.py").stat().st_mtime,
    ):
        subprocess.run([sys.executable, str(ROOT / "build_full_presentation.py")], check=True, cwd=ROOT)


def team_slides_for(mode: str, landscape_src: str | None = None) -> list[str]:
    return SLIDE_RE.findall(build_team_slides_html(intro=True, mode=mode, landscape_src=landscape_src))


def parse_slides(html: str) -> list[str]:
    deck = re.search(r'<div id="deck">(.*)</div>\s*<div id="dots">', html, re.DOTALL)
    if not deck:
        raise SystemExit("Could not parse #deck from presentation.html")
    return SLIDE_RE.findall(deck.group(1))


def slide_kind(slide: str) -> str:
    if 'class="slide cover' in slide:
        return "cover"
    if "О КОМПАНИИ" in slide and "Генеральный" in slide:
        return "about"
    if "Задача" in slide and "ПРОЕКТ" in slide:
        return "project"
    if "ФОТО · ОБЪЁМ" in slide:
        return "photo_scope"
    if "ФОТО · СТАНДАРТЫ" in slide:
        return "photo_standards"
    if "ВИДЕО · ОБЪЁМ" in slide:
        return "video_scope"
    if "ВИДЕО · СТАНДАРТЫ" in slide:
        return "video_standards"
    if "ПОДХОД" in slide and "Как мы" in slide:
        return "process"
    if "end-slide" in slide:
        return "end"
    if "Сводная стоимость" in slide or "Бюджет<br>проекта" in slide:
        return "summary"
    if "СМЕТА · ФОТО · ДЕТАЛИ" in slide:
        return "photo_detail"
    if "СМЕТА · ФОТО" in slide and "ДЕТАЛИ" not in slide and "ТАРИФ" not in slide:
        return "photo_budget"
    if "СМЕТА · TVC" in slide:
        return "video_tvc_detail"
    if "СМЕТА · OVERVIEW" in slide:
        return "video_overview_detail"
    if "СМЕТА · ВИДЕО" in slide:
        return "video_budget"
    return "other"


def filter_team_slide(slide: str, mode: str) -> bool:
    """Legacy guard when parsing full deck — prefer team_slides_for()."""
    if "Егор Иванов" in slide or "SHOWREEL · ЕГОР" in slide or "SHOWREEL · EGOR" in slide:
        return mode == "video"
    if "Павел Янкевич" in slide or "SHOWREEL · ПАВEL" in slide or "SHOWREEL · ПАВЕЛ" in slide:
        return mode == "video"
    if "Тео Госеллин" in slide or "ПОРТФОЛИО · ТЕО" in slide:
        return mode == "photo"
    if "gallery-section" in slide or "portfolio-slide" in slide or "sample-slide" in slide:
        return mode == "photo"
    if "byd-slide" in slide or "BYD &amp; DENZA" in slide:
        return mode == "video"
    return True


def customize_cover(slide: str, cfg: dict) -> str:
    slide = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", slide, count=1, flags=re.DOTALL)
    slide = re.sub(
        r'<div class="kicker">.*?</div>\s*<h1 class="display">.*?</h1>\s*<div class="pills">.*?</div>',
        f'<div class="kicker">{cfg["kicker"]}</div>\n      <h1 class="display">{cfg["h1"]}</h1>\n      <div class="pills">\n        {cfg["pills"]}\n      </div>',
        slide,
        count=1,
        flags=re.DOTALL,
    )
    return slide


def customize_about(slide: str, mode: str) -> str:
    if mode == "photo":
        old = "Фото и видео под ключ: pre-production, съёмка, post и delivery. 90 кадров и 4 ролика по ТЗ проекта."
        new = "Фотопроизводство под ключ: pre-production, съёмка, post и delivery. 90 финальных кадров по ТЗ проекта."
    else:
        old = "Фото и видео под ключ: pre-production, съёмка, post и delivery. 90 кадров и 4 ролика по ТЗ проекта."
        new = "Видеопроизводство под ключ: pre-production, съёмка, post и delivery. 4 ролика 4K UHD по ТЗ проекта."
    return slide.replace(old, new)


def customize_project(slide: str, mode: str) -> str:
    if mode == "photo":
        slide = slide.replace(
            "требуется профессиональное фото- и видеопроизводство автомобиля.",
            "требуется профессиональное фотопроизводство автомобиля.",
        )
        slide = re.sub(
            r'<div class="card" style="padding:1\.5vh 1\.2vw"><div class="num">Видео</div>.*?</div>\s*',
            "",
            slide,
            count=1,
            flags=re.DOTALL,
        )
        slide = re.sub(
            r'<div class="stat"><div class="big">4K</div>.*?</div>\s*',
            "",
            slide,
            count=1,
            flags=re.DOTALL,
        )
        slide = re.sub(
            r'<div class="stat"><div class="big">4</div>.*?</div>\s*',
            "",
            slide,
            count=1,
            flags=re.DOTALL,
        )
    else:
        slide = slide.replace(
            "требуется профессиональное фото- и видеопроизводство автомобиля.",
            "требуется профессиональное видеопроизводство автомобиля.",
        )
        slide = re.sub(
            r'<div class="card" style="padding:1\.5vh 1\.2vw"><div class="num">Фото</div>.*?</div>\s*',
            "",
            slide,
            count=1,
            flags=re.DOTALL,
        )
        slide = re.sub(
            r'<div class="stat"><div class="big">90</div>.*?</div>\s*',
            "",
            slide,
            count=1,
            flags=re.DOTALL,
        )
    return slide


def customize_process(slide: str, mode: str) -> str:
    if mode == "photo":
        return slide.replace(
            "Студийная и location-съёмка. Отдельные команды под фото и видео",
            "Студийная и location-съёмка. Команда фотопроизводства",
        )
    return slide.replace(
        "Студийная и location-съёмка. Отдельные команды под фото и видео",
        "Студийная и location-съёмка. Команда видеопроизводства",
    )


def fix_asset_paths(html: str, prefix: str = "../../assets/") -> str:
    html = html.replace('src="assets/', f'src="{prefix}')
    html = html.replace("url('assets/", f"url('{prefix}")
    html = html.replace('<source src="assets/', f'<source src="{prefix}')
    html = html.replace('poster="assets/', f'poster="{prefix}')
    return html


def use_root_assets(html: str) -> str:
    html = html.replace("../../assets/", "assets/")
    html = html.replace("url('../../assets/", "url('assets/")
    return fix_asset_paths(html, prefix="assets/")


def inject_split_css(html: str) -> str:
    if SPLIT_CSS.strip() in html:
        return html
    return html.replace("/* end slide */", SPLIT_CSS + "\n/* end slide */", 1)


def assemble_html(slides: list[str], title: str, extra_css: bool = False, root_assets: bool = False) -> str:
    src_html = BASE_HTML.read_text(encoding="utf-8")
    if TEAM_CSS.strip() not in src_html:
        src_html = src_html.replace("/* end slide */", TEAM_CSS + "\n/* end slide */", 1)
    head = re.search(r"^(.*?<div id=\"deck\">)", src_html, re.DOTALL).group(1)
    tail = re.search(r"</div>\s*<div id=\"dots\">.*", src_html, re.DOTALL).group(0)
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, count=1)
    if extra_css:
        head = inject_split_css(head)
    body = "\n\n".join(slides)
    html = head + "\n" + body + "\n" + tail
    if root_assets:
        return use_root_assets(html)
    return fix_asset_paths(html)


def build_photo_deck(slides: list[str], budget: dict) -> str:
    by_kind: dict[str, list[str]] = {}
    for s in slides:
        by_kind.setdefault(slide_kind(s), []).append(s)

    ordered: list[str] = []
    for kind in ("cover", "about", "project", "photo_scope", "photo_standards", "process"):
        if kind in by_kind:
            ordered.append(by_kind[kind][0])

    ordered.extend(team_slides_for("photo"))

    ordered.extend(
        [
            photo_unit_pricing_slide(budget).strip(),
        ]
    )

    if "end" in by_kind:
        ordered.append(by_kind["end"][0])

    out = []
    for slide in ordered:
        kind = slide_kind(slide)
        if kind == "cover":
            slide = customize_cover(slide, PHOTO_COVER)
        elif kind == "about":
            slide = customize_about(slide, "photo")
        elif kind == "project":
            slide = customize_project(slide, "photo")
        elif kind == "process":
            slide = customize_process(slide, "photo")
        out.append(slide)

    return assemble_html(out, PHOTO_COVER["title"], extra_css=True)


def build_photo_deck_deploy(slides: list[str], budget: dict) -> str:
    html = build_photo_deck(slides, budget)
    return use_root_assets(html)


def build_video_deck_deploy(slides: list[str], budget: dict) -> str:
    html = build_video_deck(slides, budget, landscape_src=BYD_REEL_LAND_HOSTED)
    return use_root_assets(html)


def copy_tree(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_files(src_dir: Path, dst_dir: Path, names: tuple[str, ...]):
    dst_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = src_dir / name
        if src.exists():
            shutil.copy2(src, dst_dir / name)


def write_deploy_readme(path: Path, title: str, pages_url: str, *, video: bool = False):
    extra = ""
    if video:
        extra = (
            "\n## Видео BYD · 4×3 (отдельная загрузка)\n\n"
            "Файл `byd-4x3-final.mp4` (~170 MB) не входит в git. Загрузите на хостинг основного КП:\n\n"
            "```\n"
            "car-production-kp/assets/byd/byd-4x3-final.mp4\n"
            "```\n\n"
            f"URL: `{BYD_REEL_LAND_HOSTED}`\n"
        )
    path.write_text(
        f"# {title}\n\n"
        f"Клиентское КП 8BIT-MEDIA (GitHub Pages).\n\n"
        f"**Презентация:** {pages_url}\n\n"
        f"Сборка: `python deploy_split_github.py` из репозитория `LightL2/car-production-kp`.\n"
        f"{extra}",
        encoding="utf-8",
    )


def build_deploy_packages(photo_html: str, video_html: str):
    assets = ROOT / "assets"
    PHOTO_DEPLOY.mkdir(parents=True, exist_ok=True)
    VIDEO_DEPLOY.mkdir(parents=True, exist_ok=True)

    (PHOTO_DEPLOY / "index.html").write_text(photo_html, encoding="utf-8")
    (VIDEO_DEPLOY / "index.html").write_text(video_html, encoding="utf-8")

    photo_assets = PHOTO_DEPLOY / "assets"
    video_assets = VIDEO_DEPLOY / "assets"
    for folder in (photo_assets, video_assets):
        if folder.exists():
            shutil.rmtree(folder)
    photo_assets.mkdir(parents=True)
    video_assets.mkdir(parents=True)

    shutil.copy2(assets / "logo-8bit-white.png", photo_assets / "logo-8bit-white.png")
    shutil.copy2(assets / "bg-photo.jpg", photo_assets / "bg-photo.jpg")
    copy_files(assets / "team", photo_assets / "team", PHOTO_TEAM_FILES)
    copy_tree(assets / "almaty", photo_assets / "almaty")

    shutil.copy2(assets / "logo-8bit-white.png", video_assets / "logo-8bit-white.png")
    shutil.copy2(assets / "bg-video.jpg", video_assets / "bg-video.jpg")
    copy_files(assets / "team", video_assets / "team", VIDEO_TEAM_FILES)
    byd_src = assets / "byd"
    if byd_src.exists():
        video_assets.mkdir(parents=True, exist_ok=True)
        (video_assets / "byd").mkdir(parents=True, exist_ok=True)
        for name in ("denza-35.mp4", "byd-cinematic.mp4"):
            src = byd_src / name
            if src.exists():
                shutil.copy2(src, video_assets / "byd" / name)

    write_deploy_readme(
        PHOTO_DEPLOY / "README.md",
        "Car Production KP — Photo",
        "https://lightl2.github.io/car-production-kp-photo/",
    )
    write_deploy_readme(
        VIDEO_DEPLOY / "README.md",
        "Car Production KP — Video",
        "https://lightl2.github.io/car-production-kp-video/",
        video=True,
    )

    for stale in (PHOTO_DEPLOY / ".gitattributes", VIDEO_DEPLOY / ".gitattributes"):
        if stale.exists():
            stale.unlink()


def build_video_deck(slides: list[str], budget: dict, landscape_src: str | None = None) -> str:
    by_kind: dict[str, list[str]] = {}
    for s in slides:
        by_kind.setdefault(slide_kind(s), []).append(s)

    ordered: list[str] = []
    for kind in ("cover", "about", "project", "video_scope", "video_standards", "process"):
        if kind in by_kind:
            ordered.append(by_kind[kind][0])

    ordered.extend(team_slides_for("video", landscape_src=landscape_src))

    ordered.extend(
        [
            video_overview_slide(budget).strip(),
        ]
    )

    if "end" in by_kind:
        ordered.append(by_kind["end"][0])

    out = []
    for slide in ordered:
        kind = slide_kind(slide)
        if kind == "cover":
            slide = customize_cover(slide, VIDEO_COVER)
        elif kind == "about":
            slide = customize_about(slide, "video")
        elif kind == "project":
            slide = customize_project(slide, "video")
        elif kind == "process":
            slide = customize_process(slide, "video")
        out.append(slide)

    return assemble_html(out, VIDEO_COVER["title"])


def main():
    ensure_full_presentation()
    html = SRC.read_text(encoding="utf-8")
    slides = parse_slides(html)
    budget = load_budget_data()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    PHOTO_OUT.parent.mkdir(parents=True, exist_ok=True)
    VIDEO_OUT.parent.mkdir(parents=True, exist_ok=True)

    photo_html = build_photo_deck(slides, budget)
    video_html = build_video_deck(slides, budget)
    photo_deploy = build_photo_deck_deploy(slides, budget)
    video_deploy = build_video_deck_deploy(slides, budget)

    PHOTO_OUT.write_text(photo_html, encoding="utf-8")
    VIDEO_OUT.write_text(video_html, encoding="utf-8")
    build_deploy_packages(photo_deploy, video_deploy)

    u = budget["photo_total_usd"]
    from build_budget_html import photo_unit_rates

    rates = photo_unit_rates(budget)
    print(f"Photo deck: {PHOTO_OUT} — {photo_html.count('<section class=\"slide')} slides")
    print(f"  Unit: shoot {rates['shoot_usd']} + post {rates['process_usd']} = {rates['pair_usd']} / photo")
    print(f"Video deck: {VIDEO_OUT} — {video_html.count('<section class=\"slide')} slides")
    print(f"  Total video: ${budget['video_total_usd']:,.0f}".replace(",", " "))
    print(f"Deploy photo: {PHOTO_DEPLOY / 'index.html'} — {photo_deploy.count('<section class=\"slide')} slides")
    print(f"Deploy video: {VIDEO_DEPLOY / 'index.html'} — {video_deploy.count('<section class=\"slide')} slides")


if __name__ == "__main__":
    main()
