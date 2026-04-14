import os
import re

root = r"C:\GitHub-Repositories\Katalog-RSS"
out_path = r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Vse Shifri.md"

# Паттерн: цифры/буквы (рус+лат) + допускаем . и - , длина ≥ 3
pattern = re.compile(r"\b[0-9A-Za-zА-Яа-яЁё\-.]{3,}\b")

codes = set()

for dirpath, dirnames, filenames in os.walk(root):
    for name in filenames:
        if not name.lower().endswith((".md", ".html", ".htm", ".txt")):
            continue
        full_path = os.path.join(dirpath, name)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            continue

        for m in pattern.findall(text):
            # хотя бы одна буква и одна цифра
            has_letter = bool(re.search(r"[A-Za-zА-Яа-яЁё]", m))
            has_digit = bool(re.search(r"\d", m))
            if has_letter and has_digit:
                codes.add(m)

sorted_codes = sorted(codes, key=lambda x: (x.replace("РТ", "RT"), x))
result_line = ", ".join(sorted_codes)

os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(result_line)