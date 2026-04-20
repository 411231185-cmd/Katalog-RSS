#!/usr/bin/env python3
"""Sample the 1014 'has_services only' rows to understand their format"""

import openpyxl
import re

FINAL = "PLOSIADKI-RSS/PromPortal/Каталоги/PromPortal-FINAL-with-descriptions.xlsx"
wb = openpyxl.load_workbook(FINAL, read_only=True, data_only=True)
ws = wb.active

SERVICES_MARKER = "Подобрать конкретную запчасть"

samples = []
count = 0

for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    name = str(row[2] or '')
    desc = str(row[4] or '')
    if not desc.strip():
        continue

    tags = set()
    if desc.strip().startswith('ООО') or desc.strip().startswith('ТД РУС'):
        tags.add('marketing')
    if 'Смотрите также:' in desc:
        tags.add('smotrite')
    if SERVICES_MARKER in desc:
        tags.add('has_services')
    if 'ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ' in desc or 'Назначение\n' in desc or 'Назначение\r' in desc:
        tags.add('directus_format')
    if 'Позиция' in desc and 'кинематической схеме' in desc:
        tags.add('kinematic')
    if 'применяется в' in desc.lower() and 'Поставляется' in desc:
        tags.add('gen_desc_format')

    # "has_services" only — no other tags
    if tags == {'has_services'}:
        count += 1
        if len(samples) < 15:
            tech = desc[:desc.index(SERVICES_MARKER)].strip() if SERVICES_MARKER in desc else desc.strip()
            samples.append((row_num, name[:80], tech[:250]))

wb.close()

print(f"=== 'has_services' ONLY: {count} rows ===\n")
for r, n, t in samples:
    print(f"Row {r}: {n}")
    print(f"  Tech: {t}")
    print()
