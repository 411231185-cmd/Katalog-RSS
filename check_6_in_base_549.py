import re
from pathlib import Path
from difflib import SequenceMatcher

file_base = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Список что есть на 02.04.26.md")
queries = [
    "Втулка переходная в шпиндельную бабку ДИП500, 1М65, 1Н65, РТ117, РТ817",
    "4-х кулачковые механизированные патроны для обработки заготовок ф. 1250и 1500мм.",
    "Шкив 1М63.21.053",
    "ШВП 1П756ДФ3",
    "Вал-шестерня 6Р82.4.50А коробки подач станка 6Р82, 6Р12",
    "Резцедержатель для станков ДИП300, 1М63, 1М63Н, 16К40"
]

if not file_base.exists():
    print(f"❌ Не найден файл: {file_base}")
    raise SystemExit

text_base = file_base.read_text(encoding="utf-8")
base_items = [x.strip() for x in re.findall(r"^-\s+(.+)$", text_base, re.MULTILINE)]

if not base_items:
    base_items = [x.strip() for x in re.findall(r"^\d+\.\s+(.+)$", text_base, re.MULTILINE)]

def norm(s: str) -> str:
    s = s.lower().strip()
    s = s.replace("ё", "е")
    s = s.replace("_", " ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^a-zа-я0-9]+", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

print("ПРОВЕРКА 6 ПОЗИЦИЙ В БАЗЕ 549 ТОВАРОВ")
print("=" * 80)
print(f"📦 Всего позиций в базе: {len(base_items)}")

for q in queries:
    exact = []
    fuzzy = []
    for item in base_items:
        score = sim(q, item)
        if norm(q) == norm(item):
            exact.append(item)
        elif score >= 0.72:
            fuzzy.append((item, round(score, 3)))
    print(f"\nПОЗИЦИЯ: {q}")
    if exact:
        print("  ✅ ТОЧНО ЕСТЬ В БАЗЕ:")
        for x in exact[:5]:
            print(f"     - {x}")
    elif fuzzy:
        print("  🔶 ПОХОЖЕ ЕСТЬ В БАЗЕ:")
        for x, s in sorted(fuzzy, key=lambda z: z[1], reverse=True)[:5]:
            print(f"     - {x}  ({s})")
    else:
        print("  ❌ В БАЗЕ НЕ НАЙДЕНО")