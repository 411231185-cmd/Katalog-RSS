import xml.etree.ElementTree as ET

YML_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_linked_img.xml"
YML_OUT_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_linked_img_fixed.xml"
DEFAULT_PIC = "https://static.tildacdn.com/tild6132-3937-4437-b964-393263393964/logo_russtanko.png"

tree = ET.parse(YML_PATH)
root = tree.getroot()
offers = root.find('shop').find('offers')

for offer in offers:
    pic = offer.find('picture')
    if pic is None or not pic.text or not pic.text.strip():
        new_pic = ET.Element('picture')
        new_pic.text = DEFAULT_PIC
        # Вставить после <name>
        name_idx = [i for i, el in enumerate(offer) if el.tag == 'name']
        if name_idx:
            offer.insert(name_idx[0]+1, new_pic)
        else:
            offer.append(new_pic)

ET.indent(tree, space="  ")
tree.write(YML_OUT_PATH, encoding='utf-8', xml_declaration=True)
print(f"YML с фото для всех офферов сохранён в {YML_OUT_PATH}")
