import json, csv
from pathlib import Path
import logging, requests, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = "c638b380d8fa25b77026"
PROJECT_ID = "17325576"

def upload_to_tilda(file_path):
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        url = f"https://api.tilda.cc/v1/project/{PROJECT_ID}/filestorage/upload"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, files=files, timeout=60)
        
        logger.info(f"Код: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info(f"Ответ: {str(data)[:100]}")
            
            if isinstance(data, dict):
                if "url" in data:
                    return data["url"]
                if "file" in data and isinstance(data["file"], dict) and "url" in data["file"]:
                    return data["file"]["url"]
            return None
        else:
            logger.error(f"Ошибка {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return None

def main():
    root = Path(__file__).parent.parent
    mapping_file = root / "data" / "mappings" / "offer_to_photos.json"
    csv_file = root / "data" / "source" / "ETALONNYI-est-UID-i-SKU.csv"
    output_csv = root / "data" / "normalized" / "catalog_with_tilda_urls.csv"
    
    logger.info("ЗАГРУЗКА ФОТ НА TILDA")
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    upload_results = {}
    successful = 0
    
    for i, (uid, data) in enumerate(mapping.items(), 1):
        photos = data.get("photos", [])
        if photos:
            file_path = photos[0]["fullPath"]
            file_name = photos[0]["fileName"]
            logger.info(f"[{i}/{len(mapping)}] {file_name[:40]}")
            
            cdn_url = upload_to_tilda(file_path)
            if cdn_url:
                upload_results[uid] = cdn_url
                successful += 1
                logger.info(f" Загружено")
            
            time.sleep(1)
    
    logger.info(f"Всего загружено: {successful}")
    
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
                logger.info(f" {uid}: добавлена Tilda ссылка")
            rows.append(row)
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f" CSV сохранен: {output_csv}")

if __name__ == "__main__":
    main()
