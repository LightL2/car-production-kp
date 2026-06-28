# КП 8BIT-MEDIA · Image & Video Production — handoff для нового чата

Документ фиксирует, как устроено коммерческое предложение (КП) для **8BIT-MEDIA** по фото/видео продакшну автомобильного бренда. Используй его как стартовый контекст в новом чате.

---

## Главный deliverable

| Что | Путь |
|-----|------|
| **Презентация (основной файл)** | `e:\DENZA SITE\car-production-kp\index.html` — только КП (16 слайдов) |
| **Полная презентация (КП + команда)** | `e:\DENZA SITE\car-production-kp\presentation.html` — **основной файл для клиента** (25 слайдов) |
| Источник команды | `Anor Bureau x 8BIT x BYD Presentation.pptx` → без логотипов Anor |
| Логотип | `car-production-kp/assets/logo-8bit-white.png` |
| Фон фото-слайдов | `car-production-kp/assets/bg-photo.jpg` (BYD Song Plus) |
| Фон видео-слайдов | `car-production-kp/assets/bg-video.jpg` |

Формат: **интерактивный HTML-deck** (16 слайдов), не PPTX.  
Навигация: ← → / пробел, **F** — fullscreen, **P** — печать/PDF.

PPTX (`build_presentation.py`) — **устарел**, не использовать для клиента.

---

## Источники данных

| Источник | Путь | Назначение |
|----------|------|------------|
| RFP (ТЗ) | `e:\Cat\Общие\Image&Video Production RFP Requirements.xlsx` | Объёмы: 90 фото, 8–12 видео, QC, форматы |
| Смета (реальная) | `e:\Документы\Копия Смета 8Bit x BYD.xlsx` | 3 блока в одном листе |
| Дамп RFP | `car-production-kp/rfp_extract.txt` | Текст из RFP |
| Дамп сметы | `car-production-kp/estimate_extract.txt` | Текст из Excel |

### Три блока в Excel (колонки A–D, F–I, K–N)

| Блок | Смены | Subtotal (база) | Mark up 20% | Tax 2% | Overall USD |
|------|-------|-----------------|-------------|--------|-------------|
| **TVC** | 2 | $61 500 | $12 300 | $1 230 | $75 030 |
| **Photo Unit** | 3 | $45 200 | $9 040 | $904 | $55 144 |
| **Overview** | 2 | $46 950 | $9 390 | $939 | $57 279 |

**Клиентская группировка:**
- **Фото** = Photo Unit
- **Видео** = TVC + Overview

---

## Пайплайн пересборки сметы

```powershell
cd "e:\DENZA SITE\car-production-kp"
python parse_estimate.py      # Excel → estimate_data.json
python build_budget_html.py        # смета → index.html
python build_full_presentation.py  # index.html + команда → presentation.html
```

### Файлы скриптов

| Файл | Роль |
|------|------|
| `parse_estimate.py` | Парсит Excel, пишет `estimate_data.json`. Курс: `RATE = 12100` |
| `budget_adjust.py` | **Клиентская смета**: скрывает наценки, добавляет extras, НДС, сжимает строки |
| `build_budget_html.py` | Генерирует HTML слайдов сметы, патчит `index.html` |
| `estimate_data.json` | Сырые данные после парсинга (не показывать клиенту как есть) |

### Маркеры в index.html

```html
<!-- BUDGET_START -->
...
<!-- BUDGET_END -->
```

**Не редактировать слайды сметы вручную** в index.html — правки через скрипты, иначе перезапишется при `build_budget_html.py`.

---

## Логика клиентской сметы (`budget_adjust.py`)

### Константы (менять здесь)

```python
VAT_RATE = 0.12          # НДС — виден отдельной строкой по каждому блоку
PHOTO_EXTRA = 25_000       # Добавка к фото-блоку (размазать по строкам)
VIDEO_EXTRA_TOTAL = 40_000 # Добавка к видео (TVC + Overview пропорционально subtotal)
RATE = 12100               # в parse_estimate.py — UZS/USD (ЦБ)
```

### Что скрыто (не показывать отдельными строками)

- **Mark up 20%** из Excel — распределяется по статьям с повышенным весом на equipment, локации, логистику
- **Tax 2%** из Excel — тоже внутри строк

### Что видно клиенту

```
Subtotal  →  сумма статей
+ НДС 12% →  отдельная строка
ИТОГО     →  subtotal + НДС
```

### Итоговые суммы (USD, актуальные на момент handoff)

| Блок | Subtotal | НДС 12% | **Итого USD** | **UZS @ 12100** |
|------|----------|---------|---------------|-----------------|
| Фото | $80 144 | $9 617 | **$89 761** | 1 086 108 100 |
| TVC | $97 713 | $11 726 | **$109 439** | 1 324 211 900 |
| Overview | $74 596 | $8 952 | **$83 548** | 1 010 930 800 |
| Видео суммарно | $172 309 | $20 678 | **$192 987** | 2 335 142 700 |
| **Проект** | — | — | **$282 748** | **3 421 250 800** |

### Сжатие детализации для слайдов (`compress_for_slide`)

Detail-слайды: **8 строк** на блок (чтобы влезало на экран):

1. Pre-Production → одна строка «Producer group · pre-production»
2. Production → **4 подгруппы** (режиссёрская, админ, операторская, камера и свет)
3. Post-Production → одна строка
4. Прочее → Travel & logistics + Overtime & contingency

Первичное объединение мелких статей — словари `PHOTO_MERGE` / `VIDEO_MERGE` в `budget_adjust.py`.

---

## Структура презентации (16 слайдов)

1. Cover — логотип, «Фото и видео производство», pills (без описательного абзаца)
2. About 8BIT — генеральный подрядчик
3. Project — контекст, 90 фото, 8–12 видео, сдача 01.09.2026
4–5. Photo scope + QC (из RFP)
6–7. Video scope + QC (из RFP)
8. Process — 4 этапа
9. **Смета · Фото** (overview)
10. **Смета · Фото · Детали**
11. **Смета · Видео** (TVC + Overview колонки)
12. **Смета · TVC · Детали**
13. **Смета · Overview · Детали**
14. **Итого** — сводный бюджет
15. Условия — оплата 50/40/10, НДС 12%, курс 12 100
16. Contact — 8bit.uz, info@8bit.uz

---

## Дизайн-система 8BIT

```css
--bg: #000000
--accent: #007AFF
--display: 'Unbounded'
--sans: 'Inter'
--mono: 'JetBrains Mono'
```

- Только **8BIT-MEDIA** в клиентском КП
- **Не упоминать:** Anor Bureau, R/A Production, субподрядчиков, BYD по названию (если клиент не просит), Ташкент, launch/new model
- Cover: без курса/бюджета на обложке

### CSS-классы сметы

| Класс | Назначение |
|-------|------------|
| `budget-slide` | Вертикальное центрирование body на слайдах сметы |
| `budget-detail` | Компактная детализация |
| `ptable-2col` | Таблица «статья + USD» без третьей колонки (фикс слипания цифр) |
| `amt-pair` | USD + UZS в одной ячейке с gap (итог видео) |
| `row-note` | «включая НДС» под названием строки, не рядом с суммой |

### Известные UI-фиксы

- **Цифры слипались** USD/UZS в соседних колонках → двухколоночные footer-таблицы, `amt-pair`, `budget-meta` через flex + gap
- **Production не влезал** → `compress_for_slide()` + merge maps
- **Subtotal + текст** → не класть текст в колонку справа от суммы

---

## Что убрано по запросу клиента

- Disclaimer на итоговом слайде: ~~«Не включены: права на музыку beyond stock…»~~
- Описательный абзац на cover: ~~«90 профессиональных кадров, TVC…»~~
- Mark up 20% / Tax 2% как отдельные строки в КП

---

## RFP — ключевые цифры (слайды scope)

**Фото (90):** Exterior 20, Interior 20, Functions 15, Locations 25, KV 10 · ≥10000×7000px · RAW/TIFF/JPG

**Видео (8–12):** TVC 2–3, Exterior 2–3, Interior 2–3, Functions 2–3 · 4K UHD · 25/50fps · LOG · EN/RU/UZ subs

---

## Типичные задачи в новом чате

### Обновить смету из Excel
1. Положить новый файл или обновить путь в `parse_estimate.py` → `PATH`
2. Запустить оба скрипта (см. пайплайн)
3. Проверить итоги в консоли и на слайдах 9–14

### Изменить курс
- `parse_estimate.py` → `RATE = 12100`
- Пересобрать; UZS пересчитается в `prepare_client_budget()`

### Изменить добавки / НДС
- `budget_adjust.py` → `PHOTO_EXTRA`, `VIDEO_EXTRA_TOTAL`, `VAT_RATE`

### Править тексты слайдов (не смету)
- Редактировать `index.html` **вне** блока `BUDGET_START`…`BUDGET_END`

### Добавить слайд
- Вставить `<section class="slide">` в index.html
- Нумерация в footer обновляется автоматически (JS в конце файла)

---

## Контакты в КП

- Сайт: https://8bit.uz  
- Email: info@8bit.uz  
- Footer: **8BIT-MEDIA** · Digital-агентство полного цикла

---

## Чеклист перед отправкой клиенту

- [x] Нет упоминаний субподрядчика / Anor Bureau
- [x] Нет mark up 20% / tax 2% отдельными строками
- [x] НДС 12% есть на каждом блоке
- [x] USD и UZS не слипаются
- [x] Detail-слайды влезают по вертикали (центрированы через `budget-slide`)
- [x] Курс 12 100 UZS/USD везде一致
- [x] Cover без лишнего текста
- [x] F11 / PDF выглядит корректно (проверено @ 1280×720)

---

*Последнее обновление: июнь 2026 · проект DENZA SITE / car-production-kp*
