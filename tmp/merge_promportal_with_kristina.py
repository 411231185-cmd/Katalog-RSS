#!/usr/bin/env python3
"""
merge_promportal_with_kristina.py
Сливает три источника в один финальный Excel-файл:
  1. PromPortal+шифры-NEW.xlsx  — основная структура товаров (2491 строка)
  2. description_new_full.csv   — сгенерированные описания (2387 позиций)
  3. export от Кристины.xlsx    — старая рабочая выгрузка с богатыми описаниями

Принцип слияния:
  • Шаг 1: df_prom LEFT JOIN df_desc  по  row  →  description_new
  • Шаг 2: df_prom LEFT JOIN df_kristina  по  name (fuzzy-нормализованное)
           →  old_name_kristina, old_description_kristina

Для ~104 позиций без description_new — берём существующее «Описание» из xlsx
и дописываем стандартный блок услуг.
"""

import pandas as pd
import re, html, os, sys

# ====================================================================
# PATHS — адаптированы для sandbox; для локального запуска на Windows
# замените BASE на r"C:\GitHub-Repositories\Katalog-RSS"
# ====================================================================
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROM_XLSX   = os.path.join(BASE, 'PLOSIADKI-RSS', 'PromPortal', 'PromPortal+шифры-NEW.xlsx')
DESC_CSV    = os.path.join(BASE, 'tmp', 'description_new_full.csv')

# Экспорт Кристины — пробуем несколько вариантов расположения
KRISTINA_CANDIDATES = [
    os.path.join(BASE, 'PLOSIADKI-RSS', 'PromPortal', 'Каталоги', 'export от Кристины.xlsx'),
    os.path.join(BASE, 'PLOSIADKI-RSS', 'PromPortal', 'UPLOAD_READY.xlsx'),
    os.path.join(BASE, 'PLOSIADKI-RSS', 'PromPortal', 'СПИСОК ОФФЕРОВ+ОПИСАНИЕ.xlsx'),
]

OUT_XLSX = os.path.join(BASE, 'PLOSIADKI-RSS', 'PromPortal', 'PromPortal-FINAL-with-descriptions.xlsx')

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


def strip_html(text):
    """Убрать HTML-теги, декодировать entities."""
    if not text or pd.isna(text):
        return ''
    text = str(text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def normalize_name(name):
    """Нормализовать наименование для fuzzy-мэтчинга: lower, убрать лишние пробелы."""
    if not name or pd.isna(name):
        return ''
    s = str(name).strip().lower()
    s = re.sub(r'\s+', ' ', s)
    return s


# ====================================================================
# 1. Читаем PromPortal+шифры-NEW.xlsx
# ====================================================================
print(f'[1/6] Читаю {PROM_XLSX} ...')
df_prom = pd.read_excel(PROM_XLSX, engine='openpyxl')
# Добавляем row = 1-based номер строки (строка 1 = заголовок, данные с 2)
df_prom.insert(0, 'row', range(2, len(df_prom) + 2))
print(f'       {len(df_prom)} строк, колонки: {list(df_prom.columns[:10])} ...')

# ====================================================================
# 2. Читаем description_new_full.csv
# ====================================================================
print(f'[2/6] Читаю {DESC_CSV} ...')
df_desc = pd.read_csv(DESC_CSV, encoding='utf-8')
print(f'       {len(df_desc)} строк')

# ====================================================================
# 3. Читаем export от Кристины
# ====================================================================
KRISTINA_PATH = None
for cand in KRISTINA_CANDIDATES:
    if os.path.exists(cand):
        KRISTINA_PATH = cand
        break

if KRISTINA_PATH:
    print(f'[3/6] Читаю {KRISTINA_PATH} ...')
    df_kristina = pd.read_excel(KRISTINA_PATH, engine='openpyxl')
    print(f'       {len(df_kristina)} строк')
else:
    print('[3/6] ⚠ Экспорт Кристины не найден ни по одному из путей:')
    for c in KRISTINA_CANDIDATES:
        print(f'       - {c}')
    print('       Продолжаю без него (old_name_kristina / old_description_kristina будут пустые).')
    df_kristina = None

# ====================================================================
# 4. Шаг 1: df_prom + df_desc  по  row
# ====================================================================
print('[4/6] Слияние PromPortal + description_new  по row ...')
df_desc_slim = df_desc[['row', 'description_new']].copy()
df_desc_slim['row'] = df_desc_slim['row'].astype(int)
df_prom['row'] = df_prom['row'].astype(int)

df_merged = df_prom.merge(df_desc_slim, on='row', how='left')

filled = df_merged['description_new'].notna().sum()
missing = df_merged['description_new'].isna().sum()
print(f'       Заполнено description_new: {filled}, пусто: {missing}')

# Для позиций без description_new — берём очищенное «Описание» + блок услуг
mask_empty = df_merged['description_new'].isna()
if mask_empty.any():
    print(f'       Дозаполняю {mask_empty.sum()} позиций из существующего «Описание» + блок услуг ...')
    for idx in df_merged.index[mask_empty]:
        raw_desc = df_merged.at[idx, 'Описание']
        clean = strip_html(raw_desc)
        if clean and len(clean) > 20:
            df_merged.at[idx, 'description_new'] = clean + '\n\n' + SERVICES_BLOCK
        else:
            # Совсем короткое — используем наименование как базу
            name = str(df_merged.at[idx, 'Наименование'] or '').strip()
            fallback = (
                f'{name} — запасная часть / комплектующее для металлорежущих станков. '
                'Поставляется ТД РУССтанкоСбыт. '
                'При заказе сверяйте каталожный номер по паспорту станка.'
            )
            df_merged.at[idx, 'description_new'] = fallback + '\n\n' + SERVICES_BLOCK

total_filled = df_merged['description_new'].notna().sum()
print(f'       Итого description_new заполнено: {total_filled}/{len(df_merged)}')

# ====================================================================
# 5. Шаг 2: подтянуть данные из Кристины
# ====================================================================
print('[5/6] Подтягиваю старые описания из экспорта Кристины ...')

if df_kristina is not None:
    # Определяем колонки в файле Кристины
    kr_name_col = 'Наименование' if 'Наименование' in df_kristina.columns else None
    kr_desc_col = 'Описание' if 'Описание' in df_kristina.columns else None
    kr_code_col = 'Код товара' if 'Код товара' in df_kristina.columns else None

    if kr_name_col and kr_desc_col:
        # Нормализуем наименование для join
        df_kristina['_name_norm'] = df_kristina[kr_name_col].apply(normalize_name)
        df_merged['_name_norm'] = df_merged['Наименование'].apply(normalize_name)

        # Убираем дубли в Кристине — оставляем первую запись с самым длинным описанием
        df_kristina['_desc_len'] = df_kristina[kr_desc_col].apply(
            lambda x: len(strip_html(x)) if x and not pd.isna(x) else 0
        )
        df_kr_dedup = (
            df_kristina
            .sort_values('_desc_len', ascending=False)
            .drop_duplicates(subset='_name_norm', keep='first')
        )

        # Готовим slim-версию для join
        kr_slim = df_kr_dedup[['_name_norm', kr_name_col, kr_desc_col]].copy()
        kr_slim = kr_slim.rename(columns={
            kr_name_col: 'old_name_kristina',
            kr_desc_col: 'old_description_kristina_raw',
        })

        df_merged = df_merged.merge(kr_slim, on='_name_norm', how='left')

        # Очищаем HTML из старых описаний Кристины
        df_merged['old_description_kristina'] = df_merged['old_description_kristina_raw'].apply(strip_html)
        df_merged.drop(columns=['old_description_kristina_raw', '_name_norm'], inplace=True)

        matched = df_merged['old_name_kristina'].notna().sum()
        print(f'       Сопоставлено с Кристиной по наименованию: {matched}/{len(df_merged)}')
    else:
        print(f'       ⚠ Не найдены колонки Наименование/Описание в Кристине')
        df_merged['old_name_kristina'] = ''
        df_merged['old_description_kristina'] = ''
else:
    df_merged['old_name_kristina'] = ''
    df_merged['old_description_kristina'] = ''
    if '_name_norm' in df_merged.columns:
        df_merged.drop(columns=['_name_norm'], inplace=True)

# Чистим служебные колонки
for col in ['_name_norm', '_desc_len']:
    if col in df_merged.columns:
        df_merged.drop(columns=[col], inplace=True)

# ====================================================================
# 6. Сохраняем финальный Excel
# ====================================================================
print(f'[6/6] Сохраняю {OUT_XLSX} ...')

# Переупорядочиваем колонки: row, Код товара, Наименование, Описание (оригинал),
# description_new, old_name_kristina, old_description_kristina, ... остальные
priority_cols = [
    'row', 'Код товара', 'Наименование', 'Описание',
    'description_new', 'old_name_kristina', 'old_description_kristina',
]
other_cols = [c for c in df_merged.columns if c not in priority_cols]
final_cols = [c for c in priority_cols if c in df_merged.columns] + other_cols
df_merged = df_merged[final_cols]

df_merged.to_excel(OUT_XLSX, index=False, engine='openpyxl')

print(f'\n{"="*60}')
print(f'ГОТОВО: {OUT_XLSX}')
print(f'Строк: {len(df_merged)}')
print(f'Колонок: {len(df_merged.columns)}')
print(f'{"="*60}')

# Показать первые 10 строк
print('\n=== ПЕРВЫЕ 10 СТРОК (ключевые поля) ===')
show_cols = ['row', 'Код товара', 'Наименование', 'description_new', 'old_name_kristina']
show_cols = [c for c in show_cols if c in df_merged.columns]
pd.set_option('display.max_colwidth', 60)
pd.set_option('display.width', 200)
print(df_merged[show_cols].head(10).to_string(index=False))

# Статистика
print('\n=== СТАТИСТИКА ===')
print(f'  Всего строк:                        {len(df_merged)}')
dn = df_merged['description_new']
print(f'  description_new заполнено:           {dn.notna().sum()}')
print(f'  description_new пусто:               {dn.isna().sum()}')
if 'old_name_kristina' in df_merged.columns:
    kr = df_merged['old_name_kristina']
    print(f'  Сопоставлено с Кристиной:            {kr.notna().sum()}')
    print(f'  Не сопоставлено:                     {kr.isna().sum()}')
avg_len = dn.dropna().apply(len).mean()
print(f'  Средняя длина description_new:       {avg_len:.0f} символов')
