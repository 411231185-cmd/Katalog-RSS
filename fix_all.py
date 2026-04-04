import re

big_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса.md"
list_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса- список сделанных.md"
done_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"

# Читаем файлы
with open(big_file, "r", encoding="utf-8") as f:
    big = f.read()
with open(list_file, "r", encoding="utf-8") as f:
    lst = f.read()
with open(done_file, "r", encoding="utf-8") as f:
    done = f.read()

# Фикс 1: Большой файл — убираем "Товар:" из заголовков
big_fixed = re.sub(r'^(## )Товар:\s*', r'\1', big, flags=re.MULTILINE)
with open(big_file, "w", encoding="utf-8") as f:
    f.write(big_fixed)

titles_big = [i.strip() for i in re.findall(r'^## (.+)', big_fixed, re.MULTILINE)]
print(f"✅ Большой файл исправлен: {len(titles_big)} заголовков (убрали 'Товар:')")
print(f"   Пример: {titles_big[0]}")

# Фикс 2: Список — убираем подчёркивания и суффиксы
def clean_offer(name):
    name = name.replace("_", " ")
    name = re.sub(r'\s*(для Directus|Directus)\s*$', '', name, flags=re.IGNORECASE)
    return name.strip()

titles_list = [clean_offer(i) for i in re.findall(r'^- (.+)', lst, re.MULTILINE)]

# Пересобираем список из заголовков большого файла (источник правды!)
with open(list_file, "w", encoding="utf-8") as f:
    f.write("## ОФФЕРЫ ДЛЯ DIRECTUS (Готово)\n\n")
    for title in titles_big:
        f.write(f"- {title}\n")
print(f"✅ Список пересобран из большого файла: {len(titles_big)} офферов")

# Фикс 3: Переделанные — убираем строки с ": " в начале и дубли
done_list_raw = re.findall(r'^\d+\.\s+(.+)', done, re.MULTILINE)
done_clean = []
seen = set()
for item in done_list_raw:
    item = re.sub(r'^:\s*', '', item).strip()  # убираем ": " в начале
    item = re.sub(r'\bтовар\b', '', item, flags=re.IGNORECASE).strip()
    if item.lower() not in seen and item:
        seen.add(item.lower())
        done_clean.append(item)

with open(done_file, "w", encoding="utf-8") as f:
    f.write("# Список переделанных товаров (ТКП готовы)\n\n")
    for i, item in enumerate(done_clean, 1):
        f.write(f"{i}. {item}\n")
print(f"✅ Переделанные очищены: {len(done_clean)} уникальных (было {len(done_list_raw)})")

# Финальное сравнение
big_set = set(i.lower() for i in titles_big)
done_set = set(i.lower() for i in done_clean)
matches = big_set & done_set
print(f"\n🎯 ИТОГ:")
print(f"   Офферов в базе: {len(titles_big)}")
print(f"   Переделанных: {len(done_clean)}")
print(f"   Совпадений: {len(matches)}")
print(f"   Готовность: {round(len(matches)/len(titles_big)*100,1)}%")