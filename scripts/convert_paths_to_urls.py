#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def local_path_to_dropbox_url(local_path):
    """Преобразует локальный путь в Dropbox URL"""
    if not local_path or local_path.strip() == "":
        return ""
    
    # Примеры преобразования:
    # C:\Users\User\Dropbox\MDT-Katalog\KUZL\kuzl_val_1M63_21_236.jpg
    #  https://www.dropbox.com/s/[file_id]/kuzl_val_1M63_21_236.jpg?dl=1
    
    # Получаем только имя файла
    path = Path(local_path)
    filename = path.name
    
    # Заменяем на временную ссылку (нужен реальный Dropbox API для полноценного)
    # На данный момент - ссылка вида: https://dl.dropboxusercontent.com/...
    
    return f"file:///{path.as_posix()}"

def main():
    root = Path(__file__).parent.parent
    input_file = root / "tests" / "catalog_with_photos_test.csv"
    output_file = root / "tests" / "catalog_with_photos_urls.csv"
    
    logger.info(f"Читаю: {input_file}")
    
    rows = []
    fieldnames = []
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        
        for row in reader:
            rows.append(row)
    
    logger.info(f"Загружено: {len(rows)} офферов")
    
    # Конвертируем пути в URL
    logger.info("\n Конвертирую пути в URL...")
    
    converted = 0
    for row in rows:
        if 'Фото' in row and row['Фото'].strip():
            local_path = row['Фото']
            # На данный момент используем file:// протокол
            # В реале нужно конвертировать в https://
            row['Фото'] = local_path  # TODO: преобразовать в Dropbox URL
            converted += 1
    
    logger.info(f" Конвертировано: {converted}")
    
    logger.info(f"\nСохраняю: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(" Готово!")

if __name__ == "__main__":
    main()
