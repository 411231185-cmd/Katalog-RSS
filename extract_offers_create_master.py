import pandas as pd
import os
from pathlib import Path

def read_old_offers_list(file_path='Vse-offery-RSS.txt'):
    print("=" * 80)
    print("ЧТЕНИЕ СТАРОГО СПИСКА ОФФЕРОВ")
    print("=" * 80)
    offers_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('==='):
                continue
            if ')' in line and '—' in line:
                parts = line.split(')', 1)
                if len(parts) == 2:
                    content = parts[1].strip()
                    if '—' in content:
                        sku, title = content.split('—', 1)
                        offers_dict[sku.strip()] = title.strip()
        print(f"Загружено {len(offers_dict)} офферов")
        
        # Показываем первые 5 SKU из списка
        print("\nПримеры SKU из старого списка:")
        for i, sku in enumerate(list(offers_dict.keys())[:5], 1):
            print(f"  {i}. '{sku}'")
        
        return offers_dict
    except Exception as e:
        print(f"Ошибка: {e}")
        return {}

def extract_offers_from_catalog(csv_file):
    print(f"\n{'='*80}")
    print(f"ОБРАБОТКА: {csv_file}")
    print(f"{'='*80}")
    
    attempts = [
        {'encoding': 'utf-8', 'sep': ';'},
        {'encoding': 'utf-8', 'sep': ','},
        {'encoding': 'cp1251', 'sep': ';'},
        {'encoding': 'cp1251', 'sep': ','},
    ]
    
    for params in attempts:
        try:
            df = pd.read_csv(csv_file, on_bad_lines='skip', **params)
            if len(df.columns) > 5:
                print(f"✓ Прочитано: {len(df)} строк, {len(df.columns)} колонок")
                
                # Показываем первые 5 SKU из каталога
                if 'SKU' in df.columns:
                    print("\nПримеры SKU из каталога:")
                    for i, sku in enumerate(df['SKU'].head(5), 1):
                        print(f"  {i}. '{sku}'")
                
                return df
        except:
            continue
    
    return pd.DataFrame()

def create_master_catalog(source_df, old_offers_dict, output_file='MASTER_CATALOG_RSS.csv'):
    print("\n" + "="*80)
    print("СОЗДАНИЕ ЭТАЛОННОГО КАТАЛОГА")
    print("="*80)
    
    # ВРЕМЕННО ОТКЛЮЧАЕМ ФИЛЬТРАЦИЮ - берем все офферы из каталога
    print(f"\n⚠️  ФИЛЬТРАЦИЯ ОТКЛЮЧЕНА - берём все {len(source_df)} офферов из каталога")
    
    tilda_structure = ['Tilda UID', 'Brand', 'SKU', 'Offers ID', 'Mark', 'Category', 
                       'Title', 'Description', 'Text', 'Photo', 'Price', 'Quantity', 
                       'Price Old', 'Editions', 'Modifications', 'External ID', 
                       'Parent UID', 'Weight', 'Length', 'Width', 'Height', 'Url', 'Tabs:1']
    
    master_df = pd.DataFrame()
    column_mapping = {
        'SKU': 'SKU', 'Title': 'Title', 'Brand': 'Brand', 
        'Category': 'Category', 'Description': 'Description', 
        'Text': 'Text', 'CHPU-TEXT': 'Text', 
        'Photo': 'Photo', 'Price': 'Price', 'Url': 'Url'
    }
    
    for source_col, target_col in column_mapping.items():
        if source_col in source_df.columns and target_col not in master_df.columns:
            master_df[target_col] = source_df[source_col]
    
    for col in tilda_structure:
        if col not in master_df.columns:
            master_df[col] = ''
    
    master_df = master_df[tilda_structure]
    master_df['Tilda UID'] = master_df.apply(
        lambda row: row['SKU'] if pd.isna(row['Tilda UID']) or row['Tilda UID'] == '' 
        else row['Tilda UID'], axis=1
    )
    
    master_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Сохранено: {output_file} ({len(master_df)} офферов)")
    
    # Статистика
    print("\n" + "="*80)
    print("СТАТИСТИКА ЗАПОЛНЕННОСТИ")
    print("="*80)
    for col in ['SKU', 'Title', 'Description', 'Text', 'Photo', 'Price']:
        if col in master_df.columns:
            filled = (master_df[col].notna() & (master_df[col] != '')).sum()
            pct = (filled / len(master_df) * 100) if len(master_df) > 0 else 0
            print(f"{col:15s}: {filled:4d} / {len(master_df):4d} ({pct:5.1f}%)")
    
    return master_df

def main():
    print("="*80)
    print("СОЗДАНИЕ ЭТАЛОННОГО КАТАЛОГА")
    print("="*80)
    
    main_catalog = r'catalogs\TOP-KATALOG-s-prefiksami-i-foto copy 2-CHPU-TEXT.csv'
    
    old_offers_dict = read_old_offers_list('Vse-offery-RSS.txt')
    source_df = extract_offers_from_catalog(main_catalog)
    
    if source_df.empty or len(source_df.columns) < 3:
        print("\n❌ Файл прочитан некорректно!")
        return
    
    master_df = create_master_catalog(source_df, old_offers_dict, 'MASTER_CATALOG_RSS.csv')
    
    if len(master_df) > 0:
        needs_text = master_df[
            (master_df['Text'].isna() | (master_df['Text'] == '')) | 
            (master_df['Description'].isna() | (master_df['Description'] == ''))
        ]
        
        if not needs_text.empty:
            needs_text[['SKU', 'Title', 'Text', 'Description']].to_csv(
                'OFFERS_NEED_TEXT_DESCRIPTION.csv', 
                index=False, 
                encoding='utf-8-sig'
            )
            print(f"\n✓ Требуют заполнения TEXT/Description: {len(needs_text)} офферов")
    
    print("\n" + "="*80)
    print("ГОТОВО!")
    print("="*80)
    print("\nСозданные файлы:")
    print("  1. MASTER_CATALOG_RSS.csv - Эталонный каталог (все офферы)")
    print("  2. OFFERS_NEED_TEXT_DESCRIPTION.csv - Офферы без TEXT/Description")

if __name__ == "__main__":
    main()
