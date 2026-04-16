import openpyxl
import csv

xlsx_path = 'RegTorg-Fis-MashPort/XLSX/RegTorg_catalog_FINAL_200.xlsx'
csv_path = 'RegTorg-Fis-MashPort/XLSX/RegTorg_catalog_FINAL_200.csv'

wb = openpyxl.load_workbook(xlsx_path)
ws = wb.active

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for row in ws.iter_rows(values_only=True):
        writer.writerow(row)
