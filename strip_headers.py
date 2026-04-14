from pathlib import Path

path = Path(r"C:\GitHub-Repositories\Katalog-RSS\Kinematika-Chertegi\Шифры RSS\ЧЕРНОВИК-РАЗДЕЛЫ-ШИФРЫ.md")

text = path.read_text(encoding="utf-8")
lines = text.splitlines()

new_lines = []

for line in lines:
    # пропускаем все заголовки разделов
    if line.lstrip().startswith("###"):
        continue
    new_lines.append(line)

path.write_text("\n".join(new_lines), encoding="utf-8")
print("Все строки, начинающиеся с '###', удалены.")