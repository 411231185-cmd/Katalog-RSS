#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO-оптимизатор каталога РСС
Извлекает модели станков, типы деталей, генерирует ключевые слова
"""

import pandas as pd
import re
from collections import Counter
import os

# ========================================
# СКРИПТ A: SEO-ОПТИМИЗАЦИЯ КАТАЛОГА
# ========================================

def extract_model_numbers(title, description):
    """Извлекает модели станков из названия и описания"""
    # Паттерн для моделей станков: 1М63, 16К20, РТ-817, ДИП300, UBB252
    pattern = r'\b(?:1[МНА]?\d{2,3}[НБКМФ]*\d*|16[КР]?\d{2}[ФНБ]*\d*|РТ-?\d{3,4}|ДИП-?\d{3}|UBB\d{3}|ГС\d{3})\b'
    
    models = set()
    
    if pd.notna(title):
        models.update(re.findall(pattern, str(title), re.IGNORECASE))
    
    if pd.notna(description):
        models.update(re.findall(pattern, str(description), re.IGNORECASE))
    
    return ';'.join(sorted(models)) if models else ''


def extract_part_types(title, category):
    """Определяет типы деталей на основе ключевых слов"""
    types = []
    
    keywords_map = {
        'вал': ['вал', 'валик', 'вал-'],
        'винт': ['винт'],
        'гайка': ['гайка'],
        'шестерня': ['шестерня', 'шестерен', 'блок-шестерн', 'зубчатое колесо'],
        'колесо': ['колесо'],
        'муфта': ['муфта'],
        'патрон': ['патрон'],
        'револьверная_головка': ['револьверн'],
        'фартук': ['фартук'],
        'суппорт': ['суппорт', 'каретка'],
        'бабка': ['бабка'],
        'коробка': ['коробка'],
        'электрооборудование': ['электро', 'двигатель', 'пускатель'],
        'подшипник': ['подшипник'],
        'ручка': ['ручка', 'рукоятка'],
        'прокладка': ['прокладка'],
        'пружина': ['пружина']
    }
    
    text = f"{str(title).lower()} {str(category).lower()}"
    
    for part_type, patterns in keywords_map.items():
        if any(p in text for p in patterns):
            types.append(part_type)
    
    return ';'.join(types) if types else 'общая_деталь'


def generate_search_keywords(row):
    """Генерирует поисковые ключевые слова для SEO"""
    keywords = []
    
    # 1. Модели станков
    if row.get('Models'):
        models = str(row['Models']).split(';')
        keywords.extend(models)
    
    # 2. Типы деталей (заменяем _ на пробел)
    if row.get('PartTypes'):
        types = str(row['PartTypes']).replace('_', ' ')
        keywords.extend(types.split(';'))
    
    # 3. Бренд
    if pd.notna(row.get('Brand')):
        keywords.append(str(row['Brand']))
    
    # 4. Артикул
    if pd.notna(row.get('SKU')):
        keywords.append(str(row['SKU']))
    
    # 5. Значимые слова из заголовка (минимум 4 буквы)
    if pd.notna(row.get('Title')):
        title_words = re.findall(r'\b[А-Яа-яA-Za-z]{4,}\b', str(row['Title']))
        keywords.extend(title_words[:5])  # Берём первые 5
    
    # 6. Категория
    if pd.notna(row.get('Category')):
        cat_words = str(row['Category']).split()
        keywords.extend(cat_words[:3])
    
    # Убираем дубликаты, сохраняя порядок
    unique_keywords = list(dict.fromkeys([k.strip() for k in keywords if k and len(str(k).strip()) > 1]))
    
    # Ограничиваем 15 ключами
    return ';'.join(unique_keywords[:15])


def optimize_catalog(input_file, output_file):
    """Основная функция SEO-оптимизации каталога"""
    
    print("📂 Загрузка каталога...")
    df = pd.read_csv(input_file, sep=';', encoding='utf-8-sig')
    
    print(f"✅ Загружено записей: {len(df)}")
    print(f"📊 Колонки: {', '.join(df.columns.tolist())}")
    
    # Создаём новые колонки для SEO
    print("\n🔍 Извлечение моделей станков...")
    df['Models'] = df.apply(
        lambda row: extract_model_numbers(row.get('Title'), row.get('Description')), 
        axis=1
    )
    
    print("🔧 Определение типов деталей...")
    df['PartTypes'] = df.apply(
        lambda row: extract_part_types(row.get('Title'), row.get('Category')), 
        axis=1
    )
    
    print("🏷️ Генерация ключевых слов...")
    df['SearchKeywords'] = df.apply(generate_search_keywords, axis=1)
    
    # Статистика
    models_count = df['Models'].str.len().gt(0).sum()
    avg_keywords = df['SearchKeywords'].str.split(';').str.len().mean()
    
    print(f"\n📊 СТАТИСТИКА SEO:")
    print(f"  • Записей с моделями: {models_count} ({models_count/len(df)*100:.1f}%)")
    print(f"  • Среднее кол-во ключевых слов: {avg_keywords:.1f}")
    
    # ТОП-10 моделей
    all_models = []
    for models in df['Models'].dropna():
        if models:
            all_models.extend(models.split(';'))
    
    if all_models:
        model_counter = Counter(all_models)
        print(f"\n🏆 ТОП-10 моделей станков:")
        for model, count in model_counter.most_common(10):
            print(f"  • {model}: {count}")
    
    # Сохранение
    print(f"\n💾 Сохранение оптимизированного каталога: {output_file}")
    df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    
    print(f"\n✅ SEO-ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!")
    print(f"   Файл: {output_file}")
    print(f"   Записей: {len(df)}")
    print(f"   Новые колонки: Models, PartTypes, SearchKeywords")
    
    return df


# ========================================
# ТОЧКА ВХОДА
# ========================================
if __name__ == "__main__":
    # Путь к входному каталогу
    INPUT_FILE = os.getenv('INPUT_CATALOG', 'catalogs/TOP-KATALOG-s-prefiksami-i-foto.csv')
    
    # Путь к выходному файлу
    OUTPUT_FILE = os.getenv('OUTPUT_CATALOG', 'catalogs/TOP-KATALOG-SEO-optimized.csv')
    
    print("=" * 60)
    print("🚀 SEO-ОПТИМИЗАТОР КАТАЛОГА РСС")
    print("=" * 60)
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ ОШИБКА: Файл не найден: {INPUT_FILE}")
        exit(1)
    
    try:
        result_df = optimize_catalog(INPUT_FILE, OUTPUT_FILE)
        print("\n✅ УСПЕШНО ЗАВЕРШЕНО!")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
