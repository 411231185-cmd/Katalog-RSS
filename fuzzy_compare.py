import re
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

offers_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса- список сделанных.md"
done_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"

print("🔍 FUZZY СРАВНЕНИЕ ОФФЕРОВ (похожесть > 70%)\n")

# Читаем списки
with open(offers_file, 'r', encoding='utf-8') as f:
    offers_content = f.read()
with open(done_file, 'r', encoding='utf-8') as f:
    done_content = f.read()

# Извлекаем списки названий
offers_list = re.findall(r'^- (.+)', offers_content, re.MULTILINE)
done_list = re.findall(r'^- (.+)', done_content, re.MULTILINE)

print(f"📦 Офферов в базе: {len(offers_list)}")
print(f"📋 Переделанных: {len(done_list)}")

# Fuzzy matching: находим совпадения с похожостью > 70%
matches = []
missing_from_offers = []  # есть в переделанных, нет в базе офферов
missing_from_done = []    # есть в офферах, нет в переделанных

for done_offer in done_list:
    found_match = False
    best_match = None
    best_score = 0
    
    for offer in offers_list:
        score = similarity(done_offer, offer)
        if score > 0.7 and score > best_score:  # Порог похожести 70%
            best_score = score
            best_match = offer
    
    if best_match:
        matches.append((done_offer, best_match, best_score))
    else:
        missing_from_offers.append(done_offer)

for offer in offers_list:
    if offer not in [m[1] for m in matches]:
        missing_from_done.append(offer)

# РЕЗУЛЬТАТЫ
print(f"\n🎯 НАЙДЕНО СОВПАДЕНИЙ (fuzzy match >70%): {len(matches)}")
print(f"✅ Готово для Directus: {len(matches)} из {len(done_list)} ({round(len(matches)/len(done_list)*100,1)}%)")

print(f"\n📋 ОТСУТСТВУЮТ В БАЗЕ ОФФЕРОВ (нужно добавить): {len(missing_from_offers)}")
for i, item in enumerate(missing_from_offers[:10], 1):
    print(f"   {i}. {item}")
if len(missing_from_offers) > 10:
    print(f"   ... и ещё {len(missing_from_offers)-10} товаров")

print(f"\n📦 ОФФЕРЫ БЕЗ ПЕРЕДЕЛКИ (есть в базе, нет в списке): {len(missing_from_done)}")
for i, item in enumerate(missing_from_done[:10], 1):
    print(f"   {i}. {item}")
if len(missing_from_done) > 10:
    print(f"   ... и ещё {len(missing_from_done)-10} товаров")

# Сохраняем результаты в файл
with open('C:\\GitHub-Repositories\\Katalog-RSS\\Directus-RSS\\Товары\\АНАЛИЗ-ДЛЯ-DIRECTUS.md', 'w', encoding='utf-8') as f:
    f.write(f"# АНАЛИЗ ОФФЕРОВ ДЛЯ DIRECTUS\n\n")
    f.write(f"**Готово: {len(matches)} из {len(done_list)} ({round(len(matches)/len(done_list)*100,1)}%)**\n\n")
    f.write("## ТОВАРЫ КОТОРЫХ НЕ ХВАТАЕТ В БАЗЕ:\n")
    for item in missing_from_offers:
        f.write(f"- {item}\n")
    f.write("\n## ОФФЕРЫ БЕЗ ПЕРЕДЕЛКИ:\n")
    for item in missing_from_done:
        f.write(f"- {item}\n")

print(f"\n✅ Полный анализ сохранен: АНАЛИЗ-ДЛЯ-DIRECTUS.md")
