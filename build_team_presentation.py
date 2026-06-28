# -*- coding: utf-8 -*-
"""Standalone team-only deck (optional). Full KP: use build_full_presentation.py → presentation.html"""
from pathlib import Path

from team_content import TEAM_CSS, build_team_slides_html, copy_team_assets

OUT = Path(__file__).parent / "team.html"


def main():
    copy_team_assets()
    slides = build_team_slides_html(intro=True)
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Production Team · 8BIT-MEDIA</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Unbounded:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#000;--accent:#007AFF;--white:#fff;--grey:#A0A0A0;--line:rgba(255,255,255,.12);--display:'Unbounded',sans-serif;--sans:'Inter',sans-serif;--mono:'JetBrains Mono',monospace}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{height:100%;background:var(--bg);color:var(--white);font-family:var(--sans);overflow:hidden}}
#deck{{position:fixed;inset:0}} .slide{{position:absolute;inset:0;display:none;flex-direction:column;padding:4.5vh 5.5vw 0;background:var(--bg)}}
.slide.active{{display:flex}} .slide>.body{{flex:1;display:flex;flex-direction:column;justify-content:center}}
.topbar,.footer{{font-family:var(--mono);font-size:.7rem;color:var(--grey);text-transform:uppercase;border-color:var(--line)}}
.topbar{{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:1vh}}
.footer{{margin-top:auto;border-top:1px solid var(--line);padding:1.4vh 0 2.8vh;display:grid;grid-template-columns:auto 1fr auto}}
.kicker{{font-family:var(--mono);color:var(--accent);letter-spacing:.24em;text-transform:uppercase;margin-bottom:1.4vh}}
.title,.display{{font-family:var(--display);font-weight:800;text-transform:uppercase;line-height:1}}
.title{{font-size:clamp(1.6rem,3.2vw,2.8rem)}} .lead{{color:var(--grey);line-height:1.6;max-width:52ch}}
{TEAM_CSS}
</style>
</head>
<body>
<div id="deck">
{slides}
</div>
<script>
(function(){{
  const slides=[...document.querySelectorAll('.slide')];
  let cur=0;
  function pauseVideos(){{document.querySelectorAll('video').forEach(v=>v.pause());}}
  function go(i){{cur=Math.max(0,Math.min(slides.length-1,i));slides.forEach((s,j)=>s.classList.toggle('active',j===cur));pauseVideos();}}
  document.addEventListener('keydown',e=>{{if(['ArrowRight',' ','PageDown'].includes(e.key)){{e.preventDefault();go(cur+1);}}else if(['ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();go(cur-1);}}}});
  go(0);
}})();
</script>
</body>
</html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Built {OUT}")


if __name__ == "__main__":
    main()
