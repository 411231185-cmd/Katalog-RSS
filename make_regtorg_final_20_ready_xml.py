import pandas as pd
from lxml import etree
import os
from datetime import datetime
import random

src = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_200.xlsx'
dst = 'RegTorg-Fis-MashPort/RegTorg_catalog_FINAL_20_ready.xml'

# Читаем эталонный каталог
df = pd.read_excel(src)

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
    etree.SubElement(offer, 'description').text = str(row['Описание']) if pd.notnull(row['Описание']) else f"{row['Название']} — описание по запросу."
    etree.SubElement(offer, 'vendor').text = 'ТД РУССтанкоСбыт'
    etree.SubElement(offer, 'vendorCode').text = str(row['Артикул'])
    etree.SubElement(offer, 'country_of_origin').text = 'Россия'

# Сохраняем XML с декларацией и DOCTYPE
doctype = '<!DOCTYPE yml_catalog SYSTEM "shops.dtd">\n'
xml_bytes = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
with open(dst, 'wb') as f:
    f.write(xml_bytes.replace(b'?>', b'?>\n' + doctype.encode('utf-8'), 1))
print(f'XML YML сохранён: {os.path.abspath(dst)}')
