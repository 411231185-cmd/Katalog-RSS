import os
import xml.etree.ElementTree as ET

YML_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_richdesc.xml"
TKP_DIR = r"ТКП"
LOGO_URL = "https://static.tildacdn.com/tild3235-6334-4536-b430-656238613562/logo.png"
CONTACT_BLOCK = '''\n\nООО "ТД РУССтанкоСбыт" имеет отдельные производственные площадки на которых имеются участки по изготовлению станков разных типоразмеров. Контактная информация\n📞 Телефон +7 499 390-85-04\n📧 Email: zakaz@tdrusstankosbyt.ru\n🌐 Сайт tdrusstankosbyt.ru\n📍 Адрес РФ, г. Москва, ул. Берзарина, д. 36, стр. 2\n\nДля получения коммерческого предложения свяжитесь с нашими специалистами'''

def load_tkp_descriptions():
    descriptions = {}
    for fname in os.listdir(TKP_DIR):
        if fname.endswith('.md') or fname.endswith('.txt'):
            key = os.path.splitext(fname)[0].lower()
            with open(os.path.join(TKP_DIR, fname), encoding='utf-8') as f:
                text = f.read().strip()
                if text:
                    descriptions[key] = text
    return descriptions

def find_best_description(offer_name, vendor_code, tkp_descs):
    # Поиск по названию или vendorCode (без пробелов, в нижнем регистре)
    name_key = offer_name.lower().replace('ё', 'е').replace(' ', '')
    code_key = (vendor_code or '').lower().replace('ё', 'е').replace(' ', '')
    for key, desc in tkp_descs.items():
        if key in name_key or key in code_key:
            return desc
    return None

def main():
    tkp_descs = load_tkp_descriptions()
    tree = ET.parse(YML_PATH)
    root = tree.getroot()
    offers = root.find('.//offers')
    changed = 0
    for offer in offers.findall('offer'):
        name = offer.findtext('name', default='')
        vendor_code = offer.findtext('vendorCode', default='')
        desc_elem = offer.find('description')
        orig_desc = desc_elem.text or ''
        best_desc = find_best_description(name, vendor_code, tkp_descs)
        if best_desc:
            desc_elem.text = best_desc + CONTACT_BLOCK
            changed += 1
        else:
            if CONTACT_BLOCK.strip() not in orig_desc:
                desc_elem.text = orig_desc.strip() + CONTACT_BLOCK
        pic_elem = offer.find('picture')
        if pic_elem is None or not (pic_elem.text and pic_elem.text.strip()):
            if pic_elem is None:
                pic_elem = ET.SubElement(offer, 'picture')
            pic_elem.text = LOGO_URL
    tree.write(YML_PATH.replace('.xml', '_fixed.xml'), encoding='utf-8', xml_declaration=True)
    print(f"Готово! Офферов с подробным описанием из ТКП: {changed}. Файл сохранён как *_fixed.xml")

if __name__ == "__main__":
    main()
