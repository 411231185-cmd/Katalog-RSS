# СКРИПТ: ИСПРАВЛЕНИЕ ДЛИННЫХ ЗАГОЛОВКОВ (улучшенная версия)
# Файл: fix_long_titles_v2.py
# Дата: 2026-01-25

import pandas as pd

# ПУТЬ К ФАЙЛУ
CATALOG_FILE = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\FINAL_CATALOG_FOR_TILDA.csv'
BACKUP_FILE = r'C:\GitHub-Repositories\Katalog-RSS\catalogs\FINAL_CATALOG_BACKUP_titles.csv'

# НАСТРОЙКИ
MAX_LENGTH = 70  # Максимальная длина заголовка

print("="*80)
print("ИСПРАВЛЕНИЕ ДЛИННЫХ ЗАГОЛОВКОВ")
print("="*80)

# Загрузка
df = pd.read_csv(CATALOG_FILE, sep=';', encoding='utf-8')
print(f"\n✅ Загружено: {len(df)} записей")

# Бэкап
df.to_csv(BACKUP_FILE, sep=';', index=False, encoding='utf-8')
print(f"💾 Бэкап: {BACKUP_FILE}")

# АНАЛИЗ
print("\n" + "="*80)
print("АНАЛИЗ ДЛИНЫ ЗАГОЛОВКОВ")
print("="*80)

df['title_length'] = df['Title'].astype(str).str.len()

print(f"\n📊 СТАТИСТИКА:")
print(f"   Средняя длина: {df['title_length'].mean():.0f} символов")
print(f"   Максимальная: {df['title_length'].max():.0f} символов")

long_titles = df[df['title_length'] > MAX_LENGTH]
print(f"\n⚠️ Найдено {len(long_titles)} заголовков длиннее {MAX_LENGTH} символов")

if len(long_titles) > 0:
    print("\nПримеры длинных заголовков:")
    print("-"*80)
    for idx, row in long_titles.head(10).iterrows():
        sku = row.get('SKU', 'N/A')
        title = row['Title']
        length = row['title_length']
        print(f"SKU: {sku}")
        print(f"[{length} симв.] {title}")
        print()

# ПРАВИЛА СОКРАЩЕНИЯ
print("="*80)
print("ПРИМЕНЕНИЕ ПРАВИЛ СОКРАЩЕНИЯ")
print("="*80)

def shorten_title(title, sku, max_length=70):
    """
    Умное сокращение заголовка

    Правила:
    1. Если <= max_length - оставляем как есть
    2. Если > max_length - используем SKU как заголовок
    """
    if pd.isna(title):
        return title

    title = str(title)

    # Правило 1: Короткие заголовки не трогаем
    if len(title) <= max_length:
        return title

    # Правило 2: Длинные заменяем на SKU (если есть)
    if pd.notna(sku) and str(sku) != '' and str(sku) != 'nan':
        return str(sku)

    # Правило 3: Если SKU нет - умно обрезаем
    # Убираем текст в скобках
    if '(' in title:
        title = title.split('(')[0].strip()

    # Если всё ещё длинный - обрезаем
    if len(title) > max_length:
        title = title[:max_length-3].rsplit(' ', 1)[0] + '...'

    return title

# Применяем сокращение
stats = {'shortened': 0, 'unchanged': 0, 'replaced_with_sku': 0}

print(f"\n🔧 Обрабатываем заголовки...\n")

examples_shown = 0
for idx, row in df.iterrows():
    original = row['Title']
    sku = row.get('SKU', '')

    if pd.notna(original) and len(str(original)) > MAX_LENGTH:
        shortened = shorten_title(original, sku, MAX_LENGTH)
        df.at[idx, 'Title'] = shortened
        stats['shortened'] += 1

        if shortened == str(sku):
            stats['replaced_with_sku'] += 1

        # Показываем первые 7 изменений
        if examples_shown < 7:
            print(f"SKU: {sku}")
            print(f"БЫЛО ({len(str(original))} симв.):")
            print(f"  {original}")
            print(f"СТАЛО ({len(shortened)} симв.):")
            print(f"  {shortened}")
            print("-"*80)
            examples_shown += 1
    else:
        stats['unchanged'] += 1

print(f"\n📈 РЕЗУЛЬТАТ:")
print(f"   Сокращено: {stats['shortened']}")
print(f"   Из них заменено на SKU: {stats['replaced_with_sku']}")
print(f"   Без изменений: {stats['unchanged']}")

# Удаляем служебную колонку
if 'title_length' in df.columns:
    df = df.drop('title_length', axis=1)

# СОХРАНЕНИЕ
df.to_csv(CATALOG_FILE, sep=';', index=False, encoding='utf-8')

print(f"\n✅ ГОТОВО!")
print(f"   Файл обновлён: {CATALOG_FILE}")

# ФИНАЛЬНАЯ СТАТИСТИКА
print("\n" + "="*80)
print("ФИНАЛЬНАЯ СТАТИСТИКА")
print("="*80)

df['new_length'] = df['Title'].astype(str).str.len()
print(f"\n📊 После обработки:")
print(f"   Средняя длина: {df['new_length'].mean():.0f} символов")
print(f"   Максимальная: {df['new_length'].max():.0f} символов")
print(f"   Заголовков > {MAX_LENGTH} симв.: {len(df[df['new_length'] > MAX_LENGTH])}")

print("\n💾 Бэкап: " + BACKUP_FILE)
print("="*80)
