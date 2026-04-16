import re
from pathlib import Path
from difflib import SequenceMatcher

file_done = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md")
file_offers = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса.md")

print("РАСШИРЕННАЯ ПРОВЕРКА: список Переделанных ↔ Офферы")
print("=" * 90)

if not file_done.exists():
    print(f"❌ Не найден файл: {file_done}")
    raise SystemExit

if not file_offers.exists():
    print(f"❌ Не найден файл: {file_offers}")
    raise SystemExit

text_done = file_done.read_text(encoding="utf-8")
text_offers = file_offers.read_text(encoding="utf-8")

items_done = [
    re.sub(r"^\d+\.\s*", "", x).strip()
    for x in re.findall(r"^\d+\..+", text_done, re.MULTILINE)
]

items_offers_raw = [
    x.strip()
    for x in re.findall(r"^##\s+(.+)$", text_offers, re.MULTILINE)
]

items_offers = []
for x in items_offers_raw:
    clean = re.sub(r"_Directus$", "", x, flags=re.IGNORECASE)
    clean = clean.replace("_", " ").strip()
    items_offers.append((x, clean))

def norm(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("ё", "е")
    s = s.replace("_", " ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"\bдля directus\b", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"\bdirectus\b", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-zа-я0-9]+", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

exact = []
fuzzy = []
missing = []
garbage = []

offer_norm_map = {}
for raw, clean in items_offers:
    offer_norm_map.setdefault(norm(clean), []).append((raw, clean))

for item in items_done:
    n = norm(item)

    if not n or n in {"твоя роль", "поля для заполнения", "все офферы готовые"}:
        garbage.append(item)
        continue

    if n in offer_norm_map:
        exact.append((item, offer_norm_map[n][0][0]))
        continue

    best_score = 0
    best_match = None
    for raw, clean in items_offers:
        score = sim(item, clean)
        if score > best_score:
            best_score = score
            best_match = raw

    if best_score >= 0.72:
        fuzzy.append((item, best_match, round(best_score, 3)))
    else:
        missing.append(item)

print(f"📄 Переделанных: {len(items_done)}")
print(f"📦 Офферов: {len(items_offers)}")
print(f"✅ Точные совпадения: {len(exact)}")
print(f"🔶 Похожие совпадения: {len(fuzzy)}")
print(f"❌ Реально не найдено: {len(missing)}")
print(f"🗑️ Мусор/служебное: {len(garbage)}")

print("\nПЕРВЫЕ 20 ТОЧНЫХ:")
for i, (a, b) in enumerate(exact[:20], 1):
    print(f"{i:2d}. {a} --> {b}")

print("\nПЕРВЫЕ 20 ПОХОЖИХ:")
for i, (a, b, s) in enumerate(fuzzy[:20], 1):
    print(f"{i:2d}. {a} --> {b}  ({s})")

print("\nРЕАЛЬНО НЕ НАЙДЕНО:")
for i, item in enumerate(missing[:50], 1):
    print(f"{i:2d}. {item}")

print("\nМУСОР/СЛУЖЕБНОЕ:")
for i, item in enumerate(garbage, 1):
    print(f"{i:2d}. {item}")

report_path = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\ОТЧЕТ-fuzzy-проверка.md")
report = []
report.append("# Расширенная проверка совпадений\n\n")
report.append(f"- Переделанных: **{len(items_done)}**\n")
report.append(f"- Офферов: **{len(items_offers)}**\n")
report.append(f"- Точные совпадения: **{len(exact)}**\n")
report.append(f"- Похожие совпадения: **{len(fuzzy)}**\n")
report.append(f"- Реально не найдено: **{len(missing)}**\n")
report.append(f"- Мусор/служебное: **{len(garbage)}**\n\n")

report.append("## Точные совпадения\n")
for i, (a, b) in enumerate(exact, 1):
    report.append(f"{i}. {a} --> {b}\n")

report.append("\n## Похожие совпадения\n")
for i, (a, b, s) in enumerate(fuzzy, 1):
    report.append(f"{i}. {a} --> {b} ({s})\n")

report.append("\n## Реально не найдено\n")
for i, item in enumerate(missing, 1):
    report.append(f"{i}. {item}\n")

report.append("\n## Мусор/служебное\n")
for i, item in enumerate(garbage, 1):
    report.append(f"{i}. {item}\n")

report_path.write_text("".join(report), encoding="utf-8")
print(f"\n💾 Отчёт сохранён: {report_path}")