import pandas as pd
import json
from pathlib import Path
from transliterate import translit

# Пути к файлам
CATALOG_CSV = Path('catalogs/FINAL_TILDA_CATALOG.csv')
PERELINKOVKA_MD = Path('catalogs/Perelinkovka.md')
PAGES_DIR = Path('catalogs/pages')
PAGES_MD_DIR = Path('catalogs/pages_md')
PAGES_HTML_DIR = Path('catalogs/pages_html')
PAGES_DIR.mkdir(exist_ok=True)
PAGES_MD_DIR.mkdir(exist_ok=True)
PAGES_HTML_DIR.mkdir(exist_ok=True)

# 1. Чтение существующих страниц
with open(PERELINKOVKA_MD, encoding='utf-8') as f:
    existing_urls = set(line.strip() for line in f if line.strip())

# 2. Чтение каталога офферов
catalog = pd.read_csv(CATALOG_CSV)

# 3. Генерация alias и фильтрация офферов без страниц
def make_alias(name):
    alias = translit(name, 'ru', reversed=True)
    alias = alias.lower().replace(' ', '').replace('–', '').replace('—', '').replace('.', '').replace(',', '').replace('/', '').replace('(', '').replace(')', '').replace('"', '').replace("'", '')
    return alias

catalog['url_alias'] = catalog['title'].apply(make_alias)
missing_offers = catalog[~catalog['url_alias'].isin(existing_urls)]
missing_offers = missing_offers.head(100)

# 4. Генерация файлов для каждого оффера
for _, row in missing_offers.iterrows():
    data = {
        'url_alias': row['url_alias'],
        'title': row.get('title', ''),
        'subtitle': row.get('subtitle', ''),
        'description': row.get('description', ''),
        'specifications': row.get('specifications', '{}'),
        'complectation': row.get('complectation', '[]'),
        'advantages': row.get('advantages', '[]'),
        'photos': row.get('photos', '[]'),
        'price': row.get('price', 'По запросу'),
        'related_products': row.get('related_products', '[]'),
    }
    # JSON
    with open(PAGES_DIR / f"{data['url_alias']}.json", 'w', encoding='utf-8') as jf:
        json.dump(data, jf, ensure_ascii=False, indent=2)
    # Markdown
    with open(PAGES_MD_DIR / f"{data['url_alias']}.md", 'w', encoding='utf-8') as mf:
        mf.write(f"# {data['title']}\n\n{data['description']}")
    # HTML (минимальный шаблон)
    with open(PAGES_HTML_DIR / f"{data['url_alias']}.html", 'w', encoding='utf-8') as hf:
        hf.write(f"<h1>{data['title']}</h1>\n<p>{data['description']}</p>")

# 5. CSV для импорта
missing_offers.to_csv('catalogs/TILDA_IMPORT_100_PAGES.csv', index=False, encoding='utf-8')

print('Генерация завершена. Создано файлов:', len(missing_offers))
