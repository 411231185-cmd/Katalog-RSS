from pathlib import Path
import re

# Исходник со всем сырым текстом
src = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\Шифры ШВП.md")

# Файл-результат: список ШВП в столбик, пронумерованный
dst_column = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\Шифры ШВП-список в СТОЛБИК.md")

text = src.read_text(encoding="utf-8")

# Нормализуем пробелы, чтобы правильно ловить "сплошняк"
text = re.sub(r"\s+", " ", text)

# Шаг 1: вытаскиваем все фрагменты, содержащие ШВП/Швп/швп (до следующего слова "ШВП" или конца)
fragments = re.findall(r"(?i)(швп[^Шш]+)", text)

codes = []

for frag in fragments:
    # Единый регистр
    frag = frag.replace("Швп", "ШВП").replace("швп", "ШВП").strip()

    # Обязательно пробел после "ШВП", если сразу идёт код
    frag = re.sub(r"^ШВП(?=[0-9А-Яа-я])", "ШВП ", frag)

    # Убираем лишние пробелы вокруг точек и дефисов
    frag = re.sub(r"\s*\.\s*", ".", frag)
    frag = re.sub(r"\s*-\s*", "-", frag)

    # Убираем очевидные хвостовые символы
    frag = frag.rstrip(" ,;")

    # В некоторых строках у тебя сразу "ШВП<шифр><станок>", поэтому вытащим только шифр ШВП:
    # ШВП + пробел + до первого пробела/запятой/точки с запятой
    m = re.match(r"ШВП\s*([0-9А-Яа-яA-Za-z\.\-/\\]+)", frag)
    if m:
        code = "ШВП " + m.group(1)
        codes.append(code)

# Убираем дубли, сохраняем порядок
seen = set()
unique_codes = []
for c in codes:
    if c not in seen:
        seen.add(c)
        unique_codes.append(c)

# Формируем столбик с нумерацией
lines = []
for i, c in enumerate(unique_codes, start=1):
    lines.append(f"{i}. {c}")

dst_column.write_text("\n".join(lines), encoding="utf-8")
print(f"В столбик записано {len(unique_codes)} уникальных шифров ШВП в файл:\n{dst_column}")