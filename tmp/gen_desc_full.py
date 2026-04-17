#!/usr/bin/env python3
"""
gen_desc_full.py — Generate description_new for ALL needs_new items
from PromPortal+шифры-NEW.xlsx.

Based on gen_desc_5.py by Claude. Only change: process ALL items, add progress,
batch CSV write.
"""

import openpyxl, re, html, csv, json, sys, time

# === 1. Load source file ===
XLSX_PATH = 'PLOSIADKI-RSS/PromPortal/PromPortal+шифры-NEW.xlsx'
print(f'[1/5] Loading {XLSX_PATH} ...')
wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
ws = wb['Sheet1']

def strip_html(text):
    if not text: return ''
    text = str(text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()

def strip_article_tail(text):
    text = re.sub(r'\s+', ' ', text).strip()
    match = re.search(r'__[A-Z0-9][A-Za-z0-9_.]+__\s*,?\s*__[A-Z0-9]', text)
    if match:
        return text[:match.start()].strip()
    return text

GENERIC_MARKERS = [
    'запасная часть для токарного станка',
    'Купить с доставкой по России',
    'Подбор по каталогу и чертежам заказчика',
]

headers = None
needs_new = []

for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0:
        headers = list(row)
        desc_idx = headers.index('Описание')
        name_idx = headers.index('Наименование')
        code_idx = headers.index('Код товара')
        continue
    name = str(row[name_idx] or '').strip()
    code = str(row[code_idx] or '').strip()
    if code == 'None': code = ''
    desc_raw = str(row[desc_idx] or '').strip()
    desc_clean = strip_html(desc_raw)
    content = strip_article_tail(re.sub(r'\s+', ' ', desc_clean).strip())
    is_generic = (
        len(content) < 500
        or any(m in content for m in GENERIC_MARKERS)
        or content.strip() == 'Назначение'
    )
    if is_generic:
        needs_new.append({
            'row': i + 1,
            'name': name,
            'code': code,
            'existing_content': content,
        })
wb.close()

print(f'    Total rows: {i}')
print(f'    needs_new: {len(needs_new)}')

# === 2. Load reference: DIRECTUS_TKP_549 for enrichment ===
print('[2/5] Loading DIRECTUS_TKP_549_FULL.csv ...')
dtk_lookup = {}
with open('DIRECTUS_TKP_549_FULL.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        n = row.get('name', '').strip()
        d = row.get('description', '').strip()
        if n and d:
            dtk_lookup[n.lower()] = d
print(f'    DIRECTUS entries loaded: {len(dtk_lookup)}')

# === 2b. Load ATALONNY-PERELIKOVKA.csv for enrichment ===
print('[2b/5] Loading ATALONNY-PERELIKOVKA.csv ...')
atalon_lookup = {}
try:
    with open('ATALONNY-PERELIKOVKA.csv', 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            title = row.get('Title', '').strip()
            desc = strip_html(row.get('Description', ''))
            text = strip_html(row.get('Text', ''))
            combined = (desc + ' ' + text).strip()
            if title and combined:
                atalon_lookup[title.lower()] = combined
except Exception as e:
    print(f'    Warning: could not load ATALONNY: {e}')
print(f'    ATALONNY entries loaded: {len(atalon_lookup)}')

# === 3. Parsing helpers (exact copy from gen_desc_5.py) ===
print('[3/5] Initializing templates and helpers ...')

MACHINE_MODELS = re.compile(
    r'(?:мод\.\s*)?'
    r'(1[AMНК]6[0-9][A-ZА-Я0-9Ф]*'
    r'|16[КМРБA][0-9]+[А-ЯA-ZФ0-9]*'
    r'|ДИП[- ]?\d+'
    r'|РТ[- ]?\d+[А-ЯA-ZФ0-9]*'
    r'|[126]\d{0,1}[ТГКРНМA][0-9]+[А-ЯA-ZФ0-9]*'
    r'|СА\d+'
    r'|UBB\d+[A-ZФ0-9]*'
    r'|FU\d+[A-Z]*'
    r'|FSS\s?\d+[A-Z]*'
    r'|КЖ\s?\d+'
    r'|F\d+R?'
    r')',
    re.IGNORECASE
)

ASSEMBLY_MAP = {
    'шпиндельн': 'шпиндельной бабке (коробке скоростей)',
    'коробк подач': 'коробке подач',
    'коробк скорост': 'коробке скоростей (шпиндельной бабке)',
    'фартук': 'фартуке',
    'суппорт': 'суппорте',
    'каретк': 'каретке',
    'задн': 'задней бабке',
    'револьверн': 'револьверной головке',
    'люнет': 'люнете',
    'патрон': 'токарном патроне',
    'реверс': 'механизме реверса',
}

PART_TEMPLATES = {
    'вал': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает передачу крутящего момента между узлами привода, '
        'работает совместно с зубчатыми колёсами и подшипниковыми опорами. '
        'Поставляется как отдельно, так и в сборе с сопряжёнными деталями.'
    ),
    'шестерн': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Участвует в передаче вращения и переключении режимов работы узла, '
        'работает в паре с валами и другими зубчатыми колёсами. '
        'Поставляется поштучно и комплектами.'
    ),
    'колесо зубчат': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает передачу вращения в кинематической цепи узла, '
        'работает совместно с валами и сопряжёнными шестернями. '
        'Поставляется по каталожному номеру или чертежу.'
    ),
    'винт': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает точное перемещение подвижных узлов станка, '
        'работает в паре с маточной гайкой. '
        'Поставляется отдельно и в сборе с гайками.'
    ),
    'гайк': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает фиксацию и регулировку положения подвижных узлов станка, '
        'работает совместно с ходовым винтом или крепёжными элементами. '
        'Поставляется отдельно и в комплекте.'
    ),
    'муфт': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает соединение и разъединение валов привода, '
        'передаёт крутящий момент между узлами кинематической цепи. '
        'Поставляется в сборе, готовой к установке.'
    ),
    'втулк': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Служит переходным или опорным элементом, обеспечивая точную посадку '
        'сопряжённых деталей в узле. '
        'Поставляется по каталожному номеру.'
    ),
    'диск': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Выполняет функцию рабочего элемента узла, обеспечивая фиксацию, '
        'торможение или крепление инструмента. '
        'Поставляется отдельно и в комплекте с сопряжёнными деталями.'
    ),
    'кулачк': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает зажим и центрирование обрабатываемой заготовки в патроне. '
        'Поставляется комплектами и поштучно, прямые и обратные исполнения.'
    ),
    'ролик': None,  # handled specially in generate_description
    'блок': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Представляет собой сборный узел, обеспечивающий передачу движения '
        'и переключение рабочих режимов. '
        'Поставляется в сборе.'
    ),
    'венец': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает передачу вращения от привода к кулачкам патрона '
        'для зажима и разжима заготовки. '
        'Поставляется по каталожному номеру.'
    ),
    'шкив': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Передаёт крутящий момент от электродвигателя к шпинделю '
        'через клиноремённую передачу. '
        'Поставляется отдельно.'
    ),
    'пружин': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает возвратное усилие, прижим или фиксацию подвижных элементов узла. '
        'Поставляется поштучно и комплектами.'
    ),
    'вилк': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Служит для переключения зубчатых колёс или муфт, '
        'обеспечивая смену режимов работы узла. '
        'Поставляется отдельно.'
    ),
    'клин': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает регулировку зазора в направляющих и устранение люфта '
        'подвижных узлов станка. '
        'Поставляется по размерам заказчика.'
    ),
    'резцедержател': (
        '{name} применяется на токарно-винторезных станках мод. {models}. '
        'Предназначен для крепления и быстрой смены режущего инструмента. '
        'Поставляется в сборе, готовым к установке на суппорт.'
    ),
    'швп': (
        '{name} применяется в {assembly} станков с ЧПУ мод. {models}. '
        'Преобразует вращательное движение серводвигателя в точное прямолинейное '
        'перемещение рабочих органов станка. '
        'Поставляется в сборе с гайкой, готовой к монтажу.'
    ),
    'шарико-винтов': (
        '{name} применяется в {assembly} станков с ЧПУ мод. {models}. '
        'Преобразует вращательное движение серводвигателя в точное прямолинейное '
        'перемещение рабочих органов станка. '
        'Поставляется в сборе с гайкой, готовой к монтажу.'
    ),
    'головк': (
        '{name} — автоматическое устройство для крепления и быстрой смены '
        'режущего инструмента на станках с ЧПУ мод. {models}. '
        'Обеспечивает точное позиционирование инструментальных блоков '
        'и сокращение вспомогательного времени обработки. '
        'Поставляется в сборе с комплектом документации.'
    ),
    'насос': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает подачу смазки к узлам и механизмам станка. '
        'Поставляется в сборе.'
    ),
    'лимб': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает визуальный контроль величины перемещения подвижных узлов станка. '
        'Поставляется в сборе с кольцом и осью.'
    ),
    'нониус': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает визуальный контроль величины перемещения подвижных узлов станка. '
        'Поставляется в сборе.'
    ),
    'скреб': (
        '{name} применяется на токарно-винторезных станках мод. {models}. '
        'Защищает направляющие станины от попадания стружки и абразивных частиц, '
        'продлевая срок службы направляющих. '
        'Поставляется комплектами на каретку и заднюю бабку.'
    ),
    'лент': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает торможение шпинделя при остановке и реверсе. '
        'Поставляется отдельно.'
    ),
    'рычаг': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Служит для переключения режимов работы узла и управления механизмами станка. '
        'Поставляется отдельно.'
    ),
    'ручк': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Обеспечивает ручное управление перемещением подвижных узлов станка. '
        'Поставляется в сборе.'
    ),
    'кронштейн': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Служит для крепления и фиксации смежных узлов и механизмов. '
        'Поставляется отдельно.'
    ),
    'корпус': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Является несущим элементом, в котором размещаются рабочие механизмы узла. '
        'Поставляется отдельно и в сборе.'
    ),
    'водило': (
        '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
        'Является элементом планетарной передачи, обеспечивает индексацию и '
        'фиксацию рабочих позиций. '
        'Поставляется отдельно и в комплекте с шестернями.'
    ),
    'станок': (
        '{name} — металлорежущее оборудование производства ТД РУССтанкоСбыт. '
        'Предназначен для выполнения токарных операций: наружное и внутреннее точение, '
        'нарезание резьб, растачивание. '
        'Поставляется в полной комплектации с паспортом и гарантией.'
    ),
}

DEFAULT_TEMPLATE = (
    '{name} применяется в {assembly} токарно-винторезных станков мод. {models}. '
    'Обеспечивает работоспособность узла, поставляется как запасная часть '
    'для ремонта и обслуживания оборудования. '
    'При заказе сверяйте каталожный номер по паспорту станка.'
)

SERVICES_BLOCK = (
    'Подобрать конкретную запчасть вы можете у нас на сайте в разделе Каталог ТД РУССтанкоСбыт.\n'
    'Поставка и изготовление ПАТРОНОВ для станков — токарные и специальные патроны.\n'
    'Поставка ПОДШИПНИКОВ для станков — шариковые, роликовые и упорные подшипники.\n'
    'Поставка и изготовление ЦЕНТРОВ для токарных станков — центры с конусом Морзе.\n'
    'Изготовление СУППОРТОВ для токарных станков — суппорты в сборе под заказ.\n'
    'Изготовление ПЛАНШАЙБ для токарных станков — планшайбы под заказ.\n'
    'Изготовление ШВП для станков — шарико\u2011винтовые пары под заказ.\n'
    'Изготовление ВИНТОВ для станков — ходовые винты, винты подачи и специальные винты под заказ.\n'
    'Изготовление ВАЛОВ для станков — вал\u2011шестерни, шлицевые и приводные валы под заказ.\n'
    'Изготовление ВТУЛОК для станков — переходные, опорные и направляющие втулки под заказ.\n'
    'Изготовление ШЕСТЕРЁН для станков — зубчатые колёса и шестерни под заказ.\n'
    'Изготовление ЛЮНЕТОВ для токарных станков — неподвижные и подвижные люнеты под заказ.\n'
    'Изготовление ЗАЩИТНЫХ КОЖУХОВ для станков любой сложности.\n'
    'Изготовление КАБИНЕТНЫХ ЗАЩИТ для станков любой сложности.\n'
    'Изготовление ВКЛАДЫШЕЙ и ЗАХВАТОВ для станков — оснастка под заказ.'
)


def extract_models(name):
    found = MACHINE_MODELS.findall(name)
    seen = []
    for m in found:
        m_clean = m.strip().rstrip(',.')
        if m_clean and m_clean not in seen and len(m_clean) >= 3:
            seen.append(m_clean)
    return seen


def detect_assembly(name):
    name_lower = name.lower()
    for keyword, assembly in ASSEMBLY_MAP.items():
        if keyword in name_lower:
            return assembly
    if any(w in name_lower for w in ['подач', 'коробк']):
        return 'коробке подач'
    if 'фрезерн' in name_lower:
        return 'приводе консольно-фрезерных станков'
    return 'узлах'


def detect_part_type(name):
    name_lower = name.lower()
    for keyword in PART_TEMPLATES:
        if keyword in name_lower:
            return keyword
    return None


def is_frezerny(name):
    return any(w in name.lower() for w in [
        'фрезерн', 'fu4', 'fu3', 'fss', 'f400', '6т8', '6р8',
        '6р12', '6р13', '6н12', 'гф2'
    ])

def is_karuselny(name):
    return any(w in name.lower() for w in ['карусел', '1512', '1516', '1525'])

def is_cnc(name):
    return any(w in name.lower() for w in ['чпу', 'ф3', 'ф4', 'ф1', 'cnc'])

def stanok_type_str(name):
    if is_frezerny(name):
        return 'консольно-фрезерных станков'
    if is_karuselny(name):
        return 'токарно-карусельных станков'
    if is_cnc(name):
        return 'токарных станков с ЧПУ'
    return 'токарно-винторезных станков'

def is_lyunet_roller(name):
    return 'люнет' in name.lower()

def is_nakatnoj_roller(name):
    nl = name.lower()
    return ('упрочн' in nl or 'сглажив' in nl or 'накат' in nl
            or 'рт301' in nl or 'рт917' in nl or 'кж' in nl)


def generate_description(item):
    name = item['name']
    models = extract_models(name)
    models_str = ', '.join(models) if models else 'по паспорту станка'
    assembly = detect_assembly(name)
    part_type = detect_part_type(name)
    stype = stanok_type_str(name)

    # Try DIRECTUS lookup — only use if text is specific, not generic
    dtk_desc = dtk_lookup.get(name.lower(), '')
    if dtk_desc and len(dtk_desc) > 80:
        lines = dtk_desc.split('\n')
        tech_text = ' '.join(l.strip() for l in lines if l.strip() and 'При подборе' not in l)
        generic_dtk = [
            'запасная часть для токарного станка',
            'вал токарного станка',
            'шестерня токарного станка',
        ]
        if len(tech_text) > 100 and not any(g in tech_text for g in generic_dtk):
            return tech_text.strip()

    # Try ATALONNY lookup — only use if text is specific enough
    atalon_desc = atalon_lookup.get(name.lower(), '')
    if atalon_desc and len(atalon_desc) > 80:
        atalon_clean = re.sub(r'\s+', ' ', atalon_desc).strip()
        generic_at = [
            'запасная часть',
            'Купить с доставкой',
            'Подбор по каталогу',
        ]
        if len(atalon_clean) > 100 and not any(g in atalon_clean for g in generic_at):
            # Trim to first 3 sentences max
            sentences = re.split(r'(?<=[.!])\s+', atalon_clean)
            tech_part = ' '.join(sentences[:3])
            if len(tech_part) > 80:
                return tech_part.strip()

    # Special handling for ролики
    if part_type == 'ролик':
        if is_lyunet_roller(name):
            return (
                f'{name} применяется в люнетах {stype} мод. {models_str}. '
                'Обеспечивает надёжную опору длинных заготовок при обработке, '
                'предотвращая прогиб и вибрацию. '
                'Поставляется в сборе с вилкой (пинолью), готовым к установке.'
            )
        elif is_nakatnoj_roller(name):
            return (
                f'{name} применяется на токарно-накатных станках мод. {models_str}. '
                'Предназначен для поверхностного пластического деформирования — '
                'упрочнения или сглаживания обрабатываемых поверхностей. '
                'Поставляется в сборе с вилкой, готовым к установке в накатное устройство.'
            )
        else:
            return (
                f'{name} применяется в {assembly} {stype} мод. {models_str}. '
                'Обеспечивает работоспособность узла, поставляется как запасная часть. '
                'При заказе сверяйте каталожный номер по паспорту станка.'
            )

    # Special: патроны (не «кулачки», а именно целый патрон)
    if 'патрон' in name.lower() and part_type == 'кулачк':
        part_type = None
    if 'патрон' in name.lower() and part_type is None:
        if models_str == 'по паспорту станка':
            models_str = 'ДИП500, 1М65, 1Н65, РТ117, РТ817 и аналогичных'
        return (
            f'{name} — механизированное зажимное устройство для {stype} мод. {models_str}. '
            'Обеспечивает автоматический зажим и центрирование заготовок. '
            'Поставляется в сборе с кулачками, готовым к установке на шпиндель.'
        )

    # Special: станки
    if part_type == 'станок' or name.lower().startswith('станок') or 'токарн' in name.lower()[:20]:
        if 'станок' in name.lower() or 'токарн' in name.lower()[:20]:
            return (
                f'{name} — металлорежущее оборудование производства ТД РУССтанкоСбыт. '
                'Предназначен для выполнения токарных операций: наружное и внутреннее точение, '
                'нарезание резьб, растачивание. '
                'Поставляется в полной комплектации с паспортом и гарантией.'
            )

    if part_type and part_type in PART_TEMPLATES:
        template = PART_TEMPLATES[part_type]
        if template is None:
            template = DEFAULT_TEMPLATE
    else:
        template = DEFAULT_TEMPLATE

    result = template.format(
        name=name,
        assembly=assembly,
        models=models_str,
    )
    if stype != 'токарно-винторезных станков':
        if 'фрезерн' in assembly:
            result = result.replace('токарно-винторезных станков мод.', 'мод.')
        else:
            result = result.replace('токарно-винторезных станков', stype)
    return result


# === 4. Generate for ALL needs_new ===
print(f'[4/5] Generating descriptions for {len(needs_new)} items ...')
OUT_PATH = 'tmp/description_new_full.csv'
t0 = time.time()

with open(OUT_PATH, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['row', 'code', 'name', 'description_new'])
    writer.writeheader()

    for idx, item in enumerate(needs_new, 1):
        tech_desc = generate_description(item)
        description_new = tech_desc + '\n\n' + SERVICES_BLOCK
        writer.writerow({
            'row': item['row'],
            'code': item['code'],
            'name': item['name'],
            'description_new': description_new,
        })

        if idx % 500 == 0 or idx == len(needs_new):
            elapsed = time.time() - t0
            print(f'    [{idx}/{len(needs_new)}] done  ({elapsed:.1f}s)')

elapsed = time.time() - t0
print(f'[5/5] Written {len(needs_new)} rows to {OUT_PATH}  ({elapsed:.1f}s total)')
print('Done.')
