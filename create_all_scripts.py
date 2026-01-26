# Сохраните это как create_all_scripts.py
import os

scripts = {
    'extract_offers_create_master.py': '''import pandas as pd
import os
from pathlib import Path

def read_old_offers_list(file_path='Vse-offery-RSS.txt'):
    """Чтение старого списка офферов из текстового файла"""
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
                        sku = sku.strip()
                        title = title.strip()
                        offers_dict[sku] = title
        
        print(f"Загружено {len(offers_dict)} офферов из старого файла")
        return offers_dict
        
    except FileNotFoundError:
        print(f"⚠️  Файл {file_path} не найден!")
        return {}
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return {}

def extract_offers_from_catalog(csv_file):
    """Извлечение офферов из каталога"""
    print(f"\\n{'='*80}")
    print(f"ОБРАБОТКА: {csv_file}")
    print(f"{'='*80}")
    
    try:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except:
            try:
                df = pd.read_csv(csv_file, encoding='cp1251')
            except:
                df = pd.read_csv(csv_file, encoding='latin1')
        
        print(f"Всего строк: {len(df)}")
        print(f"Колонок: {len(df.columns)}")
        return df
        
    except Exception as e:
        print(f"❌ Ошибка обработки файла: {e}")
        return pd.DataFrame()

def create_master_catalog(source_df, old_offers_dict, output_file='MASTER_CATALOG_RSS.csv'):
    """Создание эталонного каталога по структуре Tilda"""
    
    print("\\n" + "="*80)
    print("СОЗДАНИЕ ЭТАЛОННОГО КАТАЛОГА")
    print("="*80)
    
    if 'SKU' in source_df.columns and old_offers_dict:
        print(f"\\nСтрок до фильтрации: {len(source_df)}")
        source_df = source_df[source_df['SKU'].isin(old_offers_dict.keys())]
        print(f"Строк после фильтрации: {len(source_df)}")
    
    tilda_structure = [
        'Tilda UID', 'Brand', 'SKU', 'Offers ID', 'Mark', 'Category',
        'Title', 'Description', 'Text', 'Photo', 'Price', 'Quantity',
        'Price Old', 'Editions', 'Modifications', 'External ID',
        'Parent UID', 'Weight', 'Length', 'Width', 'Height', 'Url', 'Tabs:1'
    ]
    
    master_df = pd.DataFrame()
    
    column_mapping = {
        'SKU': 'SKU', 'Title': 'Title', 'Brand': 'Brand',
        'Category': 'Category', 'Description': 'Description',
        'Text': 'Text', 'CHPU-TEXT': 'Text', 'Photo': 'Photo',
        'Price': 'Price', 'URL': 'Url', 'Url': 'Url'
    }
    
    for source_col, target_col in column_mapping.items():
        if source_col in source_df.columns:
            master_df[target_col] = source_df[source_col]
    
    for col in tilda_structure:
        if col not in master_df.columns:
            master_df[col] = ''
    
    master_df = master_df[tilda_structure]
    
    if 'Tilda UID' in master_df.columns and 'SKU' in master_df.columns:
        master_df['Tilda UID'] = master_df.apply(
            lambda row: row['SKU'] if pd.isna(row['Tilda UID']) or row['Tilda UID'] == '' 
            else row['Tilda UID'], axis=1
        )
    
    master_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\\n✓ Эталонный каталог сохранён: {output_file}")
    print(f"Всего офферов: {len(master_df)}")
    
    return master_df

def main():
    print("=" * 80)
    print("СОЗДАНИЕ ЭТАЛОННОГО КАТАЛОГА ДЛЯ TILDA")
    print("=" * 80)
    
    main_catalog = r'catalogs\\TOP-KATALOG-s-prefiksami-i-foto copy 2-CHPU-TEXT.csv'
    old_offers_file = 'Vse-offery-RSS.txt'
    
    if not os.path.exists(main_catalog):
        print(f"❌ Файл не найден: {main_catalog}")
        return
    
    old_offers_dict = read_old_offers_list(old_offers_file)
    source_df = extract_offers_from_catalog(main_catalog)
    
    if source_df.empty:
        print("\\n❌ Нет данных!")
        return
    
    master_df = create_master_catalog(source_df, old_offers_dict, 'MASTER_CATALOG_RSS.csv')
    
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
        print(f"\\n✓ Офферов требующих заполнения: {len(needs_text)}")
    
    print("\\n" + "="*80)
    print("ГОТОВО!")
    print("="*80)

if __name__ == "__main__":
    main()
''',

    'check_tkp_descriptions.py': '''import pandas as pd
from pathlib import Path

def analyze_catalog_tkp(csv_file):
    print(f"\\n{'='*80}")
    print(f"Анализ файла: {csv_file}")
    print(f"{'='*80}\\n")
    
    try:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except:
            df = pd.read_csv(csv_file, encoding='cp1251')
        
        print(f"Всего строк: {len(df)}\\n")
        
        tkp_columns = [col for col in df.columns if 'ткп' in col.lower() or 'tkp' in col.lower()]
        desc_columns = [col for col in df.columns if 'описан' in col.lower() or 'description' in col.lower()]
        
        if tkp_columns:
            print("ТКП колонки:")
            for col in tkp_columns:
                filled = df[col].notna().sum()
                print(f"  {col}: {filled} заполнено ({filled/len(df)*100:.1f}%)")
        
        if desc_columns:
            print("\\nОписания:")
            for col in desc_columns:
                filled = df[col].notna().sum()
                print(f"  {col}: {filled} заполнено ({filled/len(df)*100:.1f}%)")
        
        return df
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def main():
    print("="*80)
    print("ДИАГНОСТИКА ТКП И ОПИСАНИЙ")
    print("="*80)
    
    csv_files = list(Path('.').rglob('*.csv'))
    
    for csv_file in csv_files[:5]:
        analyze_catalog_tkp(str(csv_file))

if __name__ == "__main__":
    main()
''',

    'check_unused_files.py': '''import os
from pathlib import Path

def find_unused_files():
    print("="*80)
    print("ПОИСК ЛИШНИХ ФАЙЛОВ")
    print("="*80)
    
    unnecessary = ['page101046196.html', '404.html', 'htaccess']
    
    found = []
    for filename in unnecessary:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            found.append((filename, size))
            print(f"❌ {filename} ({size} bytes)")
    
    if not found:
        print("✓ Лишних файлов не найдено")
    
    print(f"\\n{'='*80}")
    print("Python скрипты:")
    for py in Path('.').glob('*.py'):
        print(f"  - {py}")

if __name__ == "__main__":
    find_unused_files()
''',

    'check_git_health.py': '''import subprocess

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Ошибка: {e}"

def check_git():
    print("="*80)
    print("GIT ДИАГНОСТИКА")
    print("="*80)
    
    print("\\nТекущая ветка:")
    print(run_cmd("git branch --show-current"))
    
    print("\\nНезакоммиченные изменения:")
    status = run_cmd("git status --short")
    print(status if status else "✓ Нет изменений")
    
    print("\\nПоследние 5 коммитов:")
    print(run_cmd("git log --oneline -5"))

if __name__ == "__main__":
    check_git()
''',

    'compare_with_website.py': '''import requests

def check_website():
    print("="*80)
    print("ПРОВЕРКА САЙТОВ")
    print("="*80)
    
    sites = [
        'https://rosstanko.com',
        'https://russtanko-rzn.ru',
        'https://tdrusstankosbyt.ru'
    ]
    
    for site in sites:
        try:
            response = requests.get(site, timeout=10)
            print(f"\\n{site}: {response.status_code}")
        except Exception as e:
            print(f"\\n{site}: Ошибка - {e}")

if __name__ == "__main__":
    check_website()
'''
}

# Создаём все скрипты
os.chdir(r'C:\GitHub-Repositories\Katalog-RSS')

for filename, content in scripts.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Создан: {filename}")

print("\n" + "="*80)
print("ВСЕ СКРИПТЫ СОЗДАНЫ!")
print("="*80)
print("\nЗапустите: python extract_offers_create_master.py")
