#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ДИАГНОСТИЧЕСКИЙ СКРИПТ для анализа каталога Rezerv-chisty copy.csv
Показывает:
- Структуру CSV
- Проблемные товары (Price: 0.0, Quantity: ∞)
- Распределение по категориям
- Статистику по каждому полю
"""

import pandas as pd
import json
import os
from pathlib import Path
from collections import Counter

# Пути
CATALOG_PATH = "catalogs/Rezerv-chisty copy.csv"
REPORT_PATH = "catalogs/diagnostic_report.json"

def load_catalog():
    """Загружает CSV каталог"""
    try:
        df = pd.read_csv(CATALOG_PATH, encoding='utf-8')
        print(f"✅ Загружен каталог: {CATALOG_PATH}")
        print(f"📊 Всего товаров: {len(df)}")
        print(f"📋 Столбцы: {list(df.columns)}\n")
        return df
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None

def analyze_structure(df):
    """Анализирует структуру CSV"""
    print("=" * 80)
    print("📋 СТРУКТУРА CSV ФАЙЛА")
    print("=" * 80)
    
    analysis = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": {},
        "data_types": {}
    }
    
    for col in df.columns:
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        dtype = str(df[col].dtype)
        unique_count = df[col].nunique()
        
        analysis["columns"][col] = {
            "data_type": dtype,
            "non_null": int(non_null),
            "null": int(null_count),
            "unique_values": int(unique_count),
            "sample_value": str(df[col].iloc[0]) if len(df) > 0 else None
        }
        
        print(f"\n📌 {col}")
        print(f"   Type: {dtype} | Заполнено: {non_null}/{len(df)} | Уникальных: {unique_count}")
        print(f"   Sample: {df[col].iloc[0]}")
    
    return analysis

def analyze_price_issues(df):
    """Анализирует проблемы с ценами"""
    print("\n" + "=" * 80)
    print("💰 АНАЛИЗ ЦЕН (Price field)")
    print("=" * 80)
    
    if 'Price' not in df.columns:
        print("⚠️  Столбец Price не найден!")
        return {}
    
    issues = {
        "zero_price": [],
        "negative_price": [],
        "empty_price": [],
        "non_numeric_price": [],
        "price_distribution": {}
    }
    
    # Попытка конвертировать в float
    df['Price_numeric'] = pd.to_numeric(df['Price'], errors='coerce')
    
    # Товары с нулевой ценой
    zero_price = df[df['Price_numeric'] == 0.0]
    print(f"\n🔴 Товары с Price = 0.0: {len(zero_price)}")
    if len(zero_price) > 0:
        print("   Примеры:")
        for idx, row in zero_price.head(5).iterrows():
            sku = row.get('SKU', 'N/A')
            title = row.get('Title', 'N/A')
            print(f"   - SKU: {sku} | {title[:50]}")
        issues["zero_price"] = len(zero_price)
    
    # Товары с отрицательной ценой
    negative_price = df[df['Price_numeric'] < 0]
    print(f"\n🟡 Товары с отрицательной ценой: {len(negative_price)}")
    issues["negative_price"] = len(negative_price)
    
    # Пустые цены
    empty_price = df[df['Price_numeric'].isna()]
    print(f"\n⚪ Товары с пустой ценой: {len(empty_price)}")
    issues["empty_price"] = len(empty_price)
    
    # Статистика цен
    valid_prices = df[df['Price_numeric'] > 0]['Price_numeric']
    if len(valid_prices) > 0:
        print(f"\n✅ Товары с корректной ценой: {len(valid_prices)}")
        print(f"   Минимальная цена: {valid_prices.min()}")
        print(f"   Максимальная цена: {valid_prices.max()}")
        print(f"   Средняя цена: {valid_prices.mean():.2f}")
    
    return issues

def analyze_quantity_issues(df):
    """Анализирует проблемы с количеством"""
    print("\n" + "=" * 80)
    print("📦 АНАЛИЗ КОЛИЧЕСТВА (Quantity field)")
    print("=" * 80)
    
    if 'Quantity' not in df.columns:
        print("⚠️  Столбец Quantity не найден!")
        return {}
    
    issues = {
        "infinity_quantity": [],
        "zero_quantity": [],
        "empty_quantity": [],
        "valid_quantity": 0
    }
    
    print(f"\n📊 Примеры значений Quantity:")
    print(f"   {df['Quantity'].value_counts().head(10).to_dict()}")
    
    # Считаем символы ∞
    infinity_count = (df['Quantity'] == '∞').sum() + (df['Quantity'] == 'inf').sum()
    print(f"\n🔴 Товары с Quantity = ∞ (бесконечность): {infinity_count}")
    issues["infinity_quantity"] = infinity_count
    
    # Товары с 0 количеством
    zero_qty = (df['Quantity'] == '0') | (df['Quantity'] == 0)
    print(f"\n🟡 Товары с Quantity = 0: {zero_qty.sum()}")
    issues["zero_quantity"] = zero_qty.sum()
    
    # Пустые
    empty_qty = df['Quantity'].isna() | (df['Quantity'] == '')
    print(f"\n⚪ Товары с пустым Quantity: {empty_qty.sum()}")
    issues["empty_quantity"] = empty_qty.sum()
    
    # Корректные (числовые)
    valid_qty = 0
    try:
        numeric_qty = pd.to_numeric(df['Quantity'], errors='coerce')
        valid_qty = (numeric_qty > 0).sum()
        print(f"\n✅ Товары с корректным числовым количеством: {valid_qty}")
    except:
        pass
    
    issues["valid_quantity"] = valid_qty
    
    return issues

def analyze_categories(df):
    """Анализирует категории"""
    print("\n" + "=" * 80)
    print("🗂️  АНАЛИЗ КАТЕГОРИЙ (Category field)")
    print("=" * 80)
    
    if 'Category' not in df.columns:
        print("⚠️  Столбец Category не найден!")
        return {}
    
    analysis = {
        "total_unique_categories": 0,
        "empty_categories": 0,
        "category_distribution": {}
    }
    
    # Пустые категории
    empty = df['Category'].isna() | (df['Category'] == '')
    print(f"\n🔴 Товары без категории: {empty.sum()}")
    analysis["empty_categories"] = int(empty.sum())
    
    # Уникальные категории
    filled_cats = df[~empty]['Category']
    unique_cats = filled_cats.nunique()
    print(f"\n📊 Уникальных категорий: {unique_cats}")
    analysis["total_unique_categories"] = unique_cats
    
    # Распределение
    cat_distribution = filled_cats.value_counts()
    print(f"\n📈 ТОП 20 категорий:")
    for i, (cat, count) in enumerate(cat_distribution.head(20).items(), 1):
        print(f"   {i:2}. [{count:3} товаров] {str(cat)[:60]}")
    
    analysis["category_distribution"] = cat_distribution.head(30).to_dict()
    
    # Анализ структуры категорий (разделители)
    print(f"\n🔍 Структура категорий:")
    sample_cats = filled_cats.head(20)
    for cat in sample_cats:
        parts = str(cat).split(">")
        level = len(parts)
        print(f"   Уровней: {level} | {cat}")
    
    return analysis

def analyze_tilda_uid(df):
    """Анализирует Tilda UID"""
    print("\n" + "=" * 80)
    print("🆔 АНАЛИЗ TILDA UID")
    print("=" * 80)
    
    if 'Tilda UID' not in df.columns and 'UID' not in df.columns:
        print("⚠️  Столбец Tilda UID / UID не найден!")
        return {}
    
    uid_col = 'Tilda UID' if 'Tilda UID' in df.columns else 'UID'
    
    analysis = {
        "total_uids": 0,
        "empty_uids": 0,
        "duplicate_uids": 0,
        "unique_uids": 0
    }
    
    total = len(df)
    empty = df[uid_col].isna() | (df[uid_col] == '')
    unique = df[uid_col].nunique()
    duplicates = total - unique
    
    print(f"\n📊 Всего записей: {total}")
    print(f"⚪ Пустых UID: {empty.sum()}")
    print(f"✅ Уникальных UID: {unique}")
    print(f"🔴 Дублей UID: {duplicates}")
    
    analysis["total_uids"] = total
    analysis["empty_uids"] = int(empty.sum())
    analysis["unique_uids"] = unique
    analysis["duplicate_uids"] = duplicates
    
    if duplicates > 0:
        print(f"\n   Примеры дублей:")
        dup_uids = df[df[uid_col].duplicated()][uid_col]
        for uid in dup_uids.unique()[:5]:
            count = (df[uid_col] == uid).sum()
            print(f"   - UID {uid}: встречается {count} раз")
    
    return analysis

def analyze_sku(df):
    """Анализирует SKU"""
    print("\n" + "=" * 80)
    print("🏷️  АНАЛИЗ SKU")
    print("=" * 80)
    
    if 'SKU' not in df.columns:
        print("⚠️  Столбец SKU не найден!")
        return {}
    
    analysis = {
        "total_skus": 0,
        "empty_skus": 0,
        "unique_skus": 0,
        "duplicate_skus": 0
    }
    
    total = len(df)
    empty = df['SKU'].isna() | (df['SKU'] == '')
    unique = df['SKU'].nunique()
    duplicates = total - unique
    
    print(f"\n📊 Всего записей: {total}")
    print(f"⚪ Пустых SKU: {empty.sum()}")
    print(f"✅ Уникальных SKU: {unique}")
    print(f"🔴 Дублей SKU: {duplicates}")
    
    analysis["total_skus"] = total
    analysis["empty_skus"] = int(empty.sum())
    analysis["unique_skus"] = unique
    analysis["duplicate_skus"] = duplicates
    
    if duplicates > 0:
        print(f"\n   Примеры дублей SKU:")
        dup_skus = df[df['SKU'].duplicated()]['SKU']
        for sku in dup_skus.unique()[:5]:
            count = (df['SKU'] == sku).sum()
            items = df[df['SKU'] == sku][['SKU', 'Title']].values
            print(f"   - SKU {sku}: встречается {count} раз")
            for item in items[:2]:
                print(f"     → {item[1][:50]}")
    
    return analysis

def analyze_offers(df):
    """Анализирует Offers ID"""
    print("\n" + "=" * 80)
    print("📢 АНАЛИЗ OFFERS ID")
    print("=" * 80)
    
    if 'Offers ID' not in df.columns:
        print("⚠️  Столбец Offers ID не найден!")
        return {}
    
    analysis = {
        "total_offers": 0,
        "empty_offers": 0,
        "unique_offers": 0
    }
    
    total = len(df)
    empty = df['Offers ID'].isna() | (df['Offers ID'] == '')
    unique = df['Offers ID'].nunique()
    
    print(f"\n📊 Всего записей: {total}")
    print(f"⚪ Пустых Offers ID: {empty.sum()}")
    print(f"✅ Уникальных Offers ID: {unique}")
    
    # Примеры
    print(f"\n   Примеры Offers ID:")
    for offer in df['Offers ID'].dropna().unique()[:10]:
        count = (df['Offers ID'] == offer).sum()
        print(f"   - {offer} ({count} товаров)")
    
    analysis["total_offers"] = total
    analysis["empty_offers"] = int(empty.sum())
    analysis["unique_offers"] = unique
    
    return analysis

def create_summary_report(df):
    """Создаёт итоговый отчёт"""
    print("\n" + "=" * 80)
    print("📋 ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 80)
    
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "file": CATALOG_PATH,
        "summary": {
            "total_items": len(df),
            "total_columns": len(df.columns),
            "columns_list": list(df.columns)
        },
        "critical_issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # КРИТИЧЕСКИЕ ПРОБЛЕМЫ
    if 'Price' in df.columns:
        zero_prices = (df['Price'] == 0.0).sum() + (pd.to_numeric(df['Price'], errors='coerce') == 0.0).sum()
        if zero_prices > 0:
            report["critical_issues"].append({
                "issue": "Товары с нулевой ценой",
                "count": zero_prices,
                "severity": "HIGH",
                "action": "Установить цену по запросу или исправить"
            })
    
    if 'Quantity' in df.columns:
        inf_qty = ((df['Quantity'] == '∞') | (df['Quantity'] == 'inf')).sum()
        if inf_qty > 0:
            report["critical_issues"].append({
                "issue": "Товары с бесконечным количеством (∞)",
                "count": inf_qty,
                "severity": "MEDIUM",
                "action": "Заменить на фиксированное значение (например, 10)"
            })
    
    if 'Category' in df.columns:
        empty_cats = (df['Category'].isna() | (df['Category'] == '')).sum()
        if empty_cats > 0:
            report["critical_issues"].append({
                "issue": "Товары без категории",
                "count": empty_cats,
                "severity": "HIGH",
                "action": "Определить категорию по SKU/Title"
            })
    
    # РЕКОМЕНДАЦИИ
    report["recommendations"].append("✅ Price = 0.0 → Логика: 'По запросу' или минимальная цена")
    report["recommendations"].append("✅ Quantity = ∞ → Заменить на фиксированное (10шт по вашему запросу)")
    report["recommendations"].append("✅ Category пустая → Использовать узлы из Title/SKU")
    report["recommendations"].append("✅ Создать справочник node_keywords.json для автоматической категоризации")
    
    print("\n🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
    for issue in report["critical_issues"]:
        print(f"   [{issue['severity']}] {issue['issue']}: {issue['count']} товаров")
        print(f"          → {issue['action']}")
    
    print("\n💡 РЕКОМЕНДАЦИИ:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"   {i}. {rec}")
    
    # Сохранить JSON отчёт
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Отчёт сохранён: {REPORT_PATH}")
    
    return report

def main():
    """Главная функция"""
    print("\n🚀 ДИАГНОСТИКА КАТАЛОГА")
    print("=" * 80)
    
    # Загруузить каталог
    df = load_catalog()
    if df is None:
        return
    
    # Запустить анализы
    structure = analyze_structure(df)
    price_issues = analyze_price_issues(df)
    qty_issues = analyze_quantity_issues(df)
    categories = analyze_categories(df)
    uids = analyze_tilda_uid(df)
    skus = analyze_sku(df)
    offers = analyze_offers(df)
    
    # Итоговый отчёт
    report = create_summary_report(df)
    
    print("\n" + "=" * 80)
    print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
    print("=" * 80)
    print(f"\n📁 Результаты сохранены в: {REPORT_PATH}")
    print("\n🎯 Следующие шаги:")
    print("   1. Прочитать recommendations из отчёта")
    print("   2. Создать node_keywords.json (справочник категорий)")
    print("   3. Создать tilda_structure.json (структура Tilda)")
    print("   4. Создать distribute_offers_by_categories.py (основной скрипт)")
    print("   5. Тестировать на 10-20 товарах")
    print("   6. Запустить на всех товарах")

if __name__ == "__main__":
    main()
