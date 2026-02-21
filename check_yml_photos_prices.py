import xml.etree.ElementTree as ET

YML_PATH = r"RegTorg-Fis-MashPort/YML/RegTorg_catalog_FINAL_200_linked_img_fixed.xml"
DEFAULT_PIC = "https://static.tildacdn.com/tild6132-3937-4437-b964-393263393964/logo_russtanko.png"

missing_photo = []
wrong_price = []

try:
    tree = ET.parse(YML_PATH)
    root = tree.getroot()
    offers = root.find('shop').find('offers')
    for offer in offers:
        offer_id = offer.attrib.get('id', 'NO_ID')
        name = offer.findtext('name', 'NO_NAME')
        pic = offer.find('picture')
        price = offer.findtext('price', '').strip()
        # Проверка фото
        if pic is None or not pic.text or not pic.text.strip():
            missing_photo.append(f"{offer_id}: {name}")
        # Проверка цены (должна быть положительным числом)
        try:
            price_val = float(price.replace(',', '.'))
            if price_val <= 0:
                wrong_price.append(f"{offer_id}: {name} — {price}")
        except Exception:
            wrong_price.append(f"{offer_id}: {name} — {price}")
except Exception as e:
    print(f"Ошибка при разборе YML: {e}")

with open("photo_check_report.txt", "w", encoding="utf-8") as f:
    f.write("Офферы без фото (или пустое фото):\n")
    f.write("\n".join(missing_photo) or "Нет таких офферов!\n")
    f.write("\n\nОфферы с некорректной ценой:\n")
    f.write("\n".join(wrong_price) or "Нет таких офферов!\n")

print("Проверка завершена. Отчёт: photo_check_report.txt")
