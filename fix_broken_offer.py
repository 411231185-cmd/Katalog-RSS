# -*- coding: utf-8 -*-
import pandas as pd

filepath = r'catalogs\MASTER_WITH_HTML_LINKS copy.csv'
df = pd.read_csv(filepath, encoding='utf-8-sig')

print('=' * 80)
print('🔧 ИСПРАВЛЕНИЕ БИТОГО ОФФЕРА')
print('=' * 80)

# Ищем битый оффер
broken = df[df['Title'].isna()]
print(f'\nНайдено битых офферов: {len(broken)}')

if len(broken) > 0:
    print('\nБитый SKU:')
    for idx, row in broken.iterrows():
        print(f'  Строка {idx}: {row["SKU"][:100]}...')
    
    # Вариант 1: Удалить битый оффер
    choice = input('\nУдалить битый оффер? (y/n): ')
    
    if choice.lower() == 'y':
        df = df[df['Title'].notna()]
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f'\n✅ Битый оффер удалён. Осталось: {len(df)} офферов')
    else:
        print('\n⏭️  Пропущено')
else:
    print('\n✅ Битых офферов нет')

print('=' * 80)
