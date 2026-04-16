import xml.etree.ElementTree as ET
import re

YML_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200.xml"
YML_OUT_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_linked.xml"

# Список для перелинковки (можно расширить)
SEE_ALSO = '''16М30Ф3, 16А20Ф3, РТ755Ф3, РТ305М, РТ779Ф3, РТ5001, РТ5003, РТ5004, РТ301.01, РТ301.02, РТ301, РТ917, 16К20, 16К40, 16Р25, 1М63Н, 1М63, 163, ДИП-300, ДИП300, 1Н65, 165, 1М65, ДИП-500, ДИП500, РТ117, РТ817, 1А983, 1Н983, РТ783, резцовый блок, коробки подач, ШВП, валы, шпиндельные бабки, задние бабки, винты, рейки, каретка, суппорт, муфты обгонные, гайки маточные, гайки, фрикцион, диски, колеса конические, колеса зубчатые, червячные пары, фрикционные муфты, патроны, кулачки, венцы, ползушки, сухари, револьверные головки, ремонт'''

# Функция для генерации HTML-блока перелинковки
def make_see_also_block():
    items = [x.strip() for x in SEE_ALSO.split(',') if x.strip()]
    links = []
    for item in items:
        url = f"http://testshop.ru/search?q={item.replace(' ', '+')}"
        links.append(f'<a href="{url}">{item}</a>')
    return '<br>Смотрите также: ' + ', '.join(links)

# Основная обработка

tree = ET.parse(YML_PATH)
root = tree.getroot()
offers = root.find('shop').find('offers')
see_also_html = make_see_also_block()

for offer in offers:
    desc = offer.find('description')
    if desc is not None:
        text = desc.text or ''
        # Удаляем старый блок "Смотрите также" если был
        text = re.sub(r'Смотрите также:.*', '', text, flags=re.S)
        # Добавляем новый HTML-блок
        desc.text = text.strip() + '\n' + see_also_html

ET.indent(tree, space="  ")
tree.write(YML_OUT_PATH, encoding='utf-8', xml_declaration=True)
print(f"YML с HTML-перелинковкой сохранён в {YML_OUT_PATH}")
