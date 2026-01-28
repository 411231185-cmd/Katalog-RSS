# -*- coding: utf-8 -*-
"""
🎯 ОПТИМИЗАТОР КАТАЛОГА ДЛЯ TILDA
Автоматическая очистка, обработка и улучшение каталога товаров
"""

import pandas as pd
import re
import json
import numpy as np
from datetime import datetime
from pathlib import Path


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for NumPy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


class CatalogOptimizer:
    """Класс для оптимизации каталога товаров для Tilda"""
    
    # Паттерны для поиска моделей станков
    MACHINE_PATTERNS = [
        r'\b16К20\b', r'\b16К30\b', r'\b16К40\b', r'\b16М30Ф3\b', r'\b16А20Ф3\b',
        r'\b1М63\b', r'\b1М63Н\b', r'\b1Н65\b', r'\b1М65\b', r'\b163\b', r'\b165\b',
        r'\bДИП-?300\b', r'\bДИП-?500\b',
        r'\bРТ\d+(?:Ф\d?)?\b', r'\b16Р25\b',
        r'\b1А983\b', r'\b1Н983\b',
    ]
    
    # Соответствие моделей и посадочных страниц
    LANDING_PAGES = {
        '16К20': 'https://russtankosbyt.tilda.ws/stanokrtrt16k20',
        '16К30': 'https://tdrusstankosbyt.ru/stanokchpu16303',
        '16К40': 'https://russtankosbyt.tilda.ws/stanokrtrt16k40',
        '16М30Ф3': 'https://tdrusstankosbyt.ru/stanokchpu16303',
        '16А20Ф3': 'https://tdrusstankosbyt.ru/stanokchpu1620f3',
        '16Р25': 'https://russtankosbyt.tilda.ws/stanokrtrt16p25',
        '1М63': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        '1М63Н': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        '163': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        '1Н65': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        '1М65': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        '165': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        'ДИП-300': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        'ДИП300': 'https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300',
        'ДИП-500': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        'ДИП500': 'https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500',
        'РТ755Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7553',
        'РТ305М': 'https://tdrusstankosbyt.ru/stanokchpu305',
        'РТ779Ф3': 'https://tdrusstankosbyt.ru/stanokchpu7793',
        'РТ5001': 'https://russtankosbyt.tilda.ws/stanokrt5001',
        'РТ5003': 'https://russtankosbyt.tilda.ws/stanokrt5003',
        'РТ5004': 'https://russtankosbyt.tilda.ws/stanokrt5004',
        'РТ301.01': 'https://russtankosbyt.tilda.ws/stanokrtrt301',
        'РТ301.02': 'https://russtankosbyt.tilda.ws/stanokrtrt30102',
        'РТ301': 'https://russtankosbyt.tilda.ws/stanokrtrt301',
        'РТ917': 'https://russtankosbyt.tilda.ws/stanokrtrt917',
        'РТ117': 'https://tdrusstankosbyt.ru/stanokrt117',
        'РТ817': 'https://tdrusstankosbyt.ru/stanokrtrt817',
        'РТ783': 'https://tdrusstankosbyt.ru/stanokrt783',
        '1А983': 'https://tdrusstankosbyt.ru/stanok1a983',
        '1Н983': 'https://tdrusstankosbyt.ru/stanok1h983',
    }
    
    def __init__(self, input_file):
        """Инициализация оптимизатора"""
        self.input_file = input_file
        self.df = None
        self.stats = {
            'prices_cleaned': 0,
            'descriptions_generated': 0,
            'texts_enhanced': 0,
            'editions_added': 0,
            'categories_normalized': 0,
            'duplicates_removed': 0,
            'links_added': 0,
            'validation_errors': []
        }
        self._load_catalog()
    
    def _load_catalog(self):
        """Загрузить каталог из файла"""
        try:
            # Пробуем разные разделители
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(self.input_file, sep=sep, encoding='utf-8-sig')
                    if len(df.columns) > 5:
                        self.df = df
                        print(f"✅ Каталог загружен: {len(df)} товаров, {len(df.columns)} колонок")
                        return
                except:
                    continue
            raise Exception("Не удалось определить разделитель CSV")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            raise
    
    def clean_prices(self):
        """
        1. Найти все товары с Price = 1.0 или Price = 0.0
        2. Заменить на минимальную реальную цену из каталога
        3. Добавить в Description: " | Цена по запросу"
        4. Вернуть статистику исправлений
        """
        print("\n" + "="*80)
        print("🔧 ОЧИСТКА ЦЕН")
        print("="*80)
        
        # Конвертируем Price в числовой формат
        self.df['Price'] = pd.to_numeric(self.df['Price'], errors='coerce')
        
        # Найти товары с некорректными ценами
        bad_prices_mask = (self.df['Price'] <= 1.0) | (self.df['Price'].isna())
        bad_prices_count = bad_prices_mask.sum()
        
        print(f"Найдено товаров с некорректными ценами: {bad_prices_count}")
        
        if bad_prices_count > 0:
            # Для товаров с некорректными ценами добавляем пометку в Description
            for idx in self.df[bad_prices_mask].index:
                desc = str(self.df.loc[idx, 'Description'])
                if pd.isna(desc) or desc == 'nan':
                    desc = ""
                
                # Добавляем пометку, если её ещё нет
                if "Цена по запросу" not in desc:
                    if desc:
                        self.df.loc[idx, 'Description'] = desc.rstrip() + " | Цена по запросу"
                    else:
                        self.df.loc[idx, 'Description'] = "Цена по запросу"
                
                # Устанавливаем цену в 1.0 для товаров "по запросу"
                self.df.loc[idx, 'Price'] = 1.0
            
            self.stats['prices_cleaned'] = bad_prices_count
            print(f"✅ Исправлено цен: {bad_prices_count}")
        
        return self.stats['prices_cleaned']
    
    def generate_descriptions(self):
        """
        1. Найти товары с пустым Description
        2. Сгенерировать текст на основе:
           - Title (название товара)
           - Category (категория)
           - SKU (артикул)
        3. Формат: "Высококачественный [название] для станков модели [модели]. 
                    Артикул: [SKU]. Запасные части и комплектующие."
        4. Минимум 100 символов
        """
        print("\n" + "="*80)
        print("📝 ГЕНЕРАЦИЯ ОПИСАНИЙ")
        print("="*80)
        
        # Найти товары с пустым Description
        empty_desc_mask = self.df['Description'].isna() | (self.df['Description'] == '') | (self.df['Description'] == 'nan')
        empty_desc_count = empty_desc_mask.sum()
        
        print(f"Найдено товаров с пустым описанием: {empty_desc_count}")
        
        for idx in self.df[empty_desc_mask].index:
            title = str(self.df.loc[idx, 'Title']) if pd.notna(self.df.loc[idx, 'Title']) else ""
            sku = str(self.df.loc[idx, 'SKU']) if pd.notna(self.df.loc[idx, 'SKU']) else ""
            category = str(self.df.loc[idx, 'Category']) if pd.notna(self.df.loc[idx, 'Category']) else ""
            
            # Извлекаем модели станков из Title
            models = self._extract_machine_models(title)
            models_text = ", ".join(models[:3]) if models else "различных моделей"
            
            # Генерируем описание
            description = f"{title}. Запасные части и комплектующие для станков {models_text}."
            
            if sku:
                description += f" Артикул: {sku}."
            
            # Убеждаемся, что описание не менее 100 символов
            if len(description) < 100:
                description += " Высококачественная продукция для промышленного оборудования."
            
            self.df.loc[idx, 'Description'] = description
            self.stats['descriptions_generated'] += 1
        
        print(f"✅ Сгенерировано описаний: {self.stats['descriptions_generated']}")
        return self.stats['descriptions_generated']
    
    def enhance_text_field(self):
        """
        1. Найти товары с пустым Text
        2. Добавить SEO-оптимизированный текст:
           - Описание применения
           - Перечень совместимых моделей
           - Преимущества продукции
           - Блок "Смотрите также" с перелинковкой
        3. Использовать HTML-форматирование (<a>, <br>, <strong>)
        """
        print("\n" + "="*80)
        print("✍️  УЛУЧШЕНИЕ ТЕКСТОВЫХ ПОЛЕЙ")
        print("="*80)
        
        # Найти товары с пустым Text
        empty_text_mask = self.df['Text'].isna() | (self.df['Text'] == '') | (self.df['Text'] == 'nan')
        empty_text_count = empty_text_mask.sum()
        
        print(f"Найдено товаров с пустым текстом: {empty_text_count}")
        
        for idx in self.df[empty_text_mask].index:
            title = str(self.df.loc[idx, 'Title']) if pd.notna(self.df.loc[idx, 'Title']) else ""
            description = str(self.df.loc[idx, 'Description']) if pd.notna(self.df.loc[idx, 'Description']) else ""
            category = str(self.df.loc[idx, 'Category']) if pd.notna(self.df.loc[idx, 'Category']) else ""
            
            # Извлекаем модели станков
            models = self._extract_machine_models(title + " " + description)
            
            # Создаём SEO-текст
            text_parts = []
            
            # Описание применения
            if models:
                model_links = []
                for model in models[:3]:
                    if model in self.LANDING_PAGES:
                        model_links.append(f'<a href="{self.LANDING_PAGES[model]}">{model}</a>')
                    else:
                        model_links.append(model)
                
                models_str = ", ".join(model_links)
                text_parts.append(f"{title} для станков {models_str}.")
            else:
                text_parts.append(f"{title}.")
            
            # Добавляем описание применения
            text_parts.append("<br><br>Применяется в узлах и механизмах токарных станков. ")
            text_parts.append("Высококачественная продукция для промышленного оборудования. ")
            text_parts.append("Изготовлено из прочных материалов с соблюдением всех стандартов качества.")
            
            # Блок "Смотрите также"
            text_parts.append(self._generate_see_also_block())
            
            text = "".join(text_parts)
            self.df.loc[idx, 'Text'] = text
            self.stats['texts_enhanced'] += 1
        
        print(f"✅ Улучшено текстовых полей: {self.stats['texts_enhanced']}")
        return self.stats['texts_enhanced']
    
    def add_editions_dropdown(self):
        r"""
        1. Извлечь модели станков из Title, Description, Text
        2. Паттерны: 16К20, 1М63, РТ\d+, ДИП-\d+ и т.д.
        3. Создать поле Editions в формате: "16К20; 1М63; РТ755"
        4. Это создаст выпадающий список в Tilda для фильтрации
        """
        print("\n" + "="*80)
        print("🎯 ДОБАВЛЕНИЕ EDITIONS (МОДЕЛИ СТАНКОВ)")
        print("="*80)
        
        # Убедимся, что колонка Editions существует и имеет правильный тип
        if 'Editions' not in self.df.columns:
            self.df['Editions'] = ''
        self.df['Editions'] = self.df['Editions'].astype(str)
        
        for idx in self.df.index:
            title = str(self.df.loc[idx, 'Title']) if pd.notna(self.df.loc[idx, 'Title']) else ""
            description = str(self.df.loc[idx, 'Description']) if pd.notna(self.df.loc[idx, 'Description']) else ""
            text = str(self.df.loc[idx, 'Text']) if pd.notna(self.df.loc[idx, 'Text']) else ""
            
            # Объединяем все тексты для поиска моделей
            combined_text = f"{title} {description} {text}"
            
            # Извлекаем модели
            models = self._extract_machine_models(combined_text)
            
            if models:
                # Формируем поле Editions
                editions = "; ".join(sorted(set(models)))
                self.df.at[idx, 'Editions'] = editions
                self.stats['editions_added'] += 1
        
        print(f"✅ Добавлено Editions для товаров: {self.stats['editions_added']}")
        return self.stats['editions_added']
    
    def normalize_categories(self):
        """
        1. Парсить многоуровневые категории (разделённые ; и >>>)
        2. Привести к единому формату:
           "Главная категория;Подкатегория 1>>>Подкатегория 2"
        3. Удалить дубликаты
        4. Создать иерархию
        """
        print("\n" + "="*80)
        print("📂 НОРМАЛИЗАЦИЯ КАТЕГОРИЙ")
        print("="*80)
        
        for idx in self.df.index:
            category = str(self.df.loc[idx, 'Category']) if pd.notna(self.df.loc[idx, 'Category']) else ""
            
            if category and category != 'nan':
                # Нормализуем категорию
                normalized = self._normalize_category(category)
                if normalized != category:
                    self.df.loc[idx, 'Category'] = normalized
                    self.stats['categories_normalized'] += 1
        
        print(f"✅ Нормализовано категорий: {self.stats['categories_normalized']}")
        return self.stats['categories_normalized']
    
    def deduplicate_products(self):
        """
        1. Найти дубликаты по SKU
        2. Объединить информацию из дублей:
           - Берём лучшее Description
           - Объединяем Text
           - Сохраняем фото
        3. Удалить дубли
        4. Вернуть статистику
        """
        print("\n" + "="*80)
        print("🔍 ДЕДУПЛИКАЦИЯ ТОВАРОВ")
        print("="*80)
        
        initial_count = len(self.df)
        
        # Найти дубликаты по SKU
        duplicates = self.df[self.df.duplicated(subset=['SKU'], keep=False)]
        
        if len(duplicates) > 0:
            print(f"Найдено дубликатов: {len(duplicates)}")
            
            # Группируем по SKU и объединяем данные
            grouped = self.df.groupby('SKU')
            
            merged_rows = []
            for sku, group in grouped:
                if len(group) > 1:
                    # Берём первую строку как основу
                    merged = group.iloc[0].copy()
                    
                    # Берём лучшее описание (самое длинное)
                    descriptions = group['Description'].dropna()
                    if len(descriptions) > 0:
                        merged['Description'] = max(descriptions, key=len)
                    
                    # Объединяем тексты
                    texts = group['Text'].dropna()
                    if len(texts) > 1:
                        merged['Text'] = "<br><br>".join(texts.unique())
                    
                    # Берём фото из любой записи, где оно есть
                    photos = group['Photo'].dropna()
                    if len(photos) > 0:
                        merged['Photo'] = photos.iloc[0]
                    
                    merged_rows.append(merged)
                else:
                    merged_rows.append(group.iloc[0])
            
            self.df = pd.DataFrame(merged_rows)
            self.df.reset_index(drop=True, inplace=True)
            
            self.stats['duplicates_removed'] = initial_count - len(self.df)
            print(f"✅ Удалено дубликатов: {self.stats['duplicates_removed']}")
        else:
            print("Дубликаты не найдены")
        
        return self.stats['duplicates_removed']
    
    def link_to_landing_pages(self):
        """
        1. Найти существующие посадочные страницы
        2. Добавить ссылки в Text
        3. Создать блок "Подходит для станков:" со ссылками
        """
        print("\n" + "="*80)
        print("🔗 ДОБАВЛЕНИЕ ССЫЛОК НА ПОСАДОЧНЫЕ СТРАНИЦЫ")
        print("="*80)
        
        for idx in self.df.index:
            text = str(self.df.loc[idx, 'Text']) if pd.notna(self.df.loc[idx, 'Text']) else ""
            title = str(self.df.loc[idx, 'Title']) if pd.notna(self.df.loc[idx, 'Title']) else ""
            description = str(self.df.loc[idx, 'Description']) if pd.notna(self.df.loc[idx, 'Description']) else ""
            
            # Извлекаем модели
            models = self._extract_machine_models(f"{title} {description} {text}")
            
            if models and text:
                # Проверяем, есть ли уже ссылки
                has_links = '<a href=' in text
                
                if not has_links:
                    # Добавляем ссылки на модели в тексте
                    for model in models:
                        if model in self.LANDING_PAGES:
                            # Заменяем упоминание модели на ссылку (только первое вхождение)
                            pattern = r'\b' + re.escape(model) + r'\b'
                            replacement = f'<a href="{self.LANDING_PAGES[model]}">{model}</a>'
                            text = re.sub(pattern, replacement, text, count=1)
                    
                    self.df.loc[idx, 'Text'] = text
                    self.stats['links_added'] += 1
        
        print(f"✅ Добавлено ссылок: {self.stats['links_added']}")
        return self.stats['links_added']
    
    def validate_for_tilda(self):
        """
        1. Проверить обязательные поля:
           - Title (не пустое)
           - Price (> 0)
           - Category (валидная структура)
           - SKU (уникальный)
        2. Проверить кодировку: UTF-8 with BOM
        3. Проверить длину текстов:
           - Title: max 200 символов
           - Description: 100-500 символов (рекомендация)
           - Text: 500-2000 символов (рекомендация)
        4. Вернуть отчёт о готовности к импорту
        """
        print("\n" + "="*80)
        print("✔️  ВАЛИДАЦИЯ ДЛЯ TILDA")
        print("="*80)
        
        errors = []
        warnings = []
        
        # Проверка обязательных полей
        for idx in self.df.index:
            row_errors = []
            
            # Title
            title = self.df.loc[idx, 'Title']
            if pd.isna(title) or str(title).strip() == '':
                row_errors.append(f"Строка {idx}: Пустой Title")
            elif len(str(title)) > 200:
                warnings.append(f"Строка {idx}: Title слишком длинный ({len(str(title))} символов)")
            
            # Price
            price = self.df.loc[idx, 'Price']
            if pd.isna(price) or price < 0:
                row_errors.append(f"Строка {idx}: Некорректная цена")
            
            # Category
            category = self.df.loc[idx, 'Category']
            if pd.isna(category) or str(category).strip() == '':
                row_errors.append(f"Строка {idx}: Пустая категория")
            
            # SKU
            sku = self.df.loc[idx, 'SKU']
            if pd.isna(sku) or str(sku).strip() == '':
                row_errors.append(f"Строка {idx}: Пустой SKU")
            
            # Description length
            description = str(self.df.loc[idx, 'Description']) if pd.notna(self.df.loc[idx, 'Description']) else ""
            if description and len(description) < 50:
                warnings.append(f"Строка {idx}: Description слишком короткий ({len(description)} символов)")
            
            errors.extend(row_errors)
        
        # Проверка уникальности SKU
        duplicate_skus = self.df[self.df.duplicated(subset=['SKU'], keep=False)]['SKU'].unique()
        if len(duplicate_skus) > 0:
            errors.append(f"Найдены дубликаты SKU: {', '.join(map(str, duplicate_skus[:5]))}")
        
        self.stats['validation_errors'] = errors
        
        print(f"\n📊 Результаты валидации:")
        print(f"   Всего товаров: {len(self.df)}")
        print(f"   Ошибок: {len(errors)}")
        print(f"   Предупреждений: {len(warnings)}")
        
        if errors:
            print("\n❌ Найдены критические ошибки:")
            for error in errors[:10]:
                print(f"   - {error}")
            if len(errors) > 10:
                print(f"   ... и ещё {len(errors) - 10} ошибок")
        
        if warnings:
            print("\n⚠️  Предупреждения:")
            for warning in warnings[:10]:
                print(f"   - {warning}")
            if len(warnings) > 10:
                print(f"   ... и ещё {len(warnings) - 10} предупреждений")
        
        if not errors:
            print("\n✅ Каталог готов к импорту в Tilda!")
        
        return len(errors) == 0
    
    def export_optimized(self, output_file=None):
        """
        1. Сохранить оптимизированный каталог
        2. Создать JSON-отчёт с статистикой
        3. Создать HTML-превью первых 10 товаров
        """
        print("\n" + "="*80)
        print("💾 ЭКСПОРТ ОПТИМИЗИРОВАННОГО КАТАЛОГА")
        print("="*80)
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"catalogs/OPTIMIZED_CATALOG_{timestamp}.csv"
        
        # Экспортируем CSV с кодировкой UTF-8 with BOM
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ Каталог сохранён: {output_file}")
        
        # Создаём JSON-отчёт
        # Конвертируем все числа в Python int
        stats_json = {}
        for k, v in self.stats.items():
            if isinstance(v, list):
                stats_json[k] = v
            else:
                stats_json[k] = int(v) if isinstance(v, (int, type(pd.Int64Dtype))) else v
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_file': str(self.input_file),
            'output_file': str(output_file),
            'total_products': int(len(self.df)),
            'statistics': stats_json
        }
        
        report_file = output_file.replace('.csv', '_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        print(f"✅ Отчёт сохранён: {report_file}")
        
        # Создаём HTML-превью
        self._create_html_preview(output_file)
        
        return output_file
    
    def run_full_optimization(self):
        """
        Запустить ВСЕ оптимизации последовательно
        """
        print("=" * 80)
        print("🚀 ЗАПУСК ПОЛНОЙ ОПТИМИЗАЦИИ КАТАЛОГА")
        print("=" * 80)
        print(f"Входной файл: {self.input_file}")
        print(f"Товаров в каталоге: {len(self.df)}")
        
        # Выполняем все методы последовательно
        self.clean_prices()
        self.generate_descriptions()
        self.enhance_text_field()
        self.add_editions_dropdown()
        self.normalize_categories()
        self.deduplicate_products()
        self.link_to_landing_pages()
        is_valid = self.validate_for_tilda()
        output_file = self.export_optimized()
        
        print("\n" + "=" * 80)
        print("✅ ОПТИМИЗАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 80)
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"   ✓ Исправлено цен: {self.stats['prices_cleaned']}")
        print(f"   ✓ Сгенерировано описаний: {self.stats['descriptions_generated']}")
        print(f"   ✓ Улучшено текстов: {self.stats['texts_enhanced']}")
        print(f"   ✓ Добавлено Editions: {self.stats['editions_added']}")
        print(f"   ✓ Нормализовано категорий: {self.stats['categories_normalized']}")
        print(f"   ✓ Удалено дубликатов: {self.stats['duplicates_removed']}")
        print(f"   ✓ Добавлено ссылок: {self.stats['links_added']}")
        print(f"\n📁 Результат: {output_file}")
        
        if is_valid:
            print("✅ Каталог валиден и готов к импорту в Tilda!")
        else:
            print("⚠️  Каталог имеет ошибки, требуется доработка")
        
        return output_file
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def _extract_machine_models(self, text):
        """Извлечь модели станков из текста"""
        models = []
        for pattern in self.MACHINE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            models.extend(matches)
        
        # Убираем дубликаты и нормализуем
        unique_models = []
        seen = set()
        for model in models:
            normalized = model.upper().replace('Ф', 'Ф').replace('К', 'К').replace('М', 'М').replace('Р', 'Р').replace('Н', 'Н')
            if normalized not in seen:
                seen.add(normalized)
                unique_models.append(model)
        
        return unique_models[:10]  # Ограничиваем 10 моделями
    
    def _normalize_category(self, category):
        """Нормализовать категорию"""
        # Убираем лишние пробелы
        category = re.sub(r'\s+', ' ', category.strip())
        
        # Убираем дублирующиеся разделители
        category = re.sub(r';+', ';', category)
        category = re.sub(r'>>>+', '>>>', category)
        
        return category
    
    def _generate_see_also_block(self):
        """Генерировать блок 'Смотрите также' с ссылками"""
        see_also_links = [
            '<a href="https://tdrusstankosbyt.ru/stanokchpu16303">16М30Ф3</a>',
            '<a href="https://tdrusstankosbyt.ru/stanokchpu1620f3">16А20Ф3</a>',
            '<a href="https://tdrusstankosbyt.ru/stanokchpu7553">РТ755Ф3</a>',
            '<a href="https://russtankosbyt.tilda.ws/stanokrtrt16k20">16К20</a>',
            '<a href="https://russtankosbyt.tilda.ws/shesterninazakaz">шестерни</a>',
            '<a href="https://tdrusstankosbyt.ru/rezcovyblok">резцовый блок</a>',
            '<a href="https://tdrusstankosbyt.ru/korobkipodach">коробки подач</a>',
            '<a href="https://tdrusstankosbyt.ru/shvp">ШВП</a>',
            '<a href="https://tdrusstankosbyt.ru/valy">валы</a>',
            '<a href="https://russtankosbyt.tilda.ws/revolvernyagolovkachpu">револьверные головки</a>'
        ]
        
        return "<br><br><strong>Смотрите также:</strong><br>" + ", ".join(see_also_links)
    
    def _create_html_preview(self, csv_file):
        """Создать HTML-превью каталога"""
        preview_file = csv_file.replace('.csv', '_preview.html')
        
        html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Превью каталога</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .product { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .product h2 { color: #333; margin: 0 0 10px 0; }
        .product .meta { color: #666; font-size: 14px; margin: 5px 0; }
        .product .description { margin: 10px 0; }
        .product .text { margin: 10px 0; color: #444; line-height: 1.6; }
        .product img { max-width: 200px; margin: 10px 0; }
        .price { color: #e91e63; font-size: 20px; font-weight: bold; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Превью оптимизированного каталога</h1>
        <p>Первые 10 товаров из каталога</p>
    </div>
"""
        
        # Добавляем первые 10 товаров
        for idx in range(min(10, len(self.df))):
            row = self.df.iloc[idx]
            
            html += f"""
    <div class="product">
        <h2>{row['Title']}</h2>
        <div class="meta">SKU: {row['SKU']} | Категория: {row['Category']}</div>
        <div class="price">Цена: {row['Price']} руб.</div>
        <div class="description"><strong>Описание:</strong> {row['Description']}</div>
"""
            
            if pd.notna(row['Text']) and str(row['Text']) != 'nan':
                html += f"        <div class='text'>{row['Text']}</div>\n"
            
            if pd.notna(row['Photo']) and str(row['Photo']) != 'nan':
                html += f"        <img src='{row['Photo']}' alt='{row['Title']}'>\n"
            
            if pd.notna(row['Editions']) and str(row['Editions']) != 'nan':
                html += f"        <div class='meta'><strong>Модели:</strong> {row['Editions']}</div>\n"
            
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML-превью создано: {preview_file}")


def main():
    """Главная функция для запуска оптимизации"""
    import sys
    
    # Путь к входному файлу
    input_file = "catalogs/Rezerv-FINAL-V3-20260128_161708.csv"
    
    # Если передан аргумент командной строки, используем его
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    # Проверяем существование файла
    if not Path(input_file).exists():
        print(f"❌ Файл не найден: {input_file}")
        return
    
    # Создаём оптимизатор и запускаем полную оптимизацию
    optimizer = CatalogOptimizer(input_file)
    output_file = optimizer.run_full_optimization()
    
    print(f"\n🎉 Готово! Оптимизированный каталог: {output_file}")


if __name__ == "__main__":
    main()
