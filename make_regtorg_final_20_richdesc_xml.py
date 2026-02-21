import pandas as pd
from lxml import etree
import os
from datetime import datetime
import random
import re

# Путь к эталонному каталогу и файлу с описаниями
src = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_200.xlsx'
desc_path = 'Kinematika-Chertegi/Uzly_stankov_polniy_katalog_TD_RUSStankoSbyt.md'
dst = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_20_richdesc.xml'

# Перелинковка (можно заменить на HTML-ссылки при необходимости)
perelink = '''<br><br>16М30Ф3, 16А20Ф3, РТ755Ф3, РТ305М, РТ779Ф3, РТ5001, РТ5003, РТ5004, РТ301.01, РТ301.02, РТ301, РТ917, 16К20, 16К40, 16Р25, 1М63Н, 1М63, 163, ДИП-300, ДИП300, 1Н65, 165, 1М65, ДИП-500, ДИП500, РТ117, РТ817, 1А983, 1Н983, РТ783, шестерни, резцовый блок, коробки подач, ШВП, валы, шпиндельные бабки, задние бабки, винты, рейки, каретка, суппорт, муфты обгонные, гайки маточные, гайки, фрикцион, диски, колеса конические, колеса зубчатые, червячные пары, фрикционные муфты, патроны, кулачки, венцы, ползушки, сухари, револьверные головки, ремонт'''

# Читаем эталонный каталог
df = pd.read_excel(src)

# Читаем файл с описаниями
with open(desc_path, encoding='utf-8') as f:
    desc_text = f.read()

# Оставляем только первые 20 уникальных позиций с фото (или логотипом)
df = df[df['Фотография'].notnull() & (df['Фотография'] != '')].head(20).copy()

# Генерируем уникальные id, артикулы, url, названия (добавляем суффикс)
base_id = random.randint(100000, 999999)
for i in range(len(df)):
    df.at[df.index[i], 'ID_товара'] = base_id + i
    df.at[df.index[i], 'Артикул'] = f"TEST-{base_id + i}"
    df.at[df.index[i], 'Название'] = f"{df.at[df.index[i], 'Название']} (YML{str(base_id + i)[-4:]})"

# Собираем уникальные категории
categories = df['Рубрика'].unique()
category_map = {cat: str(i+1) for i, cat in enumerate(categories)}

# Функция поиска описания по ключевым словам
def find_description(name):
    # Ищем по названию (точное или частичное совпадение)
    for line in desc_text.split('\n'):
        if name.split()[0] in line or name in line:
            # Собираем 5-10 предложений после совпадения
            idx = desc_text.find(line)
            chunk = desc_text[idx:idx+1200]  # 1200 символов после совпадения
            sentences = re.split(r'(?<=[.!?]) +', chunk)
            return ' '.join(sentences[:8])
    return ''

# Корневой элемент
root = etree.Element('yml_catalog', date=datetime.now().strftime('%Y-%m-%d %H:%M'))
shop = etree.SubElement(root, 'shop')

# Магазин
etree.SubElement(shop, 'name').text = 'Test Shop'
etree.SubElement(shop, 'company').text = 'ТД РУССтанкоСбыт'
etree.SubElement(shop, 'url').text = 'http://testshop.ru/'

# Валюты
currencies = etree.SubElement(shop, 'currencies')
etree.SubElement(currencies, 'currency', id='RUB', rate='1')

# Категории
categories_el = etree.SubElement(shop, 'categories')
for cat, cid in category_map.items():
    etree.SubElement(categories_el, 'category', id=cid).text = str(cat)

# Офферы
offers = etree.SubElement(shop, 'offers')
for _, row in df.iterrows():
    offer = etree.SubElement(offers, 'offer', id=str(row['ID_товара']), available='true')
    etree.SubElement(offer, 'url').text = f"http://testshop.ru/p{row['ID_товара']}"
    etree.SubElement(offer, 'price').text = str(row['Цена']) if pd.notnull(row['Цена']) else 'по запросу'
    etree.SubElement(offer, 'currencyId').text = 'RUB'
    etree.SubElement(offer, 'categoryId').text = category_map.get(row['Рубрика'], '1')
    etree.SubElement(offer, 'picture').text = str(row['Фотография'])
    etree.SubElement(offer, 'name').text = str(row['Название'])
    # Описание: подробное + перелинковка
    desc = find_description(row['Название'])
    if not desc:
        desc = str(row['Описание']) if pd.notnull(row['Описание']) else f"{row['Название']} — описание по запросу."
    etree.SubElement(offer, 'description').text = desc + perelink
    etree.SubElement(offer, 'vendor').text = 'ТД РУССтанкоСбыт'
    etree.SubElement(offer, 'vendorCode').text = str(row['Артикул'])
    etree.SubElement(offer, 'country_of_origin').text = 'Россия'

# Сохраняем XML с декларацией и DOCTYPE
doctype = '<!DOCTYPE yml_catalog SYSTEM "shops.dtd">\n'
xml_bytes = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
with open(dst, 'wb') as f:
    f.write(xml_bytes.replace(b'?>', b'?>\n' + doctype.encode('utf-8'), 1))
print(f'XML YML сохранён: {os.path.abspath(dst)}')
