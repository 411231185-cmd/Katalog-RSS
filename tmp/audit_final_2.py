#!/usr/bin/env python3
"""Deeper audit: duplicated text, services block format, etc."""

import openpyxl
import re

FINAL = "PLOSIADKI-RSS/PromPortal/Каталоги/PromPortal-FINAL-with-descriptions.xlsx"
wb = openpyxl.load_workbook(FINAL, read_only=True, data_only=True)
ws = wb.active

SERVICES_MARKER = "Подобрать конкретную запчасть"

# The APPROVED services block lines (from user's spec)
APPROVED_SERVICES = [
    "Подобрать конкретную запчасть вы можете у нас на сайте в разделе Каталог ТД РУССтанкоСбыт.",
    "Поставка и изготовление ПАТРОНОВ для станков",
    "Поставка ПОДШИПНИКОВ для станков",
    "Поставка и изготовление ЦЕНТРОВ для токарных станков",
    "Изготовление СУППОРТОВ для токарных станков",
    "Изготовление ПЛАНШАЙБ для токарных станков",
    "Изготовление ШВП для станков",
    "Изготовление ВИНТОВ для станков",
    "Изготовление ВАЛОВ для станков",
    "Изготовление ВТУЛОК для станков",
    "Изготовление ШЕСТЕРЁН для станков",
    "Изготовление ЛЮНЕТОВ для токарных станков",
    "Изготовление ЗАЩИТНЫХ КОЖУХОВ для станков",
    "Изготовление КАБИНЕТНЫХ ЗАЩИТ для станков",
    "Изготовление ВКЛАДЫШЕЙ и ЗАХВАТОВ для станков",
]

dup_text_count = 0
wrong_services = 0
smotrite_count = 0
tech_chars_block = 0
no_newline_before_services = 0
position_kinematic = 0

dup_examples = []
wrong_svc_examples = []
smotrite_examples = []

for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    name = str(row[2] or '')
    desc = str(row[4] or '')

    if not desc.strip():
        continue

    # Check for duplicated sentences (same text repeated)
    # Pattern: sentence appears twice in a row
    sentences = re.split(r'[.!?]\s+', desc)
    for i in range(len(sentences)-1):
        s = sentences[i].strip()
        if len(s) > 30 and s == sentences[i+1].strip():
            dup_text_count += 1
            if len(dup_examples) < 5:
                dup_examples.append((row_num, name[:60], s[:80]))
            break

    # Check "Смотрите также:" pattern (wrong services format)
    if 'Смотрите также:' in desc:
        smotrite_count += 1
        if len(smotrite_examples) < 5:
            idx = desc.index('Смотрите также:')
            smotrite_examples.append((row_num, name[:60], desc[idx:idx+150]))

    # Check services block matches approved text
    if SERVICES_MARKER in desc:
        svc_part = desc[desc.index(SERVICES_MARKER):]
        # Check first line
        if "Каталог ТД РУССтанкоСбыт" not in svc_part:
            wrong_services += 1
            if len(wrong_svc_examples) < 5:
                wrong_svc_examples.append((row_num, name[:60], svc_part[:150]))

    # Check for "ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ" block (structured format from Directus)
    if 'ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ' in desc or 'Технические характеристики' in desc:
        tech_chars_block += 1

    # Check for kinematic position data
    if 'Позиция' in desc and 'кинематической схеме' in desc:
        position_kinematic += 1

    # Check no newline before services block
    if SERVICES_MARKER in desc:
        idx = desc.index(SERVICES_MARKER)
        if idx > 0 and desc[idx-1] != '\n':
            no_newline_before_services += 1

wb.close()

print("=== DEEPER AUDIT ===")
print(f"Duplicated sentences: {dup_text_count}")
for r, n, s in dup_examples:
    print(f"  Row {r}: [{n}] -> '{s}'")

print(f"\n'Смотрите также:' pattern: {smotrite_count}")
for r, n, s in smotrite_examples:
    print(f"  Row {r}: [{n}] -> {s}")

print(f"\nWrong services block text: {wrong_services}")
for r, n, s in wrong_svc_examples:
    print(f"  Row {r}: [{n}] -> {s}")

print(f"\nHas 'ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ' block: {tech_chars_block}")
print(f"Has kinematic position data: {position_kinematic}")
print(f"No newline before services: {no_newline_before_services}")
