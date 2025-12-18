import json, csv
from pathlib import Path
import logging, requests, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

UPLOADCARE_PUBLIC_KEY = "8me9b2pgwhgrw6l71fcl"
UPLOADCARE_UPLOAD_URL = "https://upload.uploadcare.com/base/"

def upload_to_uploadcare(file_path):
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            data = {"UPLOADCARE_PUB_KEY": UPLOADCARE_PUBLIC_KEY}
            response = requests.post(UPLOADCARE_UPLOAD_URL, files=files, data=data, timeout=30)
        
        if response.status_code in [200, 201]:
            resp_data = response.json()
            if "file" in resp_data:
                file_id = resp_data["file"].get("id")
                if file_id:
                    return f"https://ucarecdn.com/{file_id}/"
        return None
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return None

def main():
    root = Path(__file__).parent.parent
    mapping_file = root / "data" / "mappings" / "offer_to_photos.json"
    csv_file = root / "data" / "source" / "ETALONNYI-est-UID-i-SKU.csv"
    output_csv = root / "data" / "normalized" / "catalog_with_cdn_urls.csv"
    
    logger.info("ЗАГРУЗКА НА UPLOADCARE CDN")
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    upload_results = {}
    for i, (uid, data) in enumerate(mapping.items(), 1):
        photos = data.get("photos", [])
        if photos:
            file_path = photos[0]["fullPath"]
            file_name = photos[0]["fileName"]
            logger.info(f"[{i}/{len(mapping)}] {file_name[:40]}")
            cdn_url = upload_to_uploadcare(file_path)
            if cdn_url:
                upload_results[uid] = cdn_url
            time.sleep(0.3)
    
    logger.info(f"Загружено: {len(upload_results)}")
    
    rows = []
    fieldnames = []
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
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
    
    logger.info(f" CSV сохранен: {output_csv}")

if __name__ == "__main__":
    main()
