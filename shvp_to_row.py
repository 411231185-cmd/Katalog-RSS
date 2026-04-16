from pathlib import Path
import re

src_column = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\Шифры ШВП-список в СТОЛБИК.md")
dst_row = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\Шифры ШВП-список в СТРОКУ+ссылки.md")

text = src_column.read_text(encoding="utf-8")
lines = [l.strip() for l in text.splitlines() if l.strip()]

codes = []

for line in lines:
    # Ожидаемый формат: "N. ШВП ХХХХХ"
    m = re.match(r"\d+\.\s*(ШВП\s+[0-9А-Яа-яA-Za-z\.\-/\\]+)", line)
    if m:
        codes.append(m.group(1))

# На всякий случай убираем дубли, если вдруг появятся
seen = set()
unique_codes = []
for c in codes:
    if c not in seen:
        seen.add(c)
        unique_codes.append(c)

result = ", ".join(unique_codes)

dst_row.write_text(result, encoding="utf-8")
print(f"В строку записано {len(unique_codes)} шифров ШВП в файл:\n{dst_row}")