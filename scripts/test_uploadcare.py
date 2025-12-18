import requests
import json
from pathlib import Path

UPLOADCARE_PUBLIC_KEY = "8me9b2pgwhgrw6l71fcl"
UPLOADCARE_UPLOAD_URL = "https://upload.uploadcare.com/base/"

# Берем первое фото для теста
mapping_file = Path("C:\Dev\Katalog-RSS") / "data" / "mappings" / "offer_to_photos.json"
with open(mapping_file, "r", encoding="utf-8") as f:
    mapping = json.load(f)

first_uid = list(mapping.keys())[0]
first_photo = mapping[first_uid]["photos"][0]
file_path = first_photo["fullPath"]

print(f"Тестовый файл: {file_path}")
print(f"Существует: {Path(file_path).exists()}")

# Пробуем загрузить
with open(file_path, "rb") as f:
    files = {"file": (Path(file_path).name, f)}
    data = {"UPLOADCARE_PUB_KEY": UPLOADCARE_PUBLIC_KEY}
    
    response = requests.post(UPLOADCARE_UPLOAD_URL, files=files, data=data, timeout=30)

print(f"\nКод ответа: {response.status_code}")
print(f"Полный ответ:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
