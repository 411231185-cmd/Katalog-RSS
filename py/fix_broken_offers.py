# -*- coding: utf-8 -*-
import pandas as pd
import re

def clean_html_tags(text):
    """Удаляет HTML теги"""
    if pd.isna(text):
        return ''
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def fix_catalog():
    print('=' * 80)
    print('FIXING BROKEN OFFERS')
    print('=' * 80)
    
    df = pd.read_csv('MASTER_CATALOG_WITH_DESCRIPTIONS.csv', encoding='utf-8-sig')
    
    print("\nTotal offers: " + str(len(df)))
    
    fixed_desc = 0
    fixed_title = 0
    removed = 0
    
    # Исправляем Description из Title если пусто
    for idx, row in df.iterrows():
        # Проверяем Title
        if pd.isna(row['Title']) or row['Title'] == 'nan':
            # Пытаемся извлечь из SKU
            sku = str(row['SKU'])
            if ';' in sku:
                # SKU содержит лишние данные - очищаем
                parts = sku.split(';')
                if len(parts) > 6:
                    df.at[idx, 'Title'] = parts[6]
                    fixed_title += 1
        
        # Проверяем Description
        if pd.isna(row['Description']) or row['Description'] == '':
            # Пытаемся использовать Title
            if not pd.isna(row['Title']) and row['Title'] != 'nan':
                df.at[idx, 'Description'] = str(row['Title'])[:300]
                fixed_desc += 1
    
    # Удаляем строки где Title все еще nan
    df_clean = df[~(pd.isna(df['Title']) | (df['Title'] == 'nan'))]
    removed = len(df) - len(df_clean)
    
    df_clean.to_csv('MASTER_CATALOG_CLEANED.csv', index=False, encoding='utf-8-sig')
    
    print('\n' + '=' * 80)
    print('RESULTS')
    print('=' * 80)
    print("Original offers: " + str(len(df)))
    print("Fixed Titles: " + str(fixed_title))
    print("Fixed Descriptions: " + str(fixed_desc))
    print("Removed broken: " + str(removed))
    print("Final offers: " + str(len(df_clean)))
    print("\nFile saved: MASTER_CATALOG_CLEANED.csv")
    print('=' * 80)

if __name__ == '__main__':
    fix_catalog()
