import json
import csv
from pathlib import Path
import logging
import requests
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

TILDA_API_TOKEN = "7d42e65b371ce0800e9a"
TILDA_PROJECT_ID = "17325576"

def upload_file(file_path):
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = requests.post(
                f"https://api.tilda.cc/v1/project/{TILDA_PROJECT_ID}/filestorage/upload",
                headers={"Authorization": f"Bearer {TILDA_API_TOKEN}"},
                files=files,
                timeout=30
            )
        
        if response.status_code in [200, 201]:
            data = response.json()
            if "file" in data and "url" in data["file"]:
                return data["file"]["url"]
            elif "publicUrl" in data:
                return data["publicUrl"]
        return None
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return None

def main():
    root = Path(__file__).parent.parent
    mapping_file = root / "data" / "mappings" / "offer_to_photos.json"
    csv_file = root / "data" / "source" / "ETALONNYI-est-UID-i-SKU.csv"
    output_csv = root / "data" / "normalized" / "catalog_with_tilda_urls.csv"
    
    logger.info("Читаю маппинг...")
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    upload_results = {}
    for i, (uid, data) in enumerate(mapping.items(), 1):
        photos = data.get("photos", [])
        if photos:
            file_path = photos[0]["fullPath"]
            logger.info(f"[{i}] Загружаю: {Path(file_path).name}")
            cdn_url = upload_file(file_path)
            if cdn_url:
                upload_results[uid] = cdn_url
            time.sleep(0.5)
    
    logger.info(f"Успешно загружено: {len(upload_results)}")
    
    rows = []
    fieldnames = []
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = list(reader.fieldnames)
        if "Фото" not in fieldnames:
            fieldnames.append("Фото")
        
        for row in reader:
            uid = row.get("UID", "").strip()
            if "Фото" not in row:
                row["Фото"] = ""
            if uid in upload_results:
                row["Фото"] = upload_results[uid]
            rows.append(row)
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f"CSV сохранен: {output_csv}")

if __name__ == "__main__":
    main()
