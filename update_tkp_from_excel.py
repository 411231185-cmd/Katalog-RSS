#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update TKP files with correct technical specifications from Excel file
"""

import xlrd
import os
import re

def read_excel_specs(xls_file):
    """Read technical specifications from Excel file"""
    workbook = xlrd.open_workbook(xls_file, encoding_override='cp1251')
    sheet = workbook.sheet_by_index(0)
    
    # Machine names are in first row, starting from column 0
    machines = {}
    col = 0
    while col < sheet.ncols:
        machine_name = sheet.cell_value(0, col)
        if machine_name and "Станок" in machine_name:
            # Extract machine code
            machines[col] = {
                'name': machine_name.strip(),
                'specs': {}
            }
        col += 3  # Each machine takes 3 columns
    
    # Read specs starting from row 2
    for row in range(2, sheet.nrows):
        param_name = sheet.cell_value(row, 0)
        if not param_name or param_name.strip() == '':
            continue
            
        param_name = param_name.strip()
        
        for col in machines.keys():
            value = sheet.cell_value(row, col + 1)
            if value and str(value).strip():
                machines[col]['specs'][param_name] = str(value).strip()
    
    return machines

def identify_machine(machine_name):
    """Identify machine file based on machine name"""
    mapping = {
        '1М63Н': 'Токарно-винторезный станок 1М63.md',
        '16К40': 'Токарно-винторезный станок 16К40.md',
        '16Р40': None,  # Not in our list
        '1М65': None,  # Different from 1Н65
        '1Н65': 'Токарно-винторезный станок 1Н65.md',
        'РТ117': 'Токарно-винторезный станок РТ117.md',
        'РТ817': 'Токарно-винторезный станок РТ817.md',
        'РТ983': 'Трубонарезной станок РТ783.md',  # Close match
        '16А20Ф3': 'Токарный станок 16А20Ф3.md',
        '16М30Ф3': None,  # Not in our list  
        'РТ755Ф3': 'Токарный станок РТ755Ф3.md',
    }
    
    for key in mapping.keys():
        if key in machine_name:
            return mapping[key]
    return None

def format_spec_value(value):
    """Format specification value for markdown"""
    if not value:
        return ""
    # Replace commas with proper formatting
    value = value.replace(',', ', ')
    return value

def update_tkp_file(file_path, specs):
    """Update TKP file with correct specifications"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Build the technical parameters section
    tech_params = []
    
    # Diameter specs
    has_diameters = False
    for key in specs.keys():
        if 'устанавливаемой над станиной' in key or 'обрабатываемой над станиной' in key or 'обрабатываемой над суппортом' in key:
            has_diameters = True
            break
    
    if has_diameters:
        tech_params.append("#### Размеры и масса обработки")
        tech_params.append("")
        
        for key in specs.keys():
            if 'устанавливаемой над станиной' in key:
                tech_params.append(f"- **Наибольший диаметр устанавливаемой заготовки над станиной:** {specs[key]} мм")
            elif 'обрабатываемой над станиной' in key and 'выемкой' not in key:
                tech_params.append(f"- **Наибольший диаметр обрабатываемой заготовки над станиной:** {specs[key]} мм")
            elif 'обрабатываемой над суппортом' in key:
                tech_params.append(f"- **Наибольший диаметр обрабатываемой заготовки над суппортом:** {specs[key]} мм")
            elif 'над выемкой в станине' in key:
                tech_params.append(f"- **Наибольший диаметр обрабатываемой заготовки над выемкой в станине:** {specs[key]} мм")
    
    # Length specs
    for key in specs.keys():
        if 'Наибольшая длинна обрабатываемой заготовки' in key or 'Расстояние между центрами' in key:
            value = format_spec_value(specs[key])
            tech_params.append(f"- **Наибольшая длина обрабатываемой заготовки (РМЦ):** {value} мм")
            break
    
    # Weight specs
    for key in specs.keys():
        if 'Наибольший вес устанавливаемой заготовки' in key or 'Наибольшая масса устанавливаемой детали' in key:
            value = format_spec_value(specs[key])
            tech_params.append(f"- **Наибольший вес устанавливаемой заготовки:** {value} кг")
            break
    
    # Add other specs if present
    if 'Длина выемки в станине от торца фланца шпинделя' in specs:
        tech_params.append(f"- **Длина выемки в станине от торца фланца шпинделя:** {specs['Длина выемки в станине от торца фланца шпинделя']} мм")
    
    tech_params.append("")
    
    # Spindle characteristics
    tech_params.append("#### Характеристики шпинделя")
    tech_params.append("")
    
    for key in specs.keys():
        if 'Размер конца шпинделя передней бабки' in key:
            tech_params.append(f"- **Размер конца шпинделя передней бабки по DIN:** {specs[key]}")
        elif 'Количество ступеней частот вращения шпинделя' in key:
            tech_params.append(f"- **Количество ступеней частот вращения:** {specs[key]}")
        elif 'Диаметр цилиндрического отверстия в шпинделе' in key:
            tech_params.append(f"- **Диаметр цилиндрического отверстия в шпинделе:** {specs[key]} мм")
        elif 'Пределы частот вращения шпинделя' in key or 'Диапазон частот вращения шпинделя' in key:
            tech_params.append(f"- **Пределы частот вращения шпинделя:** {specs[key]} об/мин")
        elif 'Центр в шпинделе передней бабки' in key:
            tech_params.append(f"- **Центр в шпинделе передней бабки (метрический):** {specs[key]}")
        elif 'Центр в шпинделе задней бабки' in key:
            tech_params.append(f"- **Центр в шпинделе задней бабки (Морзе):** {specs[key]}")
    
    tech_params.append("")
    
    # Feed specifications
    has_feeds = False
    for key in specs.keys():
        if 'Пределы рабочих подач:' in key or 'продольных, мм/об' in key:
            if not has_feeds:
                tech_params.append("#### Подачи")
                tech_params.append("")
                has_feeds = True
        if 'продольных, мм/об' in key:
            tech_params.append(f"- **Пределы рабочих подач продольных:** {specs[key]} мм/об")
        elif 'поперечных, мм/об' in key:
            tech_params.append(f"- **Пределы рабочих подач поперечных:** {specs[key]} мм/об")
        elif 'резцовых салазок, мм/об' in key:
            tech_params.append(f"- **Пределы рабочих подач резцовых салазок:** {specs[key]} мм/об")
    
    if has_feeds:
        tech_params.append("")
    
    # Rapid traverse
    has_rapid = False
    for key in specs.keys():
        if 'Ускоренное перемещение суппорта:' in key or 'продольное, м/мин' in key:
            if not has_rapid:
                tech_params.append("#### Ускоренные перемещения")
                tech_params.append("")
                has_rapid = True
        if 'продольное, м/мин' in key:
            tech_params.append(f"- **Ускоренное перемещение суппорта продольное:** {specs[key]} м/мин")
        elif 'поперечное, м/мин' in key:
            tech_params.append(f"- **Ускоренное перемещение суппорта поперечное:** {specs[key]} м/мин")
        elif 'Максимальная скорость быстрых перемещений' in key:
            tech_params.append(f"- **Максимальная скорость быстрых перемещений суппорта:** {specs[key]}")
    
    if has_rapid:
        tech_params.append("")
    
    # Threading capabilities
    has_threading = False
    for key in specs.keys():
        if 'метрических, мм' in key or 'Величина шагов нарезания резьб:' in key:
            if not has_threading:
                tech_params.append("#### Нарезание резьб")
                tech_params.append("")
                has_threading = True
        if 'метрических, мм' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб метрических:** {specs[key]} мм")
        elif 'дюймовых, ниток/дюйм' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб дюймовых:** {specs[key]} ниток/дюйм")
        elif 'модульных, модуль' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб модульных:** {specs[key]} модуль")
        elif 'питчевых, питч диаметральный' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб питчевых:** {specs[key]} питч диаметральный")
    
    if has_threading:
        tech_params.append("")
    
    # Power
    for key in specs.keys():
        if 'Мощность главного привода' in key or 'Мощность привода главного движения' in key:
            tech_params.append("#### Энергетические показатели")
            tech_params.append("")
            tech_params.append(f"- **Мощность главного привода:** {specs[key]} кВт")
            break
    
    # CNC specific parameters
    for key in specs.keys():
        if 'Количество управляемых координат' in key:
            if "#### Энергетические показатели" not in '\n'.join(tech_params[-5:]):
                tech_params.append("")
                tech_params.append("#### Параметры ЧПУ")
                tech_params.append("")
            tech_params.append(f"- **Количество управляемых координат:** {specs[key]}")
        elif 'Количество позиций инструментальной головки' in key:
            tech_params.append(f"- **Количество позиций инструментальной головки:** {specs[key]}")
        elif 'Дискретность задания перемещения' in key:
            tech_params.append(f"- **Дискретность задания перемещения:** {specs[key]} мм")
        elif 'Точность позиционирования' in key:
            tech_params.append(f"- **Точность позиционирования:** {specs[key]} мм")
        elif 'Рабочая подача по осям' in key:
            tech_params.append(f"- **Рабочая подача по осям X и Z:** {specs[key]} мм/мин")
    
    # Build dimensions section
    dimensions = []
    dimensions.append("| Параметр | Значение |")
    dimensions.append("|----------|----------|")
    
    for key in specs.keys():
        if 'Габаритные размеры' in key:
            continue
        if 'длина, мм' in key and 'Габаритные размеры' not in key:
            value = format_spec_value(specs[key])
            dimensions.append(f"| Длина | {value} мм |")
        elif 'ширина, мм' in key and 'Габаритные размеры' not in key:
            value = format_spec_value(specs[key])
            dimensions.append(f"| Ширина | {value} мм |")
        elif 'высота, мм' in key and 'Габаритные размеры' not in key:
            value = format_spec_value(specs[key])
            dimensions.append(f"| Высота | {value} мм |")
    
    for key in specs.keys():
        if 'Масса, кг' in key or 'Масса станка' in key:
            value = format_spec_value(specs[key])
            dimensions.append(f"| Масса станка | {value} кг |")
            break
    
    # Replace technical parameters section
    tech_params_text = '\n'.join(tech_params)
    
    # Find and replace ОСНОВНЫЕ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ section
    pattern = r'## ОСНОВНЫЕ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ\n\n.*?(?=\n## |\Z)'
    replacement = f"## ОСНОВНЫЕ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ\n\n{tech_params_text}\n"
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Replace dimensions table
    if len(dimensions) > 2:
        dimensions_text = '\n'.join(dimensions)
        pattern = r'## ГАБАРИТНЫЕ РАЗМЕРЫ И МАССА\n\n\| Параметр \| Значение \|.*?(?=\n## |\Z)'
        replacement = f"## ГАБАРИТНЫЕ РАЗМЕРЫ И МАССА\n\n{dimensions_text}\n"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    # Read Excel file
    xls_file = 'docs/Станки/Технические_характеристики_станков.xls'
    print(f"Reading technical specifications from {xls_file}...")
    
    machines = read_excel_specs(xls_file)
    
    print(f"\nFound {len(machines)} machines in Excel file\n")
    
    # Update TKP files
    base_path = 'docs/Станки'
    updated_count = 0
    
    for col, machine_data in machines.items():
        machine_name = machine_data['name']
        specs = machine_data['specs']
        
        print(f"\nProcessing: {machine_name}")
        print(f"  Specifications: {len(specs)} parameters")
        
        # Identify corresponding TKP file
        tkp_file = identify_machine(machine_name)
        
        if not tkp_file:
            print(f"  ⚠️  No matching TKP file found")
            continue
        
        # Find the file in subdirectories
        file_path = None
        for category in os.listdir(base_path):
            category_path = os.path.join(base_path, category)
            if os.path.isdir(category_path):
                potential_path = os.path.join(category_path, tkp_file)
                if os.path.exists(potential_path):
                    file_path = potential_path
                    break
        
        if not file_path:
            print(f"  ⚠️  File not found: {tkp_file}")
            continue
        
        print(f"  📄 Updating: {file_path}")
        
        if update_tkp_file(file_path, specs):
            print(f"  ✅ Updated successfully")
            updated_count += 1
        else:
            print(f"  ❌ Update failed")
    
    print(f"\n{'='*60}")
    print(f"Updated {updated_count} TKP files")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
