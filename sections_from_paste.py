from pathlib import Path
import re

# если хочешь работать с ЧЕРНОВИК.md, поменяй путь на свой
src = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК.md")
dst = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-РАЗДЕЛЫ-ШИФРЫ.md")

text = src.read_text(encoding="utf-8")

lines = [l.rstrip() for l in text.splitlines()]

sections = []
current_title = "БЕЗ НАЗВАНИЯ"
current_body = []


def flush_section():
    global current_title, current_body
    if current_body:
        sections.append((current_title.strip(), "\n".join(current_body)))
    current_body = []


def is_header(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # Явные маркеры разделов старого сайта
    if "Сайт RZN СТВРЫЙ.docx" in s:
        return True
    if "КАРТА САЙТА" in s:
        return True
    # Заголовки с двоеточием
    if s.endswith(":"):
        return True
    # Строка в ВЕРХНЕМ регистре (типа ПНР, ОСНАСТКА и т.п.)
    letters = "".join(ch for ch in s if ch.isalpha())
    if letters and letters.upper() == letters:
        return True
    return False


for line in lines:
    if is_header(line):
        flush_section()
        current_title = line
    else:
        current_body.append(line)

flush_section()

# Паттерн «шифра»: буквы/цифры + .-/ длиной >= 3
code_pattern = re.compile(r"[0-9A-Za-zА-Яа-яЁё\.\-/]{3,}")

out_lines = []

for title, body in sections:
    candidates = code_pattern.findall(body)

    codes = []
    for c in candidates:
        # хотя бы одна буква и одна цифра
        has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", c))
        has_digit = bool(re.search(r"\d", c))
        if has_letter and has_digit:
            codes.append(c)

    # убираем дубли, сохраняем порядок
    seen = set()
    unique_codes = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique_codes.append(c)

    if not unique_codes:
        continue

    out_lines.append(f"### {title.strip()}")
    out_lines.append(", ".join(unique_codes))
    out_lines.append("")

dst.write_text("\n".join(out_lines), encoding="utf-8")
print(f"Разделов найдено: {len(sections)}")
print(f"Результат записан в: {dst}")