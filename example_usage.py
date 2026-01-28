#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ПРИМЕР ИСПОЛЬЗОВАНИЯ ОПТИМИЗАТОРА КАТАЛОГА

Демонстрирует различные способы использования CatalogOptimizer
"""

from optimize_catalog import CatalogOptimizer

def example_full_optimization():
    """Пример полной оптимизации каталога"""
    print("="*80)
    print("ПРИМЕР 1: ПОЛНАЯ ОПТИМИЗАЦИЯ")
    print("="*80)
    
    # Создаём оптимизатор
    optimizer = CatalogOptimizer("catalogs/Rezerv-FINAL-V3-20260128_161708.csv")
    
    # Запускаем полную оптимизацию
    output_file = optimizer.run_full_optimization()
    
    print(f"\n✅ Готово! Результат сохранён в: {output_file}")


def example_selective_optimization():
    """Пример выборочной оптимизации"""
    print("\n" + "="*80)
    print("ПРИМЕР 2: ВЫБОРОЧНАЯ ОПТИМИЗАЦИЯ")
    print("="*80)
    
    # Создаём оптимизатор
    optimizer = CatalogOptimizer("catalogs/Rezerv-FINAL-V3-20260128_161708.csv")
    
    # Запускаем только нужные методы
    print("\n1️⃣ Очистка цен...")
    optimizer.clean_prices()
    
    print("\n2️⃣ Добавление моделей станков...")
    optimizer.add_editions_dropdown()
    
    print("\n3️⃣ Дедупликация...")
    optimizer.deduplicate_products()
    
    print("\n4️⃣ Валидация...")
    is_valid = optimizer.validate_for_tilda()
    
    # Экспортируем результат
    output_file = optimizer.export_optimized("catalogs/SELECTIVE_CATALOG.csv")
    
    print(f"\n✅ Результат сохранён в: {output_file}")
    print(f"Каталог валиден: {'Да' if is_valid else 'Нет'}")


def example_custom_processing():
    """Пример кастомной обработки с доступом к DataFrame"""
    print("\n" + "="*80)
    print("ПРИМЕР 3: КАСТОМНАЯ ОБРАБОТКА")
    print("="*80)
    
    # Создаём оптимизатор
    optimizer = CatalogOptimizer("catalogs/Rezerv-FINAL-V3-20260128_161708.csv")
    
    # Получаем доступ к DataFrame
    df = optimizer.df
    
    print(f"\nВсего товаров: {len(df)}")
    print(f"Колонок: {len(df.columns)}")
    
    # Кастомная фильтрация
    cheap_products = df[df['Price'] < 1000]
    print(f"Товаров дешевле 1000 руб: {len(cheap_products)}")
    
    expensive_products = df[df['Price'] > 10000]
    print(f"Товаров дороже 10000 руб: {len(expensive_products)}")
    
    # Топ-5 самых дорогих товаров
    print("\n📊 Топ-5 самых дорогих товаров:")
    top_5 = df.nlargest(5, 'Price')[['Title', 'Price', 'SKU']]
    for idx, row in top_5.iterrows():
        print(f"   - {row['Title'][:50]}... | {row['Price']} руб.")


def example_statistics():
    """Пример получения статистики"""
    print("\n" + "="*80)
    print("ПРИМЕР 4: СТАТИСТИКА ОПТИМИЗАЦИИ")
    print("="*80)
    
    # Создаём оптимизатор
    optimizer = CatalogOptimizer("catalogs/Rezerv-FINAL-V3-20260128_161708.csv")
    
    # Запускаем оптимизации
    optimizer.clean_prices()
    optimizer.add_editions_dropdown()
    optimizer.deduplicate_products()
    
    # Получаем статистику
    stats = optimizer.stats
    
    print("\n📊 СТАТИСТИКА ОПТИМИЗАЦИИ:")
    print(f"   Исправлено цен: {stats['prices_cleaned']}")
    print(f"   Добавлено Editions: {stats['editions_added']}")
    print(f"   Удалено дубликатов: {stats['duplicates_removed']}")
    print(f"   Ошибок валидации: {len(stats['validation_errors'])}")


if __name__ == "__main__":
    # Раскомментируйте нужный пример
    
    # Пример 1: Полная оптимизация (рекомендуется)
    # example_full_optimization()
    
    # Пример 2: Выборочная оптимизация
    # example_selective_optimization()
    
    # Пример 3: Кастомная обработка
    # example_custom_processing()
    
    # Пример 4: Статистика
    # example_statistics()
    
    print("\n" + "="*80)
    print("💡 ПОДСКАЗКА:")
    print("Раскомментируйте нужный пример в этом файле и запустите снова")
    print("="*80)
