from pathlib import Path

FILENAME = "TOP-KATALOG-TILDA-MINI.csv"

path = Path(FILENAME)
text = path.read_text(encoding="utf-8-sig")

# бэкап
backup = path.with_name(path.stem + "-structure-backup.csv")
backup.write_text(text, encoding="utf-8-sig")
print("Бэкап сохранён как:", backup.name)

lines = text.splitlines()
header = lines[0]
cols = header.split(";")
n_cols = len(cols)
print("Колонок в header:", n_cols)

new_lines = [header]

for i, line in enumerate(lines[1:], start=2):
    parts = line.split(";")
    if len(parts) < n_cols:
        parts += [""] * (n_cols - len(parts))
    elif len(parts) > n_cols:
        parts = parts[:n_cols]
    new_lines.append(";".join(parts))

path.write_text("\n".join(new_lines), encoding="utf-8-sig")
print("Структура нормализована, файл перезаписан:", path.name)
