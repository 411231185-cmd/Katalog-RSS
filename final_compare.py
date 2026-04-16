import re
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

offers_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса- список сделанных.md"
done_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"

print("🔍 ТОЧНОЕ СРАВНЕНИЕ ОФФЕРОВ ДЛЯ DIRECTUS\n")

# Читаем списки с правильными паттернами
with open(offers_file, 'r', encoding='utf-8') as f:
    offers_content = f.read()
with open(done_file, 'r', encoding='utf-8') as f:
    done_content = f.read()

# Правильное извлечение: офферы с '-', переделанные с '1. '
offers_list = re.findall(r'^- (.+)', offers_content, re.MULTILINE)
done_list = re.findall(r'^(\d+\.\s+.+)', done_content, re.MULTILINE)

print(f"📦 Офферов в базе: {len(offers_list)}")
print(f"📋 Переделанных (нумерованный список): {len(done_list)}")

# Очищаем номера из переделанных
done_list_clean = [re.sub(r'^\d+\.\s*', '', item).strip() for item in done_list]

# Fuzzy matching: находим совпадения с похожостью > 75%
matches = []
missing_from_offers = []  # переделаны, но нет в базе офферов
missing_from_done = []    # есть в офферах, нет в переделанных

for done_offer in done_list_clean:
    found_match = False
    best_match = None
    best_score = 0
    
    for offer in offers_list:
        score = similarity(done_offer, offer)
        if score > 0.75 and score > best_score:
            best_score = score
            best_match = offer
    
    if best_match:
        matches.append((done_offer, best_match, f"{best_score:.1%}"))
    else:
        missing_from_offers.append(done_offer)

for offer in offers_list:
    if offer not in [m[1] for m in matches]:
        missing_from_done.append(offer)

# РЕЗУЛЬТАТЫ
print(f"\n🎯 НАЙДЕНО СОВПАДЕНИЙ (fuzzy match >75%): {len(matches)}")
print(f"✅ Готово для Directus: {len(matches)} из {len(done_list_clean)} ({round(len(matches)/len(done_list_clean)*100,1)}%)")

print(f"\n📋 ТОВАРЫ КОТОРЫХ НЕ ХВАТАЕТ В БАЗЕ ОФФЕРОВ ({len(missing_from_offers)}):")
for i, item in enumerate(missing_from_offers[:15], 1):
    print(f"   {i:2d}. {item}")

print(f"\n📦 ОФФЕРЫ КОТОРЫХ НЕТ В СПИСКЕ ПЕРЕДЕЛАННЫХ ({len(missing_from_done)}):")
for i, item in enumerate(missing_from_done[:15], 1):
    print(f"   {i:2d}. {item}")

# Сохраняем полный анализ
with open('C:\\GitHub-Repositories\\Katalog-RSS\\Directus-RSS\\Товары\\ФИНАЛЬНЫЙ-АНАЛИЗ-DIRECTUS.md', 'w', encoding='utf-8') as f:
    f.write(f"# 🎯 ФИНАЛЬНЫЙ АНАЛИЗ ДЛЯ DIRECTUS\n\n")
    f.write(f"**Всего офферов:** {len(offers_list)}\n")
    f.write(f"**Переделано:** {len(matches)} из {len(done_list_clean)}\n")
    f.write(f"**Готовность:** {round(len(matches)/len(done_list_clean)*100,1)}%\n\n")
    
    f.write("## ❌ ТОВАРЫ КОТОРЫХ НЕ ХВАТАЕТ В БАЗЕ:\n")
    for item in missing_from_offers:
        f.write(f"- {item}\n")
    
    f.write("\n## ⚠️ ОФФЕРЫ БЕЗ ПЕРЕДЕЛКИ:\n")
    for item in missing_from_done:
        f.write(f"- {item}\n")

print(f"\n✅ Полный анализ сохранен: ФИНАЛЬНЫЙ-АНАЛИЗ-DIRECTUS.md")
