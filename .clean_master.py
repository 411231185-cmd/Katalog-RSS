# -*- coding: utf-8 -*-
import pandas as pd
import re

print('=' * 80)
print('🧹 ЧИСТКА ОТ ГОРОДОВ И БРЕНДОВ')
print('=' * 80)

# Загружаем файл
filepath = 'catalogs/MASTER_WITH_HTML_LINKS copy.csv'
df = pd.read_csv(filepath, encoding='utf-8-sig')
print(f'✅ Загружено офферов: {len(df)}')

# Списки для удаления
cities = [
    'москва', 'москве', 'московский', 'московская',
    'санкт-петербург', 'петербург', 'спб',
    'новосибирск', 'екатеринбург', 'казань',
    'нижний новгород', 'челябинск', 'самара',
    'омск', 'ростов-на-дону', 'уфа', 'красноярск',
    'воронеж', 'пермь', 'волгоград', 'краснодар'
]

brands = [
    'bosch', 'makita', 'dewalt', 'hilti', 'metabo',
    'бош', 'макита', 'хилти', 'метабо',
    'гродно', 'азовмаш', 'кзтс', 'свердлов'
]

# Функция очистки
def clean_text(text):
    if pd.isna(text):
        return text
    
    text_str = str(text)
    text_lower = text_str.lower()
    
    # Удаляем города
    for city in cities:
        # Удаляем как отдельное слово с границами
        pattern = r'\b' + re.escape(city) + r'\b'
        text_str = re.sub(pattern, '', text_str, flags=re.IGNORECASE)
    
    # Удаляем бренды
    for brand in brands:
        pattern = r'\b' + re.escape(brand) + r'\b'
        text_str = re.sub(pattern, '', text_str, flags=re.IGNORECASE)
    
    # Убираем множественные пробелы
    text_str = re.sub(r'\s+', ' ', text_str)
    
    # Убираем пробелы перед знаками препинания
    text_str = re.sub(r'\s+([.,;:!?])', r'\1', text_str)
    
    return text_str.strip()

# Чистим поля
print('\n🔄 Обработка полей...')

fields_to_clean = ['Title', 'Text', 'Description']
changes_count = 0

for field in fields_to_clean:
    if field in df.columns:
        print(f'   Чистим {field}...')
        original = df[field].copy()
        df[field] = df[field].apply(clean_text)
        
        # Считаем изменения
        changed = (original != df[field]).sum()
        changes_count += changed
        print(f'   ✅ Изменено записей: {changed}')

# Сохраняем
output_path = 'catalogs/MASTER_CLEANED.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f'\n✅ ГОТОВО!')
print(f'📁 Сохранено: {output_path}')
print(f'📊 Всего изменений: {changes_count}')

# Показываем пример
print('\n📋 ПРИМЕР ДО/ПОСЛЕ (первый оффер):')
df_original = pd.read_csv(filepath, encoding='utf-8-sig')
print(f'\nДО:  {df_original.iloc[0]["Title"]}')
print(f'ПОСЛЕ: {df.iloc[0]["Title"]}')

print('=' * 80)
