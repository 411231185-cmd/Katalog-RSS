import re

offers_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса- список сделанных.md"
done_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"

print("🔍 ДИАГНОСТИКА ФОРМАТА ФАЙЛОВ\n")

# Анализируем структуру файлов
print("=== ОФФЕРЫ (первые 10 строк): ===")
with open(offers_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()[:10]
    for i, line in enumerate(lines, 1):
        print(f"{i:2d}: {repr(line.strip())}")

print("\n=== ПЕРЕДЕЛАННЫЕ (первые 10 строк): ===")
with open(done_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()[:10]
    for i, line in enumerate(lines, 1):
        print(f"{i:2d}: {repr(line.strip())}")

# Пробуем разные форматы для извлечения
print("\n=== АНАЛИЗ ФОРМАТА 'ПЕРЕДЕЛАННЫЕ': ===")
with open(done_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Пробуем разные варианты извлечения
patterns = [
    r'^- (.+)',  # Markdown списки
    r'^• (.+)',  # Точки с запятой
    r'^(\d+\..+)',  # Нумерованные списки
    r'^([А-Яа-яЁёA-Za-z0-9\s\-_]+)(?:\n|$)',  # Любые строки с буквами
]

for pattern in patterns:
    matches = re.findall(pattern, content, re.MULTILINE)
    print(f"Паттерн '{pattern}': {len(matches)} совпадений")
    if matches:
        print(f"   Пример: '{matches[0]}'")
