import re
from collections import Counter

done_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"
offers_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса- список сделанных.md"

with open(done_file, "r", encoding="utf-8") as f:
    done_content = f.read()

with open(offers_file, "r", encoding="utf-8") as f:
    offers_content = f.read()

# Извлекаем списки
done_list = re.findall(r"^\d+\.\s+(.+)", done_content, re.MULTILINE)
offers_list = [i.strip() for i in re.findall(r"^- (.+)", offers_content, re.MULTILINE)]

# Убираем слово "товар"
done_clean = [re.sub(r"\bтовар\b", "", i, flags=re.IGNORECASE).strip() for i in done_list]

# Ищем дубли
dupes = {k: v for k, v in Counter(done_clean).items() if v > 1}

# Уникальный список
unique = list(dict.fromkeys(done_clean))

# Сравниваем
done_set = set(i.lower() for i in unique)
offers_set = set(i.lower() for i in offers_list)
matches = done_set & offers_set
missing_in_done = offers_set - done_set
missing_in_offers = done_set - offers_set

print(f"📋 Переделанных (после чистки): {len(unique)}")
print(f"📦 Офферов в базе: {len(offers_list)}")
print(f"✅ Совпадений: {len(matches)}")
print(f"❌ Нет в переделанных: {len(missing_in_done)}")
print(f"❌ Нет в офферах: {len(missing_in_offers)}")
print(f"🔁 Дублей удалено: {len(done_list) - len(unique)}")

if dupes:
    print(f"\n⚠️ Дубли:")
    for k, v in list(dupes.items())[:5]:
        print(f"  {k[:60]} ({v}x)")

# Сохраняем чистый файл
with open(done_file, "w", encoding="utf-8") as f:
    f.write("# Список переделанных товаров (ТКП готовы)\n\n")
    for i, item in enumerate(unique, 1):
        f.write(f"{i}. {item}\n")

print(f"\n✅ Файл перезаписан: {len(unique)} уникальных товаров")
print(f"\n✅ Файл перезаписан: {len(unique)} уникальных товаров")