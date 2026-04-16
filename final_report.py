import re
from difflib import get_close_matches

big_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Офферы 549 + ткп для директуса.md"
done_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\список Переделанных.md"
report_file = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\ОТЧЁТ-ГОТОВНОСТЬ-DIRECTUS.md"

with open(big_file, "r", encoding="utf-8") as f:
    big = f.read()
with open(done_file, "r", encoding="utf-8") as f:
    done = f.read()

offers = [i.strip() for i in re.findall(r'^## (.+)', big, re.MULTILINE)]
done_list = [re.sub(r'^\d+\.\s*', '', i).strip() for i in re.findall(r'^\d+\..+', done, re.MULTILINE)]

offers_lower = {i.lower(): i for i in offers}
done_lower = {i.lower(): i for i in done_list}

# Точные совпадения
exact = set(offers_lower.keys()) & set(done_lower.keys())

# Не совпавшие офферы — ищем похожие в переделанных
not_matched_offers = [v for k, v in offers_lower.items() if k not in exact]
not_matched_done = [v for k, v in done_lower.items() if k not in exact]

# Fuzzy: ищем близкие названия
fuzzy_pairs = []
truly_missing = []
for offer in not_matched_offers:
    close = get_close_matches(offer.lower(), done_lower.keys(), n=1, cutoff=0.6)
    if close:
        fuzzy_pairs.append((offer, done_lower[close[0]]))
    else:
        truly_missing.append(offer)

print(f"📊 ОТЧЁТ ГОТОВНОСТИ ДЛЯ DIRECTUS")
print(f"{'='*60}")
print(f"📦 Всего офферов: {len(offers)}")
print(f"✅ Точных совпадений: {len(exact)}")
print(f"🔶 Похожие (fuzzy 60%+): {len(fuzzy_pairs)}")
print(f"❌ Реально не переделано: {len(truly_missing)}")
print(f"🎯 Реальная готовность: {round((len(exact)+len(fuzzy_pairs))/len(offers)*100,1)}%")

print(f"\n🔶 ПОХОЖИЕ ПАРЫ (одно и то же, но разное написание):")
for offer, done_item in fuzzy_pairs[:15]:
    print(f"  ОФФЕР:      {offer}")
    print(f"  ПЕРЕДЕЛАН:  {done_item}")
    print()

print(f"\n❌ ТОЧНО НЕ ПЕРЕДЕЛАНО ({len(truly_missing)}):")
for i, item in enumerate(truly_missing, 1):
    print(f"  {i:3d}. {item}")

# Сохраняем отчёт
with open(report_file, "w", encoding="utf-8") as f:
    f.write(f"# ОТЧЁТ ГОТОВНОСТИ ДЛЯ DIRECTUS\n\n")
    f.write(f"- Всего офферов: **{len(offers)}**\n")
    f.write(f"- Точных совпадений: **{len(exact)}**\n")
    f.write(f"- Похожих (те же товары): **{len(fuzzy_pairs)}**\n")
    f.write(f"- Реальная готовность: **{round((len(exact)+len(fuzzy_pairs))/len(offers)*100,1)}%**\n\n")
    f.write(f"## ❌ НЕ ПЕРЕДЕЛАНО ({len(truly_missing)}):\n")
    for item in truly_missing:
        f.write(f"- {item}\n")
    f.write(f"\n## 🔶 ПОХОЖИЕ (уточнить название):\n")
    for offer, done_item in fuzzy_pairs:
        f.write(f"- `{offer}` → `{done_item}`\n")

print(f"\n✅ Отчёт сохранён: ОТЧЁТ-ГОТОВНОСТЬ-DIRECTUS.md")