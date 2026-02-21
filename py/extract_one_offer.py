# -*- coding: utf-8 -*-
import pandas as pd

# === ПУТИ К ФАЙЛАМ ===
input_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\MASTER_WITH_HTML_LINKS.csv'
output_file = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\1OFFER-Link.csv'

print('=' * 100)
print('📋 ИЗВЛЕЧЕНИЕ ОДНОГО ОФФЕРА ДЛЯ ТЕСТИРОВАНИЯ')
print('=' * 100)

# Читаем большой каталог
df = pd.read_csv(input_file, encoding='utf-8-sig')

print(f"\n📊 Всего офферов в каталоге: {len(df)}")

# Ищем оффер с максимальным количеством ссылок
df['links_count'] = df['Text'].fillna('').str.count('<a href=')
best_offer = df.loc[df['links_count'].idxmax()]

# Создаём DataFrame с одним оффером
df_one = pd.DataFrame([best_offer])

# Удаляем служебную колонку
if 'links_count' in df_one.columns:
    df_one = df_one.drop('links_count', axis=1)

# Сохраняем
df_one.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n✅ ОФФЕР ИЗВЛЕЧЁН!")
print('=' * 100)
print(f"SKU: {best_offer['SKU']}")
print(f"Title: {best_offer['Title']}")
print(f"Количество HTML-ссылок: {best_offer['links_count']}")
print('=' * 100)
print(f"\n📂 Тестовый файл сохранён: {output_file}")
print('\n🔍 PREVIEW TEXT (первые 800 символов):')
print('=' * 100)
print(best_offer['Text'][:800] if pd.notna(best_offer['Text']) else 'Text пустой')
print('...')
print('=' * 100)
