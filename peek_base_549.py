from pathlib import Path

file_base = Path(r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Список что есть на 02.04.26.md")

if not file_base.exists():
    print(f"❌ Не найден файл: {file_base}")
    raise SystemExit

text = file_base.read_text(encoding="utf-8")
lines = text.splitlines()

print(f"Всего строк в файле: {len(lines)}")
print("=" * 80)

for i, line in enumerate(lines[:80], 1):
    print(f"{i:03d}: {repr(line)}")