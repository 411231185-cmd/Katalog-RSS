#!/usr/bin/env python3
"""
Rename TKP folders from English to Russian for better navigation
"""

import os
import shutil
import json

# Define folder mappings
FOLDER_MAPPINGS = {
    'docs/tkp_machines': 'docs/Станки',
    'docs/tkp_parts': 'docs/Запчасти',
    'docs/tkp_components': 'docs/Комплектующие',
    'docs/tkp_turret_detailed': 'docs/Револьверные головки'
}

def rename_folders():
    """Rename folders from English to Russian"""
    print("Переименование папок в русские названия...\n")
    
    for old_path, new_path in FOLDER_MAPPINGS.items():
        if os.path.exists(old_path):
            print(f"Переименование: {old_path} → {new_path}")
            shutil.move(old_path, new_path)
            print(f"✅ Готово!\n")
        else:
            print(f"⚠️  Папка не найдена: {old_path}\n")
    
    print("\n📊 Итоговая структура:")
    print("=" * 50)
    for new_path in FOLDER_MAPPINGS.values():
        if os.path.exists(new_path):
            file_count = len([f for f in os.listdir(new_path) if f.endswith('.md')])
            print(f"✅ {new_path} - {file_count} файлов")
    
    print("\n✨ Все папки переименованы в кириллицу!")

if __name__ == "__main__":
    rename_folders()
