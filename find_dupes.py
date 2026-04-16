import re
from collections import defaultdict

filepath = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса.md"
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
except Exception as e:
    print(f"Ошибка чтения файла: {e}")
    exit()

# Разбиваем файл по разделителю, который мы добавили ранее
blocks = content.split('---')
seen = defaultdict(list)

for block in blocks:
    block = block.strip()
    if not block: continue
    
    # Отделяем заголовок (имя файла) от самого текста
    lines = block.split('\n', 1)
    title = lines[0].replace('## ', '').strip() if lines[0].startswith('## ') else 'Без названия'
    body = lines[1].strip() if len(lines) > 1 else ''
    
    # Убираем все пробелы, переносы и регистр для максимально точного сравнения текста
    normalized = re.sub(r'\s+', '', body.lower())
    if normalized:
        seen[normalized].append(title)

# Выводим результаты
found = False
print("\n🔍 АНАЛИЗ ДУБЛИКАТОВ...\n")
for text, titles in seen.items():
    if len(titles) > 1:
        found = True
        print(f"⚠️ НАЙДЕН ДУБЛЬ! Одинаковый текст в следующих файлах ({len(titles)} шт.):")
        for t in titles:
            print(f"   - {t}")
        print("-" * 40)

if not found:
    print("✅ Дубликатов текстов не найдено, все офферы уникальны!")
print("\n")
