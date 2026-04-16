#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update TKP files with CORRECT technical specifications from Excel file
Properly handles both conventional and CNC machines
"""

import xlrd
import os
import re

def read_excel_specs_improved(xls_file):
    """Read technical specifications from Excel file with improved parsing"""
    workbook = xlrd.open_workbook(xls_file, encoding_override='cp1251')
    sheet = workbook.sheet_by_index(0)
    
    # Machine names are in first row
    machines = {}
    col = 0
    while col < sheet.ncols:
        machine_name = sheet.cell_value(0, col)
        if machine_name and "Станок" in machine_name:
            machines[col] = {
                'name': machine_name.strip(),
                'specs': {}
            }
        col += 3
    
    # Read ALL rows for each machine to get proper parameter-value mapping
    for row in range(0, sheet.nrows):
        for col in machines.keys():
            param_cell = sheet.cell_value(row, col)
            value_cell = sheet.cell_value(row, col + 1)
            
            if param_cell and str(param_cell).strip():
                param_name = str(param_cell).strip()
                value = str(value_cell).strip() if value_cell else ""
                
                if value and param_name not in ['Технические характеристики', 'Габаритные размеры (вместе с электрооборудованием):']:
                    machines[col]['specs'][param_name] = value
    
    return machines

def identify_machine(machine_name):
    """Identify machine file based on machine name"""
    mapping = {
        '1М63Н': 'Токарно-винторезный станок 1М63.md',
        '16К40': 'Токарно-винторезный станок 16К40.md',
        '1Н65': 'Токарно-винторезный станок 1Н65.md',
        'РТ117': 'Токарно-винторезный станок РТ117.md',
        'РТ817': 'Токарно-винторезный станок РТ817.md',
        'РТ983': 'Трубонарезной станок РТ783.md',
        '16А20Ф3': 'Токарный станок 16А20Ф3.md',
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
    value = value.replace(',', ', ')
    return value

def build_tech_params(specs, is_cnc=False):
    """Build technical parameters section"""
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
            if key == '-устанавливаемой над станиной, мм':
                tech_params.append(f"- **Наибольший диаметр устанавливаемой заготовки над станиной:** {specs[key]} мм")
            elif key == '-обрабатываемой над станиной, мм':
                tech_params.append(f"- **Наибольший диаметр обрабатываемой заготовки над станиной:** {specs[key]} мм")
            elif key == '-обрабатываемой над суппортом, мм':
                tech_params.append(f"- **Наибольший диаметр обрабатываемой заготовки над суппортом:** {specs[key]} мм")
            elif '-над выемкой в станине' in key:
                tech_params.append(f"- **Наибольший диаметр обрабатываемой заготовки над выемкой в станине:** {specs[key]} мм")
        
        # Length specs
        for key in specs.keys():
            if 'Наибольшая длинна обрабатываемой заготовки' in key or 'Расстояние между центрами' in key:
                value = format_spec_value(specs[key])
                tech_params.append(f"- **Наибольшая длина обрабатываемой заготовки (РМЦ):** {value} мм")
                break
            elif 'Наибольшая длинна устанавливаемой заготовки, мм' in key:
                value = format_spec_value(specs[key])
                tech_params.append(f"- **Наибольшая длина устанавливаемой заготовки (РМЦ):** {value} мм")
                break
        
        # Weight specs
        for key in specs.keys():
            if 'Наибольший вес устанавливаемой заготовки' in key or 'Наибольшая масса устанавливаемой детали' in key:
                value = format_spec_value(specs[key])
                tech_params.append(f"- **Наибольший вес устанавливаемой заготовки:** {value} кг")
                break
            elif 'Наибольшая длинна обработки заготовки, мм' in key:
                value = format_spec_value(specs[key])
                tech_params.append(f"- **Наибольшая длина обработки заготовки:** {value} мм")
        
        # Add other specs
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
        if '-продольных, мм/об' in key:
            if not has_feeds:
                tech_params.append("#### Подачи")
                tech_params.append("")
                has_feeds = True
            tech_params.append(f"- **Пределы рабочих подач продольных:** {specs[key]} мм/об")
        elif '-поперечных, мм/об' in key:
            tech_params.append(f"- **Пределы рабочих подач поперечных:** {specs[key]} мм/об")
        elif '-резцовых салазок, мм/об' in key:
            tech_params.append(f"- **Пределы рабочих подач резцовых салазок:** {specs[key]} мм/об")
        elif 'Рабочая подача по осям' in key:
            if not has_feeds:
                tech_params.append("#### Подачи")
                tech_params.append("")
                has_feeds = True
            tech_params.append(f"- **Рабочая подача по осям X и Z:** {specs[key]} мм/мин")
    
    if has_feeds:
        tech_params.append("")
    
    # Rapid traverse
    has_rapid = False
    for key in specs.keys():
        if '-продольное, м/мин' in key:
            if not has_rapid:
                tech_params.append("#### Ускоренные перемещения")
                tech_params.append("")
                has_rapid = True
            tech_params.append(f"- **Ускоренное перемещение суппорта продольное:** {specs[key]} м/мин")
        elif '-поперечное, м/мин' in key:
            tech_params.append(f"- **Ускоренное перемещение суппорта поперечное:** {specs[key]} м/мин")
        elif 'Максимальная скорость быстрых перемещений' in key:
            if not has_rapid:
                tech_params.append("#### Ускоренные перемещения")
                tech_params.append("")
                has_rapid = True
            tech_params.append(f"- **Максимальная скорость быстрых перемещений суппорта:** {specs[key]} м/мин")
    
    if has_rapid:
        tech_params.append("")
    
    # Threading capabilities
    has_threading = False
    for key in specs.keys():
        if '-метрических, мм' in key:
            if not has_threading:
                tech_params.append("#### Нарезание резьб")
                tech_params.append("")
                has_threading = True
            tech_params.append(f"- **Величина шагов нарезания резьб метрических:** {specs[key]} мм")
        elif '-дюймовых, ниток/дюйм' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб дюймовых:** {specs[key]} ниток/дюйм")
        elif '-модульных, модуль' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб модульных:** {specs[key]} модуль")
        elif '-питчевых, питч диаметральный' in key:
            tech_params.append(f"- **Величина шагов нарезания резьб питчевых:** {specs[key]} питч диаметральный")
    
    if has_threading:
        tech_params.append("")
    
    # CNC specific parameters
    has_cnc_params = False
    for key in specs.keys():
        if 'Количество управляемых координат' in key:
            if not has_cnc_params:
                tech_params.append("#### Параметры ЧПУ")
                tech_params.append("")
                has_cnc_params = True
            tech_params.append(f"- **Количество управляемых координат:** {specs[key]}")
        elif 'Количество позиций инструментальной головки' in key:
            if not has_cnc_params:
                tech_params.append("#### Параметры ЧПУ")
                tech_params.append("")
                has_cnc_params = True
            tech_params.append(f"- **Количество позиций инструментальной головки:** {specs[key]}")
        elif 'Дискретность задания перемещения' in key:
            tech_params.append(f"- **Дискретность задания перемещения:** {specs[key]} мм")
        elif 'Точность позиционирования' in key:
            tech_params.append(f"- **Точность позиционирования:** {specs[key]} мм")
    
    if has_cnc_params:
        tech_params.append("")
    
    # Power
    for key in specs.keys():
        if 'Мощность главного привода' in key or 'Мощность привода главного движения' in key:
            tech_params.append("#### Энергетические показатели")
            tech_params.append("")
            tech_params.append(f"- **Мощность главного привода:** {specs[key]} кВт")
            break
    
    # Torque for CNC
    for key in specs.keys():
        if 'Наибольший крутящий момент' in key:
            tech_params.append(f"- **Наибольший крутящий момент:** {specs[key]} кНм")
            break
    
    return '\n'.join(tech_params)

def build_dimensions_table(specs):
    """Build dimensions table"""
    dimensions = []
    dimensions.append("| Параметр | Значение |")
    dimensions.append("|----------|----------|")
    
    for key in specs.keys():
        if key == '-длина, мм':
            value = format_spec_value(specs[key])
            dimensions.append(f"| Длина | {value} мм |")
        elif key == '-ширина, мм':
            value = format_spec_value(specs[key])
            dimensions.append(f"| Ширина | {value} мм |")
        elif key == '-высота, мм':
            value = format_spec_value(specs[key])
            dimensions.append(f"| Высота | {value} мм |")
    
    for key in specs.keys():
        if 'Масса, кг' in key or 'Масса станка' in key:
            value = format_spec_value(specs[key])
            dimensions.append(f"| Масса станка | {value} кг |")
            break
    
    return '\n'.join(dimensions)

def update_tkp_file(file_path, specs, is_cnc=False):
    """Update TKP file with correct specifications"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Build the technical parameters section
    tech_params_text = build_tech_params(specs, is_cnc)
    
    # Replace technical parameters section
    pattern = r'## ОСНОВНЫЕ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ\n\n.*?(?=\n## |\Z)'
    replacement = f"## ОСНОВНЫЕ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ\n\n{tech_params_text}\n"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Replace dimensions table
    dimensions_text = build_dimensions_table(specs)
    if '| Параметр |' in dimensions_text:
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
    
    machines = read_excel_specs_improved(xls_file)
    
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
        
        # Determine if it's a CNC machine
        is_cnc = 'ЧПУ' in machine_name or 'программным' in machine_name
        
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
        print(f"  {'  (CNC machine)' if is_cnc else '  (Conventional machine)'}")
        
        if update_tkp_file(file_path, specs, is_cnc):
            print(f"  ✅ Updated successfully")
            updated_count += 1
        else:
            print(f"  ❌ Update failed")
    
    print(f"\n{'='*60}")
    print(f"Updated {updated_count} TKP files")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
