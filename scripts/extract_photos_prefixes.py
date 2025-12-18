#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
from collections import defaultdict
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def extract_prefix_from_path(full_path):
    """Извлекает префикс из пути фото"""
    # Пример: /kuzl/val/kzul_val_1M63Y_20_182.jpg -> KUZL, VAL
    # или: /KOLZUB/165/file.jpg -> KOLZUB, 165
    path = Path(full_path)
    parts = path.parent.parts
    return parts

def main():
    root = Path(__file__).parent.parent
    registry_file = root / "data" / "mappings" / "photos_registry_full.json"
    output_file = root / "data" / "mappings" / "photos_prefixes_dict.json"

    logger.info(f"Читаю реестр фото: {registry_file}")
    with open(registry_file, 'r', encoding='utf-8-sig') as f:
        photos_registry = json.load(f)

    prefixes_by_folder = defaultdict(list)
    all_prefixes = set()
    
    # Анализируем структуру папок
    for folder_prefix, photos_list in photos_registry.items():
        logger.info(f"\n Папка: {folder_prefix}")
        
        folder_prefixes = set()
        for photo in photos_list:
            # Получаем путь к фото
            full_path = photo.get('fullPath', '')
            if full_path:
                # Извлекаем части пути
                path_parts = Path(full_path).parent.parts
                # Берём части пути (исключая корневые директории)
                for part in path_parts:
                    if part and part not in ['/', '\\', 'C:']:
                        folder_prefixes.add(part.upper())
                        all_prefixes.add(part.upper())
        
        if folder_prefixes:
            prefixes_by_folder[folder_prefix] = sorted(list(folder_prefixes))
            logger.info(f"  Префиксы: {', '.join(sorted(folder_prefixes))}")

    # Сохраняем словарь
    output_dict = {
        "total_prefixes": len(all_prefixes),
        "all_prefixes": sorted(list(all_prefixes)),
        "prefixes_by_folder": prefixes_by_folder
    }

    logger.info(f"\n Статистика:")
    logger.info(f"  Всего уникальных префиксов: {len(all_prefixes)}")
    logger.info(f"  Папок с фото: {len(prefixes_by_folder)}")
    
    logger.info(f"\nСохраняю: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Готово!")

if __name__ == "__main__":
    main()
