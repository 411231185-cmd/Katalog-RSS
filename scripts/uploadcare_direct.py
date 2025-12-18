import json, csv
from pathlib import Path
import logging, requests, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

UPLOADCARE_PUBLIC_KEY = "8me9b2pgwhgrw6l71fcl"
UPLOADCARE_API_URL = "https://upload.uploadcare.com/upload/"

def upload_to_uploadcare_direct(file_path):
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            data = {
                "UPLOADCARE_PUB_KEY": UPLOADCARE_PUBLIC_KEY,
                "UPLOADCARE_STORE": "1"
            }
            response = requests.post(UPLOADCARE_API_URL, files=files, data=data, timeout=60)
        
        logger.info(f"Статус: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                resp_json = response.json()
                logger.info(f"Ответ: {str(resp_json)[:100]}")
                
                if "file" in resp_json:
                    file_id = resp_json["file"]
                    cdn_url = f"https://ucarecdn.com/{file_id}/"
                    logger.info(f" {file_path.name[:40]}  {file_id}")
                    return cdn_url
                elif "id" in resp_json:
                    file_id = resp_json["id"]
                    cdn_url = f"https://ucarecdn.com/{file_id}/"
                    logger.info(f" {file_path.name[:40]}  {file_id}")
                    return cdn_url
            except:
                logger.warning(f"Ошибка парса: {response.text[:100]}")
                return None
        else:
            logger.error(f"Ошибка {response.status_code}: {response.text[:100]}")
            return None
    except Exception as e:
        logger.error(f"Исключение: {e}")
        return None

def main():
    root = Path(__file__).parent.parent
    mapping_file = root / "data" / "mappings" / "offer_to_photos.json"
    csv_file = root / "data" / "source" / "ETALONNYI-est-UID-i-SKU.csv"
    output_csv = root / "data" / "normalized" / "catalog_with_cdn_urls.csv"
    
    logger.info("ЗАГРУЗКА НА UPLOADCARE CDN")
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    logger.info(f"Офферов: {len(mapping)}")
    
    upload_results = {}
    successful = 0
    
    for i, (uid, data) in enumerate(mapping.items(), 1):
        photos = data.get("photos", [])
        if photos:
            file_path = photos[0]["fullPath"]
            file_name = photos[0]["fileName"]
            logger.info(f"[{i}/{len(mapping)}] {file_name[:50]}")
            cdn_url = upload_to_uploadcare_direct(file_path)
            if cdn_url:
                upload_results[uid] = cdn_url
                successful += 1
            time.sleep(0.5)
    
    logger.info(f"Успешно: {successful}")
    
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
    
    logger.info(f" CSV: {output_csv}")

if __name__ == "__main__":
    main()
