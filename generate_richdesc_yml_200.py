import csv
import xml.etree.ElementTree as ET
from collections import defaultdict
import re

# Пути к файлам
CSV_PATH = r"RegTorg-Fis-MashPort/XLSX/RegTorg_catalog_FINAL_200.csv"
TXT_PATH = r"RegTorg-Fis-MashPort/Пример-rfnfkju.TXT"
YML_ETALON_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_20_richdesc.xml"
REPORT_MD_PATH = r"RegTorg-Fis-MashPort/Узлы, детали и цены.md"
YML_OUT_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_richdesc.xml"

# Ключевые слова для топ-узлов (можно расширить)
TOP_NODES = [
    'суппорт', 'револьвер', 'патрон', 'швп', 'шпиндель', 'резцедерж', 'винт', 'люнет',
    'гайка', 'муфта', 'шестерн', 'кулачк', 'вал', 'насос', 'диск', 'опора', 'шкив', 'каретка', 'фартук'
]

# 1. Чтение эталонного YML (20 офферов)
def get_etalon_offers():
    tree = ET.parse(YML_ETALON_PATH)
    root = tree.getroot()
    offers = root.find('shop').find('offers')
    etalon = []
    for offer in offers:
        etalon.append(ET.tostring(offer, encoding='unicode'))
    return etalon

# 2. Чтение TXT для обогащения
def load_txt_enrichment():
    enrich = {}
    with open(TXT_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            key = row.get('Артикул') or row.get('ID_товара') or row.get('Название')
            if key:
                enrich[key.strip()] = row
    return enrich

# 3. Чтение CSV и отбор топ-180 по цене и ключевым словам
def select_top_180(csv_path, top_nodes, etalon_vendor_codes):
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Фильтрация по ключевым словам и исключение эталонных
    filtered = []
    for row in rows:
        name = row['Название'].lower()
        art = row.get('Артикул', '').strip()
        if art in etalon_vendor_codes:
            continue
        if any(node in name for node in top_nodes):
            filtered.append(row)
    # Сортировка по цене (убывание)
    filtered.sort(key=lambda r: float(re.sub(r'[^\d.]', '', r['Цена'] or '0')), reverse=True)
    # Если не хватает, добираем остальными дорогими
    if len(filtered) < 180:
        rest = [r for r in rows if r not in filtered and r.get('Артикул', '').strip() not in etalon_vendor_codes]
        rest.sort(key=lambda r: float(re.sub(r'[^\d.]', '', r['Цена'] or '0')), reverse=True)
        filtered += rest[:180-len(filtered)]
    return filtered[:180]

# 4. Генерация YML-оффера по шаблону эталона
def make_offer(row, enrich_row, offer_id, category_map):
    # Минимальный набор полей, остальные можно доработать по эталону
    name = row['Название']
    price = row['Цена']
    currency = 'RUB'
    category = category_map.get(row['Рубрика'], '1')
    picture = row['Фотография']
    description = enrich_row.get('Описание') or row['Описание']
    vendor = row['Производитель'] or 'ТД РУССтанкоСбыт'
    vendorCode = row['Артикул'] or row['ID_товара']
    country = row['Страна_производитель'] or 'Россия'
    availability = 'в розницу' if 'в наличии' in (row['Наличие'] or '').lower() else 'под заказ'
    # Формируем XML
    offer = f'''
      <offer id="{offer_id}">
        <url>http://testshop.ru/p{offer_id}</url>
        <price>{price}</price>
        <currencyId>{currency}</currencyId>
        <categoryId>{category}</categoryId>
        <picture>{picture}</picture>
        <name>{name}</name>
        <description>{description}</description>
        <vendor>{vendor}</vendor>
        <vendorCode>{vendorCode}</vendorCode>
        <country_of_origin>{country}</country_of_origin>
        <availability>{availability}</availability>
      </offer>'''
    return offer

# 5. Получить маппинг рубрик на категории из эталона
def get_category_map():
    tree = ET.parse(YML_ETALON_PATH)
    root = tree.getroot()
    cats = root.find('shop').find('categories')
    mapping = {}
    for cat in cats:
        mapping[cat.text.strip()] = cat.attrib['id']
    return mapping

# 6. Основная сборка YML
def main():
    etalon_offers = get_etalon_offers()
    etalon_vendor_codes = set()
    for offer_xml in etalon_offers:
        m = re.search(r'<vendorCode>(.*?)</vendorCode>', offer_xml)
        if m:
            etalon_vendor_codes.add(m.group(1))
    enrich = load_txt_enrichment()
    category_map = get_category_map()
    top180 = select_top_180(CSV_PATH, TOP_NODES, etalon_vendor_codes)
    offers_xml = etalon_offers[:]
    offer_id = 200000
    for row in top180:
        key = row.get('Артикул') or row.get('ID_товара') or row.get('Название')
        enrich_row = enrich.get(key.strip(), {})
        offers_xml.append(make_offer(row, enrich_row, offer_id, category_map))
        offer_id += 1
    # Сборка итогового YML
    with open(YML_ETALON_PATH, encoding='utf-8') as f:
        yml = f.read()
    offers_block = '\n'.join(offers_xml)
    yml_out = re.sub(r'<offers>[\s\S]*?</offers>', f'<offers>\n{offers_block}\n</offers>', yml)
    with open(YML_OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(yml_out)
    print(f'YML на 200 офферов сохранён в {YML_OUT_PATH}')

if __name__ == '__main__':
    main()
