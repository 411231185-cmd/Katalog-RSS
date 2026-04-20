#!/usr/bin/env python3
"""Generate new_description_top for 20 sample parts from DIRECTUS_TKP_549_FULL.csv
in the target style (like the 1М63Б.08.164 example)."""

import csv, re

path = 'Directus-RSS/Товары/Каталоги CSV/DIRECTUS_TKP_549_FULL.csv'
with open(path, 'r', encoding='utf-8-sig') as f:
    all_rows = list(csv.DictReader(f))

# === Model → full name mapping ===
MODEL_NAMES = {
    '1М63': '1М63/1М63Н (ДИП‑300)',
    '1М63Б': '1М63Б (ДИП‑300)',
    '1М63Н': '1М63Н (ДИП‑300)',
    '1А64': '1А64 (1М65/1Н65)',
    '165': '165 (1М65/1Н65, ДИП‑500)',
    '1Н65': '1Н65 (ДИП‑500)',
    '1М65': '1М65 (ДИП‑500)',
    '16М50': '16М50',
    '16К30': '16К30',
    '1658': '1658 (1М65)',
    '164': '164 (1М65)',
    'У05': 'У05',
    '2825П': '2825П',
    '6Р82': '6Р82/6Р12',
}

# === Assembly mapping from Directus description ===
ASSEMBLY_NORMALIZE = {
    'шпиндельной бабки (коробки скоростей)': 'шпиндельной бабки (коробки скоростей)',
    'коробки подач': 'коробки подач',
    'фартука': 'фартука',
    'каретки': 'каретки',
    'задней бабки': 'задней бабки',
}

def extract_from_directus(row):
    """Extract structured facts from a DIRECTUS_TKP_549 description."""
    desc = row.get('description', '')
    name = row.get('name', '')
    meta = row.get('meta_description', '')

    facts = {
        'name': name,
        'artikul': '',
        'part_type': '',
        'assembly': '',
        'models': [],
        'position': '',
        'z': '',
        'm': '',
        'width': '',
        'function': '',
    }

    # Extract artikul from name or description
    art_match = re.search(r'(\d{1,4}[А-ЯA-Z]{0,4}\d{0,2}[\.\-]\d{2}[\.\-]\d{2,4}[А-ЯA-Z]{0,3})', name or desc)
    if art_match:
        facts['artikul'] = art_match.group(1)

    # Part type
    dl = desc.lower()
    if 'вал-колесо' in dl or 'валик-колесо' in dl or 'вал колесо' in dl:
        facts['part_type'] = 'вал-колесо зубчатое'
    elif 'вал-шестерня' in dl or 'вал‑шестерня' in dl:
        facts['part_type'] = 'вал-шестерня'
    elif 'зубчатое колесо' in dl or 'колесо зубчатое' in dl:
        facts['part_type'] = 'зубчатое колесо'
    elif 'венец' in dl:
        facts['part_type'] = 'венец'
    elif 'вал ' in dl[:10]:
        facts['part_type'] = 'вал'
    else:
        facts['part_type'] = 'запасная часть'

    # Assembly
    for key in ASSEMBLY_NORMALIZE:
        if key in desc:
            facts['assembly'] = ASSEMBLY_NORMALIZE[key]
            break
    if not facts['assembly']:
        if 'коробки подач' in desc:
            facts['assembly'] = 'коробки подач'
        elif 'шпиндельной бабки' in desc or 'коробки скоростей' in desc:
            facts['assembly'] = 'шпиндельной бабки (коробки скоростей)'
        elif 'фартук' in desc:
            facts['assembly'] = 'фартука'
        elif 'каретк' in desc:
            facts['assembly'] = 'каретки'

    # Models from description
    model_pat = re.compile(
        r'(1М63[А-ЯН]?|16К[0-9]+|16М[0-9]+|1[АН][0-9]+|165[0-9]*|164|1658'
        r'|ДИП[\-‑]?\d+|РТ\d+|16Р\d+|У0\d|2825П|6[РТ]\d+[А-Я]?)',
        re.IGNORECASE
    )
    found_models = model_pat.findall(desc)
    seen = []
    for m in found_models:
        mc = m.strip()
        if mc and mc not in seen:
            seen.append(mc)
    facts['models'] = seen

    # Kinematic data
    pos_match = re.search(r'Позиция\s+(\d+)', desc)
    if pos_match:
        facts['position'] = pos_match.group(1)

    z_match = re.search(r'(?:Число зубьев|z)\s*[:=]\s*(\d+)', desc, re.IGNORECASE)
    if z_match:
        facts['z'] = z_match.group(1)

    m_match = re.search(r'(?:Модуль|m)\s*[:=]\s*([\d.]+)', desc, re.IGNORECASE)
    if m_match:
        facts['m'] = m_match.group(1)

    w_match = re.search(r'Ширина венца\s*[:=]?\s*(\d+)', desc)
    if w_match:
        facts['width'] = w_match.group(1)

    return facts


def gen_description_top(facts):
    """Generate new_description_top in target style."""
    art = facts['artikul']
    pt = facts['part_type']
    assy = facts['assembly']
    models = facts['models']

    # Build model string with full names
    model_parts = []
    for m in models[:3]:
        full = MODEL_NAMES.get(m, m)
        model_parts.append(full)
    model_str = ', '.join(model_parts) if model_parts else 'по паспорту станка'

    # Sentence 1: What it is + where it's used
    if pt in ('зубчатое колесо', 'вал-колесо зубчатое'):
        if assy:
            s1 = f'{facts["name"]} — цилиндрическое {pt} {assy} токарно‑винторезного станка {model_str}.'
        else:
            s1 = f'{facts["name"]} — {pt} токарно‑винторезного станка {model_str}.'
    elif pt == 'вал-шестерня':
        if assy:
            s1 = f'{facts["name"]} — комбинированная деталь (вал с нарезанным зубчатым венцом) {assy} станка {model_str}.'
        else:
            s1 = f'{facts["name"]} — комбинированная деталь (вал с нарезанным зубчатым венцом) станка {model_str}.'
    elif pt == 'вал':
        if assy:
            s1 = f'{facts["name"]} — вал {assy} токарного станка {model_str}.'
        else:
            s1 = f'{facts["name"]} — вал токарного станка {model_str}.'
    elif pt == 'венец':
        s1 = f'{facts["name"]} — венец токарного патрона станка {model_str}.'
    else:
        s1 = f'{facts["name"]} — запасная часть токарного станка {model_str}.'

    # Sentence 2: Parameters (z, m, width, position)
    params = []
    if facts['m']:
        params.append(f'модуль m\u2009=\u2009{facts["m"]}')
    if facts['z']:
        params.append(f'число зубьев z\u2009=\u2009{facts["z"]}')
    if facts['width']:
        params.append(f'ширина венца {facts["width"]}\u2009мм')
    if facts['position']:
        params.append(f'позиция {facts["position"]} по кинематической схеме')

    if params:
        s2 = 'Параметры: ' + ', '.join(params) + '.'
    else:
        s2 = ''

    # Sentence 3: Function
    if pt in ('зубчатое колесо', 'вал-колесо зубчатое', 'вал-шестерня'):
        s3 = 'Назначение — передача крутящего момента в кинематической цепи узла, работа в зацеплении с сопряжёнными колёсами и валами.'
    elif pt == 'вал':
        if assy and 'подач' in assy:
            s3 = 'Назначение — передача движения подач к ходовому винту/валу и обеспечение требуемых подач и шагов резьб.'
        elif assy and 'скорост' in assy:
            s3 = 'Назначение — передача крутящего момента между ступенями коробки скоростей.'
        else:
            s3 = 'Назначение — передача крутящего момента между узлами привода станка.'
    elif pt == 'венец':
        s3 = 'Назначение — передача крутящего момента при перемещении кулачков патрона.'
    else:
        s3 = 'Назначение — обеспечение работоспособности узла станка.'

    # Sentence 4: Material + supplier
    if pt in ('зубчатое колесо', 'вал-колесо зубчатое', 'вал-шестерня') and (facts['z'] or facts['m']):
        s4 = f'Материал — легированная сталь, зубья термообработаны. Поставщик — ТД РУССтанкоСбыт, подбор по артикулу {art} и кинематической схеме.'
    elif pt == 'вал':
        s4 = f'Материал — конструкционная легированная сталь. Поставщик — ТД РУССтанкоСбыт, подбор по артикулу {art}.'
    else:
        s4 = f'Поставщик — ТД РУССтанкоСбыт, подбор по артикулу {art}.'

    parts = [s1]
    if s2:
        parts.append(s2)
    parts.append(s3)
    parts.append(s4)

    return ' '.join(parts)


# === Select 20 samples: 10 kolesa + 5 val-kolesa + 5 valy ===

rich = [r for r in all_rows
        if ('зубьев' in r['description'].lower() or 'Модуль' in r['description'])
        and ('Модуль' in r['description'] or 'm=' in r['description'])]

kolesa = [r for r in rich if r['description'].startswith('Колесо зубчатое')][:10]
val_kolesa = [r for r in rich if 'ал-колесо' in r['description'][:20] or 'ал колесо' in r['description'][:20] or 'алик-колесо' in r['description'][:20]][:5]
valy = [r for r in all_rows if r['description'].startswith('Вал ') and 'коробки' in r['description']][:5]

samples = kolesa + val_kolesa + valy

print(f'Selected {len(samples)} samples ({len(kolesa)} колёса + {len(val_kolesa)} вал-колёса + {len(valy)} валы)\n')

for i, row in enumerate(samples, 1):
    facts = extract_from_directus(row)
    new_top = gen_description_top(facts)

    print(f'{"="*80}')
    print(f'[{i}] name: {row["name"]}')
    print(f'')
    print(f'--- ИСХОДНЫЙ description (Directus) ---')
    print(row['description'].strip())
    print()
    print(f'--- NEW_DESCRIPTION_TOP (целевой стиль) ---')
    print(new_top)
    print()
