import csv

# Путь к вашему исходному файлу
INP = r"C:/GitHub-Repositories/Katalog-RSS/RegTorg-Fis-MashPort/RegTorg_catalog_195_FIXED.csv"
# Путь к файлу-результату
OUT = r"C:/GitHub-Repositories/Katalog-RSS/RegTorg-Fis-MashPort/RegTorg_catalog_195_FOR_REGTORG.csv"

# Точные заголовки и порядок из шаблона
TEMPLATE_HEADERS = [
    'ID_товара',
    'Название',
    'Описание',
    'Ключевые_слова',
    'Цена',
    'Валюта',
    'Единица_измерения',
    'Наличие',
    'Тип_опт_розница',
    'Рубрика',
    'Фотография',
    'Артикул',
    'Производитель',
    'Страна_производитель'
]

# Соответствие для "Рубрика" (можно расширить)
RUBRIKA_MAP = {
    'Патроны токарные': 'Патроны',
    'Револьверные головки': 'Револьверные головки',
    'ШВП': 'ШВП',
    'Суппорты': 'Суппорты',
    'Шпиндели': 'Шпиндели',
    'Люнеты': 'Люнеты',
    'Резцедержатели': 'Резцедержатели',
    'Винты ходовые': 'Винты',
    'Муфты': 'Муфты',
    'Шестерни': 'Шестерни',
    'Кулачки': 'Кулачки',
    'Гайки': 'Гайки',
    'Диски фрикционные': 'Диски',
    'Гайки маточные': 'Гайки маточные',
    'Насосы': 'Насосы',
    'Шкивы': 'Шкивы',
    'Подшипники': 'Подшипники',
    'Электрика': 'Электрика',
    'Ограждения': 'Ограждения',
    'Комплекты': 'Комплекты',
}

def clean_value(val, field):
    if field == 'Наличие':
        return 'в наличии'
    if field == 'Тип_опт_розница':
        return 'опт и розница'
    if field == 'Рубрика':
        return RUBRIKA_MAP.get(val.strip(), val.strip())
    if field == 'Фотография':
        # Оставляем только прямой URL
        return val.strip().split('](')[-1].replace(')', '').replace('[', '')
    if field == 'Единица_измерения':
        return 'шт.'
    if field == 'Валюта':
        return 'руб'
    return val.strip()

with open(INP, newline='', encoding='utf-8-sig') as f_in, open(OUT, 'w', newline='', encoding='utf-8-sig') as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=TEMPLATE_HEADERS)
    writer.writeheader()
    for row in reader:
        new_row = {}
        for h in TEMPLATE_HEADERS:
            val = row.get(h, '')
            new_row[h] = clean_value(val, h)
        writer.writerow(new_row)

print('OK ->', OUT)
