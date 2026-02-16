import csv
import re
from pathlib import Path

INPUT = Path(r'docs/ТКП/ТКП-1Н65-ДИП500-полная-номенклатура-kinematics_part1.csv')
OUTPUT = Path(r'docs/ТКП/ТКП-1Н65-ДИП500-полная-номенклатура-kinematics_part1.normalized.csv')

SECTION_KEYWORDS = [
    'Бабка передняя', 'Патрон', 'Колеса', 'Коробка', 'Фартук', 'Станина', 'Бабка задняя',
    'Каретка', 'Суппорт', 'Валы', 'Общие запчасти', 'Питчевыми', 'Сменные', 'Гитара',
]

DESIGNATION_PAT = re.compile(r'(1[АНМ]\d{2}|16М50)\.[\w\-/]+')
POS_PAT = re.compile(r'([a-zA-Zа-яА-Я\d]+)$')

header = ['part','section','pos','Z','module','width','designation','name']

read_lines = 0
written_lines = 0
skipped_lines = 0
problem_lines = []

with INPUT.open('r', encoding='utf-8-sig', errors='ignore') as fin, OUTPUT.open('w', encoding='utf-8', newline='') as fout:
    writer = csv.writer(fout)
    writer.writerow(header)
    for line in fin:
        read_lines += 1
        line = line.strip().replace('\ufeff','')
        if not line or line.count(',') < 3:
            skipped_lines += 1
            continue
        row = [c.strip() for c in line.split(',')]
        # Format A: section,pos,Z,module,width,designation,name
        if len(row) == 7 and row[0] in SECTION_KEYWORDS:
            section, pos, Z, module, width, designation, name = row
        # Format B: ...designation,name,section,pos,...
        elif any(s in row for s in SECTION_KEYWORDS):
            try:
                # Find section and pos at end
                for i in range(len(row)-2):
                    if row[i] in SECTION_KEYWORDS and POS_PAT.match(row[i+1]):
                        section = row[i]
                        pos = row[i+1]
                        # Try to find designation
                        designation = ''
                        for j in range(i):
                            if DESIGNATION_PAT.match(row[j]):
                                designation = row[j]
                        # Try to find Z/module/width to the left
                        nums = [x for x in row[max(0,i-3):i] if re.match(r'^\d+(,\d+)?$', x)]
                        Z = nums[0] if len(nums)>0 else ''
                        module = nums[1] if len(nums)>1 else ''
                        width = nums[2] if len(nums)>2 else ''
                        name = row[i-1] if i-1>=0 else ''
                        break
                else:
                    raise ValueError('No section/pos found')
            except Exception as e:
                skipped_lines += 1
                problem_lines.append((line, str(e)))
                continue
        else:
            skipped_lines += 1
            problem_lines.append((line, 'Unknown format'))
            continue
        # part calculation
        try:
            part = '2' if pos.isdigit() and 100<=int(pos)<=115 else '1'
        except:
            part = '1'
        writer.writerow([part,section,pos,Z,module,width,designation,name])
        written_lines += 1

print(f'Read: {read_lines}, Written: {written_lines}, Skipped: {skipped_lines}')
if problem_lines:
    print('Problem lines (up to 10):')
    for l,err in problem_lines[:10]:
        print(f'  {l[:120]}... | {err}')
