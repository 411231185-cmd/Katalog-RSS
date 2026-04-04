import re
from pathlib import Path
from difflib import SequenceMatcher

file_done = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md")
file_offers = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса.md")
out_file = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\НУЖНО-СГЕНЕРИРОВАТЬ-ТКП.md")
check_file = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\ПРОВЕРИТЬ-ВРУЧНУЮ.md")

text_done = file_done.read_text(encoding="utf-8")
text_offers = file_offers.read_text(encoding="utf-8")

items_done = [re.sub(r"^\d+\.\s*", "", x).strip() for x in re.findall(r"^\d+\..+", text_done, re.MULTILINE)]
items_offers_raw = [x.strip() for x in re.findall(r"^##\s+(.+)$", text_offers, re.MULTILINE)]

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
    if not n or n in {"твоя роль", "поля для заполнения", "все офферы готовые", "все офферы готовые directus", "партия 2", "партия 2 для directus"}:
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

need_lines = [
    "# НУЖНО-СГЕНЕРИРОВАТЬ-ТКП\n\n",
    f"Всего позиций: **{len(missing)}**\n\n"
]
for i, item in enumerate(missing, 1):
    need_lines.append(f"{i}. {item}\n")
out_file.write_text("".join(need_lines), encoding="utf-8")

check_lines = [
    "# ПРОВЕРИТЬ-ВРУЧНУЮ\n\n",
    f"Всего спорных позиций: **{len(fuzzy)}**\n\n"
]
for i, (a, b, s) in enumerate(fuzzy, 1):
    check_lines.append(f"{i}. {a} --> {b} ({s})\n")
check_file.write_text("".join(check_lines), encoding="utf-8")

print("ГОТОВО")
print("=" * 80)
print(f"✅ Точных совпадений: {len(exact)}")
print(f"🔶 Спорных: {len(fuzzy)}")
print(f"❌ Нужно сгенерировать ТКП: {len(missing)}")
print(f"🗑️ Мусор: {len(garbage)}")

print("\nНУЖНО СГЕНЕРИРОВАТЬ:")
for i, item in enumerate(missing, 1):
    print(f"{i}. {item}")

print(f"\n💾 Список генерации: {out_file}")
print(f"💾 Список ручной проверки: {check_file}")