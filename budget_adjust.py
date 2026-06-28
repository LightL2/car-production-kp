# -*- coding: utf-8 -*-
"""Client-facing budget: hide markup/tax, add extras, show VAT 12%."""
from __future__ import annotations

import copy
from collections import defaultdict

VAT_RATE = 0.12
PHOTO_EXTRA = 25_000
VIDEO_EXTRA_TOTAL = 40_000

PHOTO_MERGE = {
    "1AD": "Art department · команда",
    "Постановщики": "Art department · команда",
    "Мастер": "Art department · команда",
    "Администратор площадки": "Административный персонал",
    "Администраторы": "Административный персонал",
    "Локации (Павилион)": "Локации · studio & location",
    "Локации (Экстерьер)": "Локации · studio & location",
    "АХЧ": "Кейтеринг и сервис площадки",
    "Сервис": "Кейтеринг и сервис площадки",
    "Ассистент фотографа": "Photo assist & digital",
    "ИИ специалист": "Photo assist & digital",
    "Гафер": "Gaffer & lighting crew",
    "Светоосветители": "Gaffer & lighting crew",
    "Объективы": "Camera package",
    "Плейбек": "Camera package",
    "Ретуш": "Post-production · retouch & grade",
    "Цветокоррекция": "Post-production · retouch & grade",
    "ИИ генерация": "Post-production · retouch & grade",
    "Авиаперелеты": "Travel & local logistics",
    "Транспорт": "Travel & local logistics",
}

VIDEO_MERGE = {
    "1AD": "Art department · команда",
    "Постановщики": "Art department · команда",
    "Администратор площадки": "Административный персонал",
    "Администраторы": "Административный персонал",
    "АХЧ": "Кейтеринг и сервис площадки",
    "Сервис": "Кейтеринг и сервис площадки",
    "Кастинг": "Casting & talent",
    "Каст": "Casting & talent",
    "Стилист": "HMU & wardrobe",
    "Проработка по костюму": "HMU & wardrobe",
    "Художник по гримму": "HMU & wardrobe",
    "Механик камеры": "Camera department",
    "1АС": "Camera department",
    "Гафер": "Gaffer & lighting crew",
    "Светоосветители": "Gaffer & lighting crew",
    "Звукорежиссер": "Sound department",
    "Камера": "Camera package",
    "Объективы": "Camera package",
    "Плейбек": "Camera package",
    "Монтаж": "Post-production",
    "Цветокоррекция": "Post-production",
    "Саунд-дизайн": "Post-production",
    "Авиаперелеты": "Travel & local logistics",
    "Транспорт": "Travel & local logistics",
}

EQUIPMENT_KEYS = ("объектив", "плейбек", "свет", "камер", "локаци", "локейшн")
LOGISTICS_KEYS = ("логист", "транспорт", "авиа", "переработ", "непредвид", "travel")
PREMIUM_KEYS = ("режисс", "оператор", "фотograf", "фотограф", "продюс", "креатив", "арт директор")


def round_clean(n: float) -> float:
    n = float(n)
    if n >= 1000:
        return round(n / 50) * 50
    if n >= 200:
        return round(n / 25) * 25
    if n >= 50:
        return round(n / 10) * 10
    return round(n / 5) * 5


def line_weight(line: dict) -> float:
    name = line["name"].lower()
    base = float(line["amount"])
    if any(k in name for k in EQUIPMENT_KEYS):
        return base * 1.28
    if any(k in name for k in LOGISTICS_KEYS):
        return base * 1.18
    if any(k in name for k in PREMIUM_KEYS):
        return base * 1.08
    return base


def distribute_hidden(lines: list[dict], markup: float, tax: float, extra: float) -> list[dict]:
    hidden = (markup or 0) + (tax or 0) + extra
    if hidden <= 0:
        return [copy.deepcopy(l) for l in lines]

    weights = [line_weight(l) for l in lines]
    total_w = sum(weights)
    out = []
    raw_adds = [hidden * (w / total_w) for w in weights]

    for line, add in zip(lines, raw_adds):
        row = copy.deepcopy(line)
        row["amount"] = round_clean(float(line["amount"]) + add)
        qty = row.get("qty")
        if isinstance(qty, (int, float)) and qty:
            row["rate"] = round_clean(row["amount"] / float(qty))
            row["amount"] = row["rate"] * float(qty)
        out.append(row)

    target = float(sum(l["amount"] for l in lines)) + hidden
    current = sum(l["amount"] for l in out)
    drift = round_clean(target - current)
    if drift:
        anchor = max(out, key=lambda x: x["amount"])
        anchor["amount"] = round_clean(anchor["amount"] + drift)
        qty = anchor.get("qty")
        if isinstance(qty, (int, float)) and qty:
            anchor["rate"] = round_clean(anchor["amount"] / float(qty))
            anchor["amount"] = anchor["rate"] * float(qty)
    return out


def _crew_qty(line: dict) -> float:
    qty = line.get("qty")
    rate = float(line.get("rate") or 0)
    if isinstance(qty, (int, float)) and qty > 1 and rate <= 600:
        return float(qty)
    return 1.0


def merge_lines(lines: list[dict], merge_map: dict) -> list[dict]:
    buckets: dict[tuple, dict] = {}
    order: list[tuple] = []

    for line in lines:
        merged_name = merge_map.get(line["name"], line["name"])
        key = (line["section"], line.get("subgroup") or "", merged_name)
        if key not in buckets:
            buckets[key] = {
                "section": line["section"],
                "subgroup": line.get("subgroup") or "",
                "name": merged_name,
                "qty": 0.0,
                "rate": 0.0,
                "amount": 0.0,
                "_crew": merged_name in merge_map.values(),
            }
            order.append(key)

        b = buckets[key]
        b["amount"] += float(line["amount"])
        if b["_crew"] and merged_name == merge_map.get(line["name"], line["name"]):
            b["qty"] += _crew_qty(line)
        elif not b["_crew"]:
            b["qty"] = max(b["qty"], float(line.get("qty") or 1))

    result = []
    for key in order:
        b = buckets[key]
        qty = b["qty"] if b["qty"] else 1.0
        amount = round_clean(b["amount"])
        rate = round_clean(amount / qty) if qty else amount
        amount = rate * qty if qty else amount
        result.append(
            {
                "section": b["section"],
                "subgroup": b["subgroup"],
                "name": b["name"],
                "qty": qty,
                "rate": rate,
                "amount": amount,
            }
        )

    drift = round_clean(sum(l["amount"] for l in lines) - sum(r["amount"] for r in result))
    if drift and result:
        result[-1]["amount"] = round_clean(result[-1]["amount"] + drift)
        qty = result[-1]["qty"]
        if qty:
            result[-1]["rate"] = round_clean(result[-1]["amount"] / qty)
            result[-1]["amount"] = result[-1]["rate"] * qty
    return result


def rollup_sections(lines: list[dict]) -> list[dict]:
    sections = []
    current = None
    for line in lines:
        sec = line["section"] or "Прочее"
        if current is None or current["section"] != sec:
            current = {"section": sec, "amount": 0.0, "items": []}
            sections.append(current)
        current["amount"] += float(line["amount"])
        current["items"].append(line)
    return sections


def _fix_total(lines: list[dict], target: float) -> list[dict]:
    target = round(target)
    current = round(sum(l["amount"] for l in lines))
    drift = target - current
    if drift and lines:
        anchor = max(lines, key=lambda x: x["amount"])
        anchor["amount"] = round(anchor["amount"] + drift)
        qty = anchor.get("qty")
        if isinstance(qty, (int, float)) and qty:
            anchor["rate"] = round_clean(anchor["amount"] / float(qty))
    return lines


def _is_production_section(section: str) -> bool:
    low = (section or "").lower()
    return "production" in low and "pre" not in low and "post" not in low


def _is_pre_section(section: str) -> bool:
    return "pre" in (section or "").lower()


def _is_post_section(section: str) -> bool:
    low = (section or "").lower()
    return "post" in low and "pre" not in low


def _pack(name: str, section: str, amount: float) -> dict:
    amount = round_clean(amount)
    return {
        "section": section,
        "subgroup": "",
        "name": name,
        "qty": 1,
        "rate": amount,
        "amount": amount,
    }


def compress_for_slide(lines: list[dict]) -> list[dict]:
    """Roll production into subgroup totals; keep other sections readable but compact."""
    total = round(sum(float(l["amount"]) for l in lines))
    result: list[dict] = []
    idx = 0

    while idx < len(lines):
        section = lines[idx]["section"]

        if _is_pre_section(section):
            chunk = []
            while idx < len(lines) and _is_pre_section(lines[idx]["section"]):
                chunk.append(lines[idx])
                idx += 1
            result.append(_pack("Producer group · pre-production", section, sum(l["amount"] for l in chunk)))
            continue

        if _is_production_section(section):
            chunk = []
            while idx < len(lines) and lines[idx]["section"] == section:
                chunk.append(lines[idx])
                idx += 1
            sg_totals: dict[str, float] = {}
            sg_order: list[str] = []
            for row in chunk:
                sg = row.get("subgroup") or "Production crew"
                if sg not in sg_totals:
                    sg_totals[sg] = 0.0
                    sg_order.append(sg)
                sg_totals[sg] += float(row["amount"])
            for sg in sg_order:
                result.append(_pack(sg, section, sg_totals[sg]))
            continue

        if _is_post_section(section):
            chunk = []
            while idx < len(lines) and _is_post_section(lines[idx]["section"]):
                chunk.append(lines[idx])
                idx += 1
            result.append(_pack("Post-production", section, sum(l["amount"] for l in chunk)))
            continue

        if "проч" in (section or "").lower():
            chunk = []
            while idx < len(lines) and "проч" in (lines[idx]["section"] or "").lower():
                chunk.append(lines[idx])
                idx += 1
            travel = 0.0
            other = 0.0
            for row in chunk:
                name = row["name"].lower()
                if any(k in name for k in ("travel", "логист", "транспорт", "авиа")):
                    travel += float(row["amount"])
                else:
                    other += float(row["amount"])
            if travel:
                result.append(_pack("Travel & logistics", section, travel))
            if other:
                result.append(_pack("Overtime & contingency", section, other))
            continue

        result.append(lines[idx])
        idx += 1

    return _fix_total(result, total)


def adjust_block(block: dict, extra_usd: float, merge_map: dict) -> dict:
    target_net = (
        float(block["subtotal"])
        + float(block.get("markup") or 0)
        + float(block.get("tax") or 0)
        + extra_usd
    )
    inflated = distribute_hidden(
        block["lines"],
        block.get("markup") or 0,
        block.get("tax") or 0,
        extra_usd,
    )
    merged = merge_lines(inflated, merge_map)
    merged = _fix_total(merged, target_net)
    compressed = compress_for_slide(merged)
    subtotal = round(sum(l["amount"] for l in compressed))
    vat = round(subtotal * VAT_RATE)
    overall = subtotal + vat

    out = copy.deepcopy(block)
    out["lines"] = compressed
    out["sections"] = rollup_sections(compressed)
    out["subtotal"] = subtotal
    out["vat"] = vat
    out["overall_usd"] = overall
    out["overall_uzs"] = overall  # multiplied by rate later
    out.pop("markup", None)
    out.pop("tax", None)
    return out


def prepare_client_budget(raw: dict) -> dict:
    rate = raw["rate"]
    tvc_sub = float(raw["video_tvc"]["subtotal"])
    ov_sub = float(raw["video_overview"]["subtotal"])
    split = tvc_sub + ov_sub
    tvc_extra = VIDEO_EXTRA_TOTAL * tvc_sub / split
    ov_extra = VIDEO_EXTRA_TOTAL * ov_sub / split

    photo = adjust_block(raw["photo"], PHOTO_EXTRA, PHOTO_MERGE)
    video_tvc = adjust_block(raw["video_tvc"], tvc_extra, VIDEO_MERGE)
    video_overview = adjust_block(raw["video_overview"], ov_extra, VIDEO_MERGE)

    photo_total = photo["overall_usd"]
    video_total = video_tvc["overall_usd"] + video_overview["overall_usd"]
    grand_total = photo_total + video_total

    return {
        "rate": rate,
        "photo": photo,
        "video_tvc": video_tvc,
        "video_overview": video_overview,
        "photo_total_usd": photo_total,
        "video_total_usd": video_total,
        "grand_total_usd": grand_total,
        "photo_total_uzs": photo_total * rate,
        "video_total_uzs": video_total * rate,
        "grand_total_uzs": grand_total * rate,
    }


if __name__ == "__main__":
    import json
    from pathlib import Path

    raw = json.loads((Path(__file__).parent / "estimate_data.json").read_text(encoding="utf-8"))
    d = prepare_client_budget(raw)
    print(f"Photo: ${d['photo_total_usd']:,.0f} (sub ${d['photo']['subtotal']:,.0f} + VAT ${d['photo']['vat']:,.0f})")
    print(f"Video: ${d['video_total_usd']:,.0f}")
    print(f"  TVC: ${d['video_tvc']['overall_usd']:,.0f}")
    print(f"  Overview: ${d['video_overview']['overall_usd']:,.0f}")
    print(f"Total: ${d['grand_total_usd']:,.0f}")
    print(f"Photo lines: {len(d['photo']['lines'])} (was {len(raw['photo']['lines'])})")
    print(f"TVC lines: {len(d['video_tvc']['lines'])} (was {len(raw['video_tvc']['lines'])})")
    print(f"Overview lines: {len(d['video_overview']['lines'])} (was {len(raw['video_overview']['lines'])})")
