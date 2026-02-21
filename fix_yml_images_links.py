import xml.etree.ElementTree as ET
import re

YML_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200.xml"
YML_OUT_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_fixed.xml"
DEFAULT_PIC = "https://static.tildacdn.com/tild6132-3937-4437-b964-393263393964/logo_russtanko.png"

# Ключевые слова для перелинковки и шаблоны ссылок (пример)
LINKS = {
    'патрон': 'http://testshop.ru/cat/patrony',
    'револьверная головка': 'http://testshop.ru/cat/revolver',
    'швп': 'http://testshop.ru/cat/shvp',
    'суппорт': 'http://testshop.ru/cat/support',
    'шпиндель': 'http://testshop.ru/cat/shpindel',
    'резцедержатель': 'http://testshop.ru/cat/rezcoderzh',
    'винт': 'http://testshop.ru/cat/vint',
    'люнет': 'http://testshop.ru/cat/lynet',
    'муфта': 'http://testshop.ru/cat/mufta',
    'шестерня': 'http://testshop.ru/cat/shesterni',
}

# Функция для добавления дефолтного фото
def ensure_picture(offer):
    pic = offer.find('picture')
    if pic is None or not pic.text or not pic.text.strip():
        new_pic = ET.Element('picture')
        new_pic.text = DEFAULT_PIC
        offer.insert(offer.getchildren().index(offer.find('name'))+1, new_pic)
    return offer

# Функция для перелинковки в описании
def add_links_to_description(desc):
    text = desc.text or ''
    for word, url in LINKS.items():
        # Только если нет уже ссылки
        if word in text and f'<a href="{url}"' not in text:
            text = re.sub(f'({word})', rf'<a href="{url}">\1</a>', text, flags=re.I)
    desc.text = text
    return desc

# Основная обработка

tree = ET.parse(YML_PATH)
root = tree.getroot()
offers = root.find('shop').find('offers')

for offer in offers:
    offer = ensure_picture(offer)
    desc = offer.find('description')
    if desc is not None:
        desc = add_links_to_description(desc)

# Сохраняем результат
ET.indent(tree, space="  ")
tree.write(YML_OUT_PATH, encoding='utf-8', xml_declaration=True)
print(f"YML с фото и перелинковкой сохранён в {YML_OUT_PATH}")
