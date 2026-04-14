from pathlib import Path
import re

# исходный файл с разделами
src = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-РАЗДЕЛЫ-ШИФРЫ.md")
# итоговый общий файл
dst = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse - Vse Shifri .md")

text = src.read_text(encoding="utf-8")

lines = [l.strip() for l in text.splitlines() if l.strip()]

codes = []

for line in lines:
    tokens = re.split(r"[,\s]+", line)
    tokens = [t for t in tokens if t]

    for t in tokens:
        t = t.strip(" ,;")

        if not t:
            continue

        # убираем одиночную точку на конце
        if t.endswith(".") and "." not in t[:-1]:
            t = t[:-1]

        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", t))
        has_digit = bool(re.search(r"\d", t))
        if not (has_letter and has_digit):
            continue

        # отбрасываем размеры, мм, ф. и т.п.
        low = t.lower()
        if low.endswith("мм") or low.endswith("мм.") or "мм" in low:
            continue
        if low.startswith("ф") or "ф." in low:
            continue
        if re.fullmatch(r"м\d+х\d+.*", low):
            continue  # М16х2мм и т.п.

        # допускаем шифр, если длина ≥ 3 и есть буквы+цифры
        codes.append(t)

# убираем дубли, сохраняем порядок
seen = set()
unique = []
for c in codes:
    if c not in seen:
        seen.add(c)
        unique.append(c)

# пишем красиво: в столбик
dst.write_text("\n".join(unique), encoding="utf-8")

print(f"Собрано {len(unique)} уникальных шифров.")
print(f"Результат: {dst}")