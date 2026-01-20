#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Переименование файлов ТКП с английских кодов на русские названия
Renames TKP files from English codes to Russian names
"""

import os
import shutil

# Mapping of English filenames to Russian names
PARTS_RENAME_MAP = {
    "APRONS.md": "Фартуки токарных станков.md",
    "BALL_SCREWS.md": "ШВП - Шарико-винтовые пары.md",
    "FEED_BOXES.md": "Коробки подач.md",
    "GEARS_CNC.md": "Шестерни для станков с ЧПУ.md",
    "GEARS_CUSTOM.md": "Шестерни на заказ.md",
    "SHAFTS.md": "Валы для токарных станков.md",
    "SPINDLE_HEADS.md": "Шпиндельные бабки.md",
    "TAILSTOCKS.md": "Задние бабки.md",
    "TOOL_BLOCKS.md": "Резцовые блоки.md",
    "TURRET_HEADS.md": "Револьверные головки.md",
    "TURRET_REPAIR.md": "Ремонт револьверных головок.md"
}

MACHINES_RENAME_MAP = {
    "16A20F3.md": "Токарный станок 16А20Ф3.md",
    "16K20.md": "Токарно-винторезный станок 16К20.md",
    "16K40.md": "Токарно-винторезный станок 16К40.md",
    "16R25.md": "Токарно-винторезный станок 16Р25.md",
    "1A983.md": "Трубонарезной станок 1А983.md",
    "1M63.md": "Токарно-винторезный станок 1М63.md",
    "1N65.md": "Токарно-винторезный станок 1Н65.md",
    "1N983.md": "Трубонарезной станок 1Н983.md",
    "RT117.md": "Токарно-винторезный станок РТ117.md",
    "RT301.01.md": "Токарно-накатной станок РТ301.01.md",
    "RT301.02.md": "Токарно-накатной станок РТ301.02.md",
    "RT301.md": "Токарно-накатной станок РТ301.md",
    "RT305M.md": "Токарно-давильный станок РТ305М.md",
    "RT5001.md": "Лентобандажировочный станок РТ5001.md",
    "RT5003.md": "Лентобандажировочный станок РТ5003.md",
    "RT5004.md": "Лентобандажировочный станок РТ5004.md",
    "RT755F3.md": "Токарный станок РТ755Ф3.md",
    "RT779F3.md": "Трубонарезной станок РТ779Ф3.md",
    "RT783.md": "Трубонарезной станок РТ783.md",
    "RT817.md": "Токарно-винторезный станок РТ817.md",
    "RT917.md": "Токарно-накатной станок РТ917.md"
}

def rename_files(directory, rename_map):
    """Rename files in a directory according to the mapping"""
    renamed_count = 0
    
    for old_name, new_name in rename_map.items():
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"✓ Переименовано: {old_name} → {new_name}")
            renamed_count += 1
        else:
            print(f"⚠ Файл не найден: {old_name}")
    
    return renamed_count

def update_readme(directory, rename_map):
    """Update README.md with new filenames"""
    readme_path = os.path.join(directory, "README.md")
    
    if not os.path.exists(readme_path):
        print(f"⚠ README.md не найден в {directory}")
        return
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace old filenames with new ones
    for old_name, new_name in rename_map.items():
        content = content.replace(f"]({old_name})", f"]({new_name})")
        content = content.replace(f"({old_name})", f"({new_name})")
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Обновлен README.md в {directory}")

def main():
    print("=" * 60)
    print("ПЕРЕИМЕНОВАНИЕ ФАЙЛОВ ТКП")
    print("=" * 60)
    
    # Rename parts TKP files
    print("\n1. Переименование ТКП запчастей...")
    parts_dir = "docs/tkp_parts"
    if os.path.exists(parts_dir):
        parts_renamed = rename_files(parts_dir, PARTS_RENAME_MAP)
        update_readme(parts_dir, PARTS_RENAME_MAP)
        print(f"\n   Переименовано файлов: {parts_renamed}")
    else:
        print(f"   ⚠ Директория не найдена: {parts_dir}")
    
    # Rename machines TKP files
    print("\n2. Переименование ТКП станков...")
    machines_dir = "docs/tkp_machines"
    if os.path.exists(machines_dir):
        machines_renamed = rename_files(machines_dir, MACHINES_RENAME_MAP)
        update_readme(machines_dir, MACHINES_RENAME_MAP)
        print(f"\n   Переименовано файлов: {machines_renamed}")
    else:
        print(f"   ⚠ Директория не найдена: {machines_dir}")
    
    print("\n" + "=" * 60)
    print("✅ ПЕРЕИМЕНОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)

if __name__ == "__main__":
    main()
