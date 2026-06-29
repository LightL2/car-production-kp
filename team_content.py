# -*- coding: utf-8 -*-
"""Shared team/portfolio slide content (from Anor PPTX, no Anor logos)."""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "pptx_extract"
ASSETS = ROOT / "assets" / "team"

COPY_MAP = {
    "image3.png": "egor-portrait.png",
    "image5.jpeg": "egor-reel-poster.jpg",
    "VAHN31fgG5o.mp4": "egor-reel.mp4",
    "image6.png": "pavel-portrait.png",
    "image7.png": "pavel-brands.png",
    "image8.jpeg": "pavel-reel-poster.jpg",
    "VAHN4BbB-As.mp4": "pavel-reel.mp4",
    "image9.png": "theo-portrait.png",
    "image10.png": "theo-brands.png",
    "image11.jpeg": "portfolio-01.jpg",
    "image12.jpeg": "portfolio-02.jpg",
    "image13.jpeg": "portfolio-03.jpg",
    "image14.jpeg": "portfolio-04.jpg",
    "image15.jpeg": "portfolio-05.jpg",
}

TEAM = [
    {
        "name": "Егор Иванов",
        "role": "Режиссёр-постановщик",
        "tag": "KZ",
        "bio": "Выпускник New York Film Academy, бывший документалист, а теперь — режиссёр рекламы и бренд-контента, который одинаково вдохновляется няшными детишками, контактными видами спорта и рёвом тяжёлой техники.",
        "portrait": "egor-portrait.png",
        "brands": "egor-brands.png",
        "reel": "egor-reel.mp4",
        "poster": "egor-reel-poster.jpg",
    },
    {
        "name": "Павел Янкевич",
        "role": "Оператор-постановщик",
        "tag": "KZ",
        "bio": "Путь Паши в кино начался в ГИТРе (Москва), где он пять лет осваивал операторское мастерство, параллельно набираясь практического опыта, ассистируя на съёмках короткометражек во ВГИКе, ГИТРе, Московской школе кино и на других студенческих и независимых площадках.",
        "portrait": "pavel-portrait.png",
        "brands": "pavel-brands.png",
        "reel": "pavel-reel.mp4",
        "poster": "pavel-reel-poster.jpg",
    },
    {
        "name": "Тео Госеллин",
        "role": "Фотограф",
        "tag": "FR",
        "bio": "Тео — фотограф из Парижа, Франция, работающий на высоком международном уровне. Его стиль отличается тонким чувством света, композиции и современной визуальной эстетикой, благодаря чему он сотрудничает с брендами и креативными проектами в Европе.",
        "portrait": "theo-portrait.png",
        "brands": "theo-brands.png",
    },
]

PORTFOLIO = [
    ("portfolio-01.jpg", "portfolio-02.jpg"),
    ("portfolio-04.jpg", "portfolio-05.jpg"),
]

# Экстерьер: сначала Тео, затем примеры Алматы · Интерьер: примеры Алматы
THEO_EXTERIOR = PORTFOLIO

BYD_REELS_TOP = [
    ("denza-35.mp4", "DENZA"),
    ("byd-cinematic.mp4", "BYD · cinematic"),
]
BYD_REEL_LAND = ("byd-4x3-final.mp4", "BYD · 4×3")
BYD_ASSETS = "assets/byd"

ALMATY_EXT = [
    ("1.jpg", "2.jpg"),
    ("3.jpg", "4.jpg"),
    ("5.jpg", "6.jpg"),
]
ALMATY_INT = [
    ("VM_13259.jpg", "VM_13310.jpg", "VM_12198.jpg"),
    ("VM_13327.jpg", "VM_13202.jpg"),
]
ALMATY_LOC = "Съёмка · г. Алматы, Казахстан"
INT_SRC = ROOT / "int"
EXT_SRC = ROOT / "ext"
ALMATY_ASSETS = ROOT / "assets" / "almaty"

TEAM_CSS = """
/* team & portfolio slides */
.team-grid{display:grid;grid-template-columns:1fr 1.05fr;gap:3vw;align-items:center;width:100%}
.team-role{font-family:var(--mono);font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-bottom:1.6vh}
.team-visual{display:flex;flex-direction:column;gap:1.5vh;align-items:center}
.team-portrait{width:100%;max-height:42vh;object-fit:contain;object-position:center bottom}
.team-brands{width:100%;max-height:20vh;object-fit:contain;opacity:.95}
.video-slide .body{justify-content:center;align-items:center}
.video-wrap{width:100%;max-width:960px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#000;box-shadow:0 20px 60px rgba(0,122,255,.15)}
.video-wrap video{display:block;width:100%;max-height:62vh;background:#000}
.video-cap{margin-top:1.2vh;font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;color:var(--grey);text-transform:uppercase;text-align:center}
.pf-grid{display:grid;gap:1.1vw;justify-content:center;justify-items:center;align-items:center;width:max-content;max-width:96vw;margin:0 auto}
.pf-grid.pf-2{grid-template-columns:repeat(2,max-content);gap:1.2vw}
.pf-grid.pf-3{grid-template-columns:repeat(3,max-content);gap:1.1vw}
.pf-grid.pf-1{grid-template-columns:max-content;max-width:96vw}
.slide.portfolio-slide > .body,.slide.sample-slide > .body{flex:1 1 0;min-height:0;width:100%;padding:0;overflow:visible}
.slide.portfolio-slide .pf-grid,.slide.sample-slide .pf-grid{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:4}
.gallery-section .body{justify-content:center;align-items:center}
.pf-cell{
  border:1px solid rgba(255,255,255,.1);
  border-radius:18px;
  overflow:hidden;
  background:linear-gradient(160deg,rgba(22,22,24,.95),rgba(8,8,10,.98));
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 28px 90px rgba(0,0,0,.62),0 0 0 1px rgba(0,122,255,.14),inset 0 1px 0 rgba(255,255,255,.07);
  transition:box-shadow .35s ease,transform .35s ease;
}
.pf-cell:hover{box-shadow:0 32px 100px rgba(0,0,0,.7),0 0 28px rgba(0,122,255,.18),0 0 0 1px rgba(0,122,255,.22),inset 0 1px 0 rgba(255,255,255,.09)}
.pf-grid.pf-1 .pf-cell{max-width:min(90vw,1320px);max-height:74vh;width:max-content}
.pf-grid.pf-1 .pf-cell img{max-width:min(90vw,1320px);max-height:74vh}
.pf-grid.pf-2 .pf-cell{max-width:min(56vw,1080px);max-height:76vh;width:max-content}
.pf-grid.pf-2 .pf-cell img{max-width:min(56vw,1080px);max-height:76vh}
.pf-grid.pf-3 .pf-cell{max-width:min(32vw,680px);max-height:64vh;width:max-content}
.pf-grid.pf-3 .pf-cell img{max-width:min(32vw,680px);max-height:64vh}
.pf-cell img{display:block;width:auto;height:auto;object-fit:contain;object-position:center}
.byd-slide .body{display:flex;justify-content:center;align-items:center;padding-top:0;padding-bottom:0}
.byd-grid{display:grid;grid-template-columns:0.9fr 1.1fr;gap:2.2vw;align-items:center;width:100%}
.byd-copy .lead{max-width:44ch}
.byd-videos{display:flex;flex-direction:column;align-items:center;gap:1.1vh;justify-content:center}
.byd-videos-row{display:flex;gap:1vw;align-items:flex-end;justify-content:center;flex-wrap:nowrap}
.byd-vid{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#111;display:inline-flex;flex-direction:column;align-items:center;max-width:100%}
.byd-vid video{display:block;width:auto;height:auto;max-width:100%;background:#000}
.byd-vid-port video{max-height:34vh}
.byd-vid-land video{max-height:19vh}
.byd-vid-cap{font-family:var(--mono);font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;color:var(--grey);text-align:center;padding:.75vh .6vw;border-top:1px solid var(--line);width:100%;align-self:stretch}
.sample-head{position:absolute;top:7.5vh;left:0;right:0;text-align:center;z-index:4;pointer-events:none}
.sample-loc{font-family:var(--mono);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
"""


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def copy_team_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in COPY_MAP.items():
        src = SRC / src_name
        if not src.exists():
            raise FileNotFoundError(f"Missing {src} — run _extract_pptx / unzip PPTX media first")
        shutil.copy2(src, ASSETS / dst_name)


def copy_almaty_samples():
    for kind, groups, src_dir in (
        ("ext", ALMATY_EXT, EXT_SRC),
        ("int", ALMATY_INT, INT_SRC),
    ):
        dst_dir = ALMATY_ASSETS / kind
        dst_dir.mkdir(parents=True, exist_ok=True)
        wanted = {img for group in groups for img in group}
        for group in groups:
            for img in group:
                src = src_dir / img
                if not src.exists():
                    raise FileNotFoundError(f"Missing {src}")
                shutil.copy2(src, dst_dir / img)
        for existing in dst_dir.iterdir():
            if existing.is_file() and existing.name not in wanted:
                existing.unlink()


def team_intro_slide():
    return """  <!-- TEAM INTRO -->
  <section class="slide mesh center-v compact">
    <div class="orb orb-2"></div>
    <div class="topbar"><span class="tag">КОМАНДА</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
      <div class="kicker">Международная production-сеть</div>
      <h2 class="title">Команда<br>проекта</h2>
      <p class="lead" style="margin-top:2vh">На&nbsp;крупных продакшн-проектах 8BIT-MEDIA работает с&nbsp;зарубежными партнёрами из&nbsp;международной production-сети&nbsp;— режиссёрами, операторами и&nbsp;фотографами, которых мы&nbsp;подключаем на&nbsp;масштабные съёмочные сессии.</p>
      <p class="lead muted" style="margin-top:1.8vh;max-width:54ch">Реализацию для BYD ведут специалисты с&nbsp;опытом automotive-проектов: мы&nbsp;понимаем, какой уровень качества требуется от&nbsp;материалов, и&nbsp;выстроили процесс под эти стандарты. Координацию съёмки и&nbsp;контроль сдачи обеспечивает 8BIT-MEDIA.</p>
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def team_member_slide(member):
    return f"""  <section class="slide mesh">
    <div class="topbar"><span class="tag">КОМАНДА · {esc(member['tag'])}</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
      <div class="team-grid">
        <div class="team-copy">
          <div class="kicker">Production team</div>
          <h2 class="title">{esc(member['name'])}</h2>
          <div class="team-role">{esc(member['role'])}</div>
          <p class="lead">{esc(member['bio'])}</p>
        </div>
        <div class="team-visual">
          <img class="team-portrait" src="assets/team/{member['portrait']}" alt="{esc(member['name'])}">
          <img class="team-brands" src="assets/team/{member['brands']}" alt="Бренды">
        </div>
      </div>
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def team_reel_slide(member):
    return f"""  <section class="slide video-slide mesh">
    <div class="topbar"><span class="tag">SHOWREEL · {esc(member['name'].split()[0].upper())}</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
      <div class="video-wrap">
        <video controls playsinline preload="metadata" poster="assets/team/{member['poster']}">
          <source src="assets/team/{member['reel']}" type="video/mp4">
        </video>
      </div>
      <div class="video-cap">{esc(member['name'])} · {esc(member['role'])}</div>
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def gallery_section_slide(title):
    return f"""  <section class="slide gallery-section mesh center-v">
    <div class="topbar"><span class="tag">ПОРТФОЛИО</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
      <h2 class="title">{esc(title)}</h2>
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def gallery_slide(source, images, page, kind):
    if source == "theo":
        tag = f"ПОРТФОЛИО · ТЕО · {kind.upper()} · {page}"
        cells = "".join(
            f'<div class="pf-cell"><img src="assets/team/{esc(img)}" alt=""></div>'
            for img in images
        )
        loc = ""
    else:
        folder = "ext" if kind == "ext" else "int"
        tag = f"ПРИМЕРЫ · {kind.upper()} · {page}"
        cells = "".join(
            f'<div class="pf-cell"><img src="assets/almaty/{folder}/{esc(img)}" alt=""></div>'
            for img in images
        )
        loc = f'      <div class="sample-head"><div class="sample-loc">{ALMATY_LOC}</div></div>\n'
    cols = f"pf-{len(images)}"
    grid = f'      <div class="pf-grid {cols}">{cells}</div>'
    return f"""  <section class="slide portfolio-slide sample-slide mesh center-v">
    <div class="topbar"><span class="tag">{tag}</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
{loc}{grid}
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def build_photo_gallery():
    parts = []
    parts.append(gallery_section_slide("Экстерьер"))
    for i, images in enumerate(THEO_EXTERIOR, 1):
        parts.append(gallery_slide("theo", images, f"{i:02d}", "ext"))
    for i, images in enumerate(ALMATY_EXT, 1):
        parts.append(gallery_slide("almaty", images, f"{i:02d}", "ext"))
    parts.append(gallery_section_slide("Интерьер"))
    for i, images in enumerate(ALMATY_INT, 1):
        parts.append(gallery_slide("almaty", images, f"{i:02d}", "int"))
    return parts


def byd_vid_cell(file, label, kind="port"):
    cls = "byd-vid-port" if kind == "port" else "byd-vid-land"
    return f"""        <div class="byd-vid {cls}">
          <video controls playsinline preload="metadata">
            <source src="{BYD_ASSETS}/{esc(file)}" type="video/mp4">
          </video>
          <div class="byd-vid-cap">{esc(label)}</div>
        </div>"""


def byd_experience_slide():
    top = "".join(byd_vid_cell(file, label, "port") for file, label in BYD_REELS_TOP)
    bottom = byd_vid_cell(BYD_REEL_LAND[0], BYD_REEL_LAND[1], "land")
    return f"""  <!-- BYD EXPERIENCE -->
  <section class="slide byd-slide mesh center-v compact">
    <div class="orb orb-2"></div>
    <div class="topbar"><span class="tag">BYD &amp; DENZA · ОПЫТ</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
      <div class="byd-grid">
        <div class="byd-copy">
          <div class="kicker">Reels · Social · 1,5 года</div>
          <h2 class="title" style="font-size:clamp(1.35rem,2.6vw,2.2rem)">Знаем продукт<br>бренда</h2>
          <p class="lead" style="margin-top:1.6vh">Почти полтора года 8BIT-MEDIA ведёт reels-продакшн для соцсетей BYD и&nbsp;DENZA в&nbsp;Узбекистане&nbsp;— регулярные съёмки, монтаж и&nbsp;публикация контента.</p>
          <p class="lead muted" style="margin-top:1.2vh">Мы знаем автомобили бренда на&nbsp;практике: ракурсы, свет, динамика кадра и&nbsp;высокие требования к&nbsp;качеству. Этот опыт&nbsp;— основа, на&nbsp;которой выстроено фото- и&nbsp;видеопроизводство для текущего проекта.</p>
        </div>
        <div class="byd-videos">
          <div class="byd-videos-row">
{top}          </div>
{bottom}        </div>
      </div>
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def build_team_slides_html(intro=True):
    parts = ["<!-- TEAM_START -->"]
    if intro:
        parts.append(team_intro_slide())
    for member in TEAM:
        parts.append(team_member_slide(member))
        if member.get("reel"):
            parts.append(team_reel_slide(member))
        if member["name"] == "Тео Госеллин":
            parts.extend(build_photo_gallery())
    parts.append(byd_experience_slide())
    parts.append("<!-- TEAM_END -->")
    return "\n".join(parts) + "\n"
