# -*- coding: utf-8 -*-
"""Generate budget slides HTML from estimate_data.json and patch index.html."""
import html
import json
import re
from collections import defaultdict
from pathlib import Path

from budget_adjust import prepare_client_budget

ROOT = Path(__file__).parent
DATA = ROOT / "estimate_data.json"
INDEX = ROOT / "kp.html"
MARK_START = "<!-- BUDGET_START -->"
MARK_END = "<!-- BUDGET_END -->"


def usd(n):
    return f"${n:,.0f}".replace(",", " ")


def uzs(n):
    return f"{n:,.0f}".replace(",", "\u202f")


def uzs_html(n, suffix=" UZS"):
    return f'<span class="nolink" x-apple-data-detectors="false">{uzs(n)}{html.escape(suffix)}</span>'


def esc(s):
    return html.escape(str(s))


def short_section(name):
    name = re.sub(r"^\d+\.\s*", "", name or "")
    low = name.lower()
    if "pre" in low:
        return "Pre-Production"
    if "post" in low:
        return "Post-Production"
    if "проч" in low:
        return "Прочее"
    if "production" in low or "съем" in low:
        return "Production"
    return name


def footer_rows(block, two_col=True):
    note = '<span class="row-note">включая НДС</span>'
    if two_col:
        return f"""
          <tr class="sub"><td class="name muted">Subtotal</td><td class="amt muted">{usd(block['subtotal'])}</td></tr>
          <tr class="sub"><td class="name muted">+ НДС 12%</td><td class="amt muted">{usd(block['vat'])}</td></tr>
          <tr class="total"><td class="name">ИТОГО {note}</td><td class="amt">{usd(block['overall_usd'])}</td></tr>"""
    return f"""
          <tr class="sub"><td class="name muted">Subtotal</td><td class="amt muted">{usd(block['subtotal'])}</td><td class="desc"></td></tr>
          <tr class="sub"><td class="name muted">+ НДС 12%</td><td class="amt muted">{usd(block['vat'])}</td><td class="desc"></td></tr>
          <tr class="total"><td class="name">ИТОГО {note}</td><td class="amt">{usd(block['overall_usd'])}</td><td class="desc"></td></tr>"""


def total_row_dual(label, usd_val, uzs_val):
    return f"""          <tr class="total">
            <td class="name">{esc(label)} <span class="row-note">включая НДС</span></td>
            <td class="totals">
              <div class="amt-pair">
                <span class="amt-usd">{usd(usd_val)}</span>
                <span class="amt-uzs">{uzs_html(uzs_val)}</span>
              </div>
            </td>
          </tr>"""


def budget_meta(shifts, total_usd, uzs_val=None, suffix=""):
    parts = [
        f"<span>{esc(str(shifts))} смены</span>",
        '<span class="sep">·</span>',
        f"<span>итого <strong>{usd(total_usd)}</strong></span>",
    ]
    if uzs_val is not None:
        parts += ['<span class="sep">·</span>', f"<span class=\"nolink\" x-apple-data-detectors=\"false\">{uzs(uzs_val)} UZS</span>"]
    if suffix:
        parts += ['<span class="sep">·</span>', f"<span>{esc(suffix)}</span>"]
    return f'<div class="budget-meta" x-apple-data-detectors="false">{"".join(parts)}</div>'


def overview_rows(block, expand_production=True, two_col=False):
    rows = []
    for sec in block["sections"]:
        label = short_section(sec["section"])
        if two_col:
            rows.append(
                f'<tr><td class="name">{esc(label)}</td><td class="amt">{usd(sec["amount"])}</td></tr>'
            )
        else:
            rows.append(
                f'<tr><td class="name">{esc(label)}</td><td class="amt">{usd(sec["amount"])}</td><td class="desc"></td></tr>'
            )
        if expand_production and "production" in sec["section"].lower() and "pre" not in sec["section"].lower() and "post" not in sec["section"].lower():
            sg = defaultdict(float)
            for it in sec["items"]:
                sg[it["subgroup"] or ""] += it["amount"]
            for name, amt in sg.items():
                if not name:
                    continue
                if two_col:
                    rows.append(
                        f'<tr class="sub"><td class="name muted">↳ {esc(name)}</td><td class="amt muted">{usd(amt)}</td></tr>'
                    )
                else:
                    rows.append(
                        f'<tr class="sub"><td class="name muted">↳ {esc(name)}</td><td class="amt muted">{usd(amt)}</td><td class="desc"></td></tr>'
                    )
        elif label == "Прочее":
            for it in sec["items"]:
                if two_col:
                    rows.append(
                        f'<tr class="sub"><td class="name muted">↳ {esc(it["name"])}</td><td class="amt muted">{usd(it["amount"])}</td></tr>'
                    )
                else:
                    rows.append(
                        f'<tr class="sub"><td class="name muted">↳ {esc(it["name"])}</td><td class="amt muted">{usd(it["amount"])}</td><td class="desc"></td></tr>'
                    )
    return "\n".join(rows)


def detail_table(lines):
    rows = []
    cur_sec = None
    cur_sg = None
    for line in lines:
        sec = short_section(line["section"])
        if sec != cur_sec:
            cur_sec = sec
            cur_sg = None
            rows.append(f'<tr class="sec"><td colspan="4" class="name">{esc(sec)}</td></tr>')
        sg = line.get("subgroup") or ""
        if sg and sg != cur_sg:
            cur_sg = sg
            rows.append(f'<tr class="sg"><td colspan="4" class="name muted">{esc(sg)}</td></tr>')
        qty = line["qty"]
        rate = line["rate"]
        qty_s = f"{qty:g}" if isinstance(qty, (int, float)) else esc(qty)
        rate_s = usd(rate) if isinstance(rate, (int, float)) else esc(rate)
        rows.append(
            f'<tr><td class="name">{esc(line["name"])}</td><td class="qty">{qty_s}</td><td class="rate">{rate_s}</td><td class="amt">{usd(line["amount"])}</td></tr>'
        )
    return "\n".join(rows)


def slide_shell(tag, title, kicker, body_inner, bg_class="", extra_class="compact"):
    bg = f'    <div class="slide-bg {bg_class}"></div>\n' if bg_class else ""
    orb = '    <div class="orb orb-2"></div>\n' if bg_class == "video" else ""
    mesh = " mesh" if bg_class else ""
    return f"""  <!-- {esc(kicker)} -->
  <section class="slide has-bg{mesh} {extra_class}">
{bg}{orb}    <div class="topbar"><span class="tag">{esc(tag)}</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
{body_inner}
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def photo_overview_slide(d):
    b = d["photo"]
    body = f"""      <div class="pricing-top">
        <div>
          <span class="tag-photo">Photo Unit</span>
          <h2 class="title" style="font-size:clamp(1.5rem,3vw,2.6rem)">Фотопроизводство</h2>
        </div>
        <div class="price-card" x-apple-data-detectors="false">
          <div class="plbl">Итого с налогами</div>
          <div class="pamt">{usd(b['overall_usd'])}</div>
          <div class="psub">{uzs_html(b['overall_usd'] * d['rate'])}</div>
          <div class="pvat">{b['shifts']} съёмочных дня · курс {d['rate']:,} UZS/USD</div>
        </div>
      </div>
      <table class="ptable ptable-2col">
        <thead><tr><th>Статья</th><th style="text-align:right">USD</th></tr></thead>
        <tbody>
{overview_rows(b, two_col=True)}
{footer_rows(b)}
        </tbody>
      </table>"""
    return slide_shell("СМЕТА · ФОТО", "", "PHOTO BUDGET", body, "photo", "compact budget-slide")


def photo_detail_slide(d):
    b = d["photo"]
    body = f"""      <div class="budget-head">
        <span class="tag-photo">Photo Unit · детализация</span>
        <h2 class="title" style="font-size:clamp(1.35rem,2.5vw,2.2rem)">Статьи расходов · фото</h2>
        {budget_meta(b['shifts'], b['overall_usd'], suffix='НДС включён')}
      </div>
      <table class="ptable ptable-dense">
        <thead><tr><th>Статья</th><th>Кол-во</th><th>Ставка</th><th style="text-align:right">USD</th></tr></thead>
        <tbody>
{detail_table(b['lines'])}
        </tbody>
      </table>
      <table class="ptable ptable-2col ptable-dense" style="margin-top:1vh">
        <tbody>
{footer_rows(b)}
        </tbody>
      </table>"""
    return slide_shell("СМЕТА · ФОТО · ДЕТАЛИ", "", "PHOTO DETAIL", body, "photo", "compact budget-detail budget-slide")


def video_overview_slide(d):
    tvc = d["video_tvc"]
    ov = d["video_overview"]
    vt = d["video_total_usd"]
    body = f"""      <div class="pricing-top">
        <div>
          <span class="tag-video">Video Production</span>
          <h2 class="title" style="font-size:clamp(1.5rem,3vw,2.6rem)">Видеопроизводство</h2>
        </div>
        <div class="price-card" x-apple-data-detectors="false">
          <div class="plbl">Итого с налогами</div>
          <div class="pamt">{usd(vt)}</div>
          <div class="psub">{uzs_html(vt * d['rate'])}</div>
          <div class="pvat">TVC {tvc['shifts']} + Overview {ov['shifts']} смены</div>
        </div>
      </div>
      <div class="budget-split">
        <div class="budget-block">
          <div class="block-title">TVC · главный ролик <span>{usd(tvc['overall_usd'])}</span></div>
          <table class="ptable ptable-dense ptable-2col">
            <thead><tr><th>Статья</th><th style="text-align:right">USD</th></tr></thead>
            <tbody>
{overview_rows(tvc, expand_production=False, two_col=True)}
            </tbody>
          </table>
        </div>
        <div class="budget-block">
          <div class="block-title">Overview · обзорные ролики <span>{usd(ov['overall_usd'])}</span></div>
          <table class="ptable ptable-dense ptable-2col">
            <thead><tr><th>Статья</th><th style="text-align:right">USD</th></tr></thead>
            <tbody>
{overview_rows(ov, expand_production=False, two_col=True)}
            </tbody>
          </table>
        </div>
      </div>
      <table class="ptable ptable-2col" style="margin-top:1.2vh">
        <tbody>
          <tr class="sub"><td class="name muted">Subtotal TVC + Overview</td><td class="amt muted">{usd(tvc['subtotal'] + ov['subtotal'])}</td></tr>
          <tr class="sub"><td class="name muted">+ НДС 12%</td><td class="amt muted">{usd(tvc['vat'] + ov['vat'])}</td></tr>
{total_row_dual('ИТОГО ВИДЕО', vt, vt * d['rate'])}
        </tbody>
      </table>"""
    return slide_shell("СМЕТА · ВИДЕО", "", "VIDEO BUDGET", body, "video", "compact budget-slide")


def video_detail_slide(d, key, label, tag):
    b = d[key]
    body = f"""      <div class="budget-head">
        <span class="tag-video">{label} · детализация</span>
        <h2 class="title" style="font-size:clamp(1.35rem,2.5vw,2.2rem)">Статьи расходов · {label.lower()}</h2>
        {budget_meta(b['shifts'], b['overall_usd'], b['overall_usd'] * d['rate'])}
      </div>
      <table class="ptable ptable-dense">
        <thead><tr><th>Статья</th><th>Кол-во</th><th>Ставка</th><th style="text-align:right">USD</th></tr></thead>
        <tbody>
{detail_table(b['lines'])}
        </tbody>
      </table>
      <table class="ptable ptable-2col ptable-dense" style="margin-top:1vh">
        <tbody>
{footer_rows(b)}
        </tbody>
      </table>"""
    return slide_shell(tag, "", f"VIDEO DETAIL {key}", body, "video", "compact budget-detail budget-slide")


def summary_slide(d):
    body = f"""      <div class="kicker">Сводная стоимость</div>
      <h2 class="title">Бюджет<br>проекта</h2>
      <div class="summary-hero">
        <div class="split-budget" style="margin-top:0">
          <div class="budget-col photo">
            <div class="bl">Фото · Photo Unit</div>
            <div class="bt">{usd(d['photo_total_usd'])}<span class="nolink" x-apple-data-detectors="false">{uzs(d['photo_total_uzs'])} UZS · {d['photo']['shifts']} смены</span></div>
            <ul class="blist muted" style="gap:.7vh">
              <li style="font-size:.82rem">Subtotal {usd(d['photo']['subtotal'])} + НДС {usd(d['photo']['vat'])}</li>
              <li style="font-size:.82rem">90 финальных кадров · 5 категорий</li>
            </ul>
          </div>
          <div class="budget-col video">
            <div class="bl" style="color:var(--white)">Видео · TVC + Overview</div>
            <div class="bt">{usd(d['video_total_usd'])}<span class="nolink" x-apple-data-detectors="false">{uzs(d['video_total_uzs'])} UZS · {d['video_tvc']['shifts']}+{d['video_overview']['shifts']} смены</span></div>
            <ul class="blist muted" style="gap:.7vh">
              <li style="font-size:.82rem">TVC {usd(d['video_tvc']['overall_usd'])} · Overview {usd(d['video_overview']['overall_usd'])}</li>
              <li style="font-size:.82rem">8–12 роликов · 4K UHD</li>
            </ul>
          </div>
        </div>
        <div class="total-block" x-apple-data-detectors="false">
          <div class="tlbl">Общая стоимость проекта</div>
          <div class="tamt">{usd(d['grand_total_usd'])}</div>
          <div class="tuzs">{uzs_html(d['grand_total_uzs'])}</div>
        </div>
      </div>
      <div class="note">Курс {d['rate']:,} UZS/USD (ЦБ). По каждому блоку начисляется НДС 12%, включён в итоговую стоимость.</div>"""
    return f"""  <!-- SUMMARY -->
  <section class="slide grid-bg mesh compact center-v budget-slide">
    <div class="orb orb-1"></div>
    <div class="topbar"><span class="tag">ИТОГО</span><img class="topbar-logo" src="assets/logo-8bit-white.png" alt=""></div>
    <div class="body">
{body}
    </div>
    <div class="footer"><div class="idx"></div><div class="brand"><b>8BIT-MEDIA</b></div><div class="footer-mark"></div></div>
  </section>
"""


def build():
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    d = prepare_client_budget(raw)
    parts = [
        MARK_START,
        photo_overview_slide(d),
        photo_detail_slide(d),
        video_overview_slide(d),
        video_detail_slide(d, "video_tvc", "TVC", "СМЕТА · TVC · ДЕТАЛИ"),
        video_detail_slide(d, "video_overview", "Overview", "СМЕТА · OVERVIEW · ДЕТАЛИ"),
        summary_slide(d),
        MARK_END,
    ]
    return "\n".join(parts) + "\n", d


def patch_index():
    html_block, d = build()
    text = INDEX.read_text(encoding="utf-8")
    if MARK_START not in text:
        raise SystemExit("Markers not found in kp.html — add BUDGET_START/BUDGET_END")
    pattern = re.compile(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), re.DOTALL)
    new_text = pattern.sub(html_block.strip(), text)
    INDEX.write_text(new_text, encoding="utf-8")
    slide_count = new_text.count('<section class="slide')
    print(f"Photo {usd(d['photo_total_usd'])} | Video {usd(d['video_total_usd'])} | Total {usd(d['grand_total_usd'])}")
    print(f"Patched {INDEX} — {slide_count} slides total")


if __name__ == "__main__":
    patch_index()
