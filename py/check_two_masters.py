# -*- coding: utf-8 -*-
import pandas as pd

print('=' * 80)
print('🔍 СРАВНЕНИЕ ДВУХ MASTER ФАЙЛОВ')
print('=' * 80)

files = [
    'catalogs/MASTER_WITH_HTML_LINKS copy.csv',
    'catalogs/MASTER_WITH_HTML_LINKS.csv'
]

for filepath in files:
    print(f'\n📂 {filepath}')
    print('-' * 80)
    
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        print(f'✅ Офферов: {len(df)}')
        
        # Берем первый оффер
        sample = df.iloc[0]
        print(f'SKU: {sample["SKU"]}')
        print(f'Title: {sample["Title"]}')
        
        # Проверяем HTML-ссылки
        text = str(sample['Text'])
        links_count = text.count('<a href="')
        print(f'HTML-ссылок в Text: {links_count}')
        
        # Показываем кусок текста
        print(f'\nText (первые 400 символов):')
        print(text[:400])
        
        # Проверяем Description тоже
        desc = str(sample.get('Description', ''))
        desc_links = desc.count('<a href="')
        print(f'\nDescription HTML-ссылок: {desc_links}')
        
    except Exception as e:
        print(f'❌ ОШИБКА: {e}')

print('\n' + '=' * 80)
print('🎯 ВЫВОД: Какой файл использовать?')
print('=' * 80)
