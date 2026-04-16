import os
import xml.etree.ElementTree as ET

YML_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_richdesc.xml"
LOGO_URL = "https://static.tildacdn.com/tild3235-6334-4536-b430-656238613562/logo.png"
CONTACT_BLOCK = '''\n\nООО "ТД РУССтанкоСбыт" имеет отдельные производственные площадки на которых имеются участки по изготовлению станков разных типоразмеров. Контактная информация\n📞 Телефон +7 499 390-85-04\n📧 Email: zakaz@tdrusstankosbyt.ru\n🌐 Сайт tdrusstankosbyt.ru\n📍 Адрес РФ, г. Москва, ул. Берзарина, д. 36, стр. 2\n\nДля получения коммерческого предложения свяжитесь с нашими специалистами'''

SEARCH_DIRS = [
    "ТКП", "docs", "Кinematika-Chertegi", "RegTorg-Fis-MashPort", "MD-Fails"
]

MIN_DESC_LEN = 300  # Минимальная длина описания (символов)


def deep_search_descriptions():
    descriptions = {}
    for search_dir in SEARCH_DIRS:
        if not os.path.isdir(search_dir):
            continue
        for root, _, files in os.walk(search_dir):
            for fname in files:
                if fname.endswith(('.md', '.txt', '.csv')):
                    key = os.path.splitext(fname)[0].lower()
                    try:
                        with open(os.path.join(root, fname), encoding='utf-8') as f:
                            text = f.read().strip()
                            if text:
                                descriptions[key] = text
                    except Exception:
                        continue
    return descriptions

def find_best_description(offer_name, vendor_code, desc_map):
    name_key = offer_name.lower().replace('ё', 'е').replace(' ', '')
    code_key = (vendor_code or '').lower().replace('ё', 'е').replace(' ', '')
    for key, desc in desc_map.items():
        if key in name_key or key in code_key:
            return desc
    return None

def pad_description(desc):
    # Если описание слишком короткое, дополняем шаблонными фразами
    if len(desc) < MIN_DESC_LEN:
        extra = "\n\nДанное изделие предназначено для использования в промышленности. Отличается высокой надежностью и качеством изготовления. Гарантия и сервисное обслуживание предоставляются производителем. Для получения подробной информации и консультации обращайтесь к нашим специалистам."
        desc += extra
    return desc

def main():
    desc_map = deep_search_descriptions()
    tree = ET.parse(YML_PATH)
    root = tree.getroot()
    offers = root.find('.//offers')
    changed = 0
    for offer in offers.findall('offer'):
        name = offer.findtext('name', default='')
        vendor_code = offer.findtext('vendorCode', default='')
        desc_elem = offer.find('description')
        orig_desc = desc_elem.text or ''
        best_desc = find_best_description(name, vendor_code, desc_map)
        if best_desc:
            desc_elem.text = pad_description(best_desc) + CONTACT_BLOCK
            changed += 1
        else:
            desc_elem.text = pad_description(orig_desc.strip()) + CONTACT_BLOCK
        pic_elem = offer.find('picture')
        if pic_elem is None or not (pic_elem.text and pic_elem.text.strip()):
            if pic_elem is None:
                pic_elem = ET.SubElement(offer, 'picture')
            pic_elem.text = LOGO_URL
    tree.write(YML_PATH.replace('.xml', '_deep.xml'), encoding='utf-8', xml_declaration=True)
    print(f"Готово! Офферов с подробным описанием из репозитория: {changed}. Файл сохранён как *_deep.xml")

if __name__ == "__main__":
    main()
