import csv
from collections import OrderedDict

# Считываем все уникальные значения из колонки 'Рубрика'
input_file = 'RegTorg-Fis-MashPort/RegTorg_catalog_195_FIXED.csv'
output_file = 'RegTorg-Fis-MashPort/unique_rubrika.txt'

unique_rubrika = OrderedDict()

with open(input_file, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rubrika = row['Рубрика'].strip()
        if rubrika:
            unique_rubrika[rubrika] = None

with open(output_file, 'w', encoding='utf-8') as f:
    for rubrika in unique_rubrika.keys():
        f.write(rubrika + '\n')

print(f'Уникальные значения "Рубрика" сохранены в {output_file}')
