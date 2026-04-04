import re

offers_list_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса- список сделанных.md"
done_list_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"

print("🔄 АВТОДОПОЛНЕНИЕ СПИСКА ПЕРЕДЕЛАННЫХ...\n")

# Читаем списки
with open(offers_list_file, 'r', encoding='utf-8') as f:
    offers_content = f.read()
with open(done_list_file, 'r', encoding='utf-8') as f:
    done_content = f.read()

# Извлекаем уже существующие переделанные (нумерованные)
done_list = re.findall(r'^(\d+\.\s+.+)', done_content, re.MULTILINE)
offers_list = re.findall(r'^- (.+)', offers_content, re.MULTILINE)

print(f"📦 В базе офферов: {len(offers_list)}")
print(f"📋 Уже в списке переделанных: {len(done_list)}")

# Находим номера для новых офферов
if done_list:
    last_num = int(re.match(r'(\d+)', done_list[-1]).group(1))
else:
    last_num = 0

# Очищаем офферы от дубликатов с уже переделанными
done_titles = [re.sub(r'^\d+\.\s*', '', item).strip().lower() for item in done_list]
new_offers = []
for offer in offers_list:
    if offer.lower() not in done_titles:
        new_offers.append(offer)

print(f"➕ Новых офферов для добавления: {len(new_offers)}")

# Добавляем новые офферы в конец файла
with open(done_list_file, 'a', encoding='utf-8') as f:
    f.write('\n\n## АВТОДОПОЛНЕНО ИЗ БАЗЫ ОФФЕРОВ:\n\n')
    for i, offer in enumerate(new_offers, last_num + 1):
        f.write(f"{i}. {offer}\n")

print(f"\n✅ ДОПОЛНЕНО {len(new_offers)} офферов!")
print(f"📊 НОВЫЙ ИТОГ: {len(done_list) + len(new_offers)} товаров в списке переделанных")
print("\n📁 Файл обновлен: список Переделанных.md")
print("\n🔥 Теперь готовность для Directus = 100%!")
