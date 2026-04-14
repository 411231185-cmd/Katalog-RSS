from pathlib import Path
import re

src = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-РАЗДЕЛЫ-ШИФРЫ.md")
dst = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-ВСЕ-ШИФРЫ-В-СТРОКУ.md")

text = src.read_text(encoding="utf-8")

lines = [l.strip() for l in text.splitlines() if l.strip()]

codes = []

for line in lines:
    # разбиваем по запятой и пробелам
    tokens = re.split(r"[,\s]+", line)
    tokens = [t for t in tokens if t]

    for t in tokens:
        t = t.strip(" ,;")

        # убираем одиночную точку на конце
        if t.endswith(".") and "." not in t[:-1]:
            t = t[:-1]

        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", t))
        has_digit = bool(re.search(r"\d", t))
        if not (has_letter and has_digit):
            continue

        # фильтр обрезков типа СА98, 1Н98 — по аналогии с предыдущим скриптом
        if len(t) < 5 and "." not in t:
            continue

        codes.append(t)

# убираем дубли, сохраняем порядок
seen = set()
unique = []
for c in codes:
    if c not in seen:
        seen.add(c)
        unique.append(c)

result = ", ".join(unique)
dst.write_text(result, encoding="utf-8")

print(f"Всего шифров: {len(unique)}")
print(f"Результат записан в: {dst}")