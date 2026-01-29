# 🎯 Оптимизатор Каталога для Tilda

Автоматическая очистка, обработка и улучшение каталога товаров ТД РУССтанкоСбыт для импорта в Tilda.

## 📋 Описание

Скрипт `optimize_catalog.py` — это мощный инструмент для автоматической обработки каталога товаров. Он решает следующие задачи:

### ✅ Основной функционал

1. **Очистка цен** - Автоматическая замена некорректных цен (1.0, 0.0) с пометкой "Цена по запросу"
2. **Генерация описаний** - Создание SEO-оптимизированных описаний для товаров без описания
3. **Улучшение текстов** - Добавление подробных текстов с HTML-форматированием и ссылками
4. **Editions (модели станков)** - Автоматическое извлечение моделей станков для выпадающих списков
5. **Нормализация категорий** - Приведение категорий к единому формату
6. **Дедупликация** - Удаление дубликатов товаров с объединением информации
7. **Линковка** - Добавление ссылок на посадочные страницы станков
8. **Валидация** - Проверка готовности каталога к импорту в Tilda

## 🚀 Быстрый старт

### Требования

- Python 3.7+
- pandas

### Установка зависимостей

```bash
pip install pandas
```

### Запуск оптимизации

```bash
python optimize_catalog.py
```

По умолчанию скрипт обрабатывает файл:
```
catalogs/Rezerv-FINAL-V3-20260128_161708.csv
```

Для обработки другого файла:
```bash
python optimize_catalog.py path/to/your/catalog.csv
```

## 📊 Результаты работы

После запуска скрипт создаёт три файла:

1. **OPTIMIZED_CATALOG_YYYYMMDD_HHMMSS.csv** - Оптимизированный каталог
2. **OPTIMIZED_CATALOG_YYYYMMDD_HHMMSS_report.json** - JSON-отчёт со статистикой
3. **OPTIMIZED_CATALOG_YYYYMMDD_HHMMSS_preview.html** - HTML-превью первых 10 товаров

### Пример отчёта

```json
{
  "timestamp": "2026-01-28T12:06:19.385682",
  "input_file": "catalogs/Rezerv-FINAL-V3-20260128_161708.csv",
  "output_file": "catalogs/OPTIMIZED_CATALOG_20260128_120619.csv",
  "total_products": 474,
  "statistics": {
    "prices_cleaned": 359,
    "descriptions_generated": 0,
    "texts_enhanced": 0,
    "editions_added": 544,
    "categories_normalized": 0,
    "duplicates_removed": 70,
    "links_added": 0,
    "validation_errors": ["Строка 450: Пустой Title"]
  }
}
```

## 🔧 Детали оптимизаций

### 1. Очистка цен (clean_prices)

- Находит товары с `Price <= 1.0` или пустые
- Добавляет пометку " | Цена по запросу" в Description
- Устанавливает Price = 1.0 для товаров по запросу

### 2. Генерация описаний (generate_descriptions)

- Создаёт описания для товаров с пустым Description
- Формат: "[Название]. Запасные части и комплектующие для станков [модели]. Артикул: [SKU]."
- Минимум 100 символов

### 3. Улучшение текстов (enhance_text_field)

- Добавляет SEO-оптимизированные тексты
- HTML-форматирование с `<a>`, `<br>`, `<strong>`
- Блок "Смотрите также" с перелинковкой

### 4. Editions - модели станков (add_editions_dropdown)

Автоматически извлекает модели станков:
- 16К20, 16К30, 16К40, 16М30Ф3, 16А20Ф3
- 1М63, 1М63Н, 1Н65, 1М65, ДИП-300, ДИП-500
- РТ755Ф3, РТ301, РТ305М, РТ779Ф3, и другие

Формат вывода: `"16К20; 1М63; РТ755Ф3"` - создаёт выпадающий список в Tilda

### 5. Нормализация категорий (normalize_categories)

- Убирает лишние пробелы
- Удаляет дублирующиеся разделители (`;`, `>>>`)
- Приводит к единому формату

### 6. Дедупликация (deduplicate_products)

- Находит дубликаты по SKU
- Объединяет информацию:
  - Берёт лучшее (самое длинное) Description
  - Объединяет Text через `<br><br>`
  - Сохраняет фото из любой записи

### 7. Линковка на посадочные страницы (link_to_landing_pages)

Добавляет HTML-ссылки на посадочные страницы станков:
```html
<a href="https://russtankosbyt.tilda.ws/stanokrtrt16k20">16К20</a>
```

### 8. Валидация (validate_for_tilda)

Проверяет:
- ✅ Title не пустой и <= 200 символов
- ✅ Price > 0
- ✅ Category валидная
- ✅ SKU уникальный
- ✅ Кодировка UTF-8 with BOM

## 📝 Использование как библиотеки

```python
from optimize_catalog import CatalogOptimizer

# Создаём оптимизатор
optimizer = CatalogOptimizer("path/to/catalog.csv")

# Запускаем полную оптимизацию
output_file = optimizer.run_full_optimization()

# Или выборочные методы
optimizer.clean_prices()
optimizer.add_editions_dropdown()
optimizer.deduplicate_products()
optimizer.export_optimized("custom_output.csv")
```

## 🎨 Формат входного CSV

Ожидаемые колонки:
```
Tilda UID, Brand, SKU, Offers ID, Mark, Category, Title, Description, 
Text, Photo, Price, Quantity, Price Old, Editions, Modifications, 
External ID, Parent UID, Weight, Length, Width, Height, Url, Tabs:1
```

## 📦 Формат выходного CSV

- Кодировка: **UTF-8 with BOM** (для корректного отображения кириллицы в Tilda)
- Разделитель: **запятая** (`,`)
- Все поля оптимизированы для импорта в Tilda

## 🔍 Примеры извлечённых моделей

Скрипт распознаёт следующие паттерны:
- `16К20`, `16К30`, `16К40` - токарные станки
- `16М30Ф3`, `16А20Ф3` - станки с ЧПУ
- `1М63`, `1М63Н`, `ДИП-300` - тяжёлые токарные станки
- `РТ755Ф3`, `РТ301`, `РТ305М` - станки с револьверной головкой
- И многие другие...

## 📈 Типичные результаты

При обработке каталога из ~544 товаров:
- ✅ Исправлено цен: 359
- ✅ Добавлено Editions: 544
- ✅ Удалено дубликатов: 70
- ✅ Финальный каталог: 474 товара
- ✅ Готовность к импорту: ~99.8% (1 ошибка из 474)

## 🛠️ Расширение функционала

### Добавление новых моделей станков

Отредактируйте `MACHINE_PATTERNS` в классе `CatalogOptimizer`:

```python
MACHINE_PATTERNS = [
    r'\b16К20\b', 
    r'\bВАША_МОДЕЛЬ\b',  # Добавьте свой паттерн
    # ...
]
```

### Добавление новых посадочных страниц

Отредактируйте `LANDING_PAGES`:

```python
LANDING_PAGES = {
    '16К20': 'https://russtankosbyt.tilda.ws/stanokrtrt16k20',
    'ВАША_МОДЕЛЬ': 'https://your-url.com/page',  # Добавьте
    # ...
}
```

## 🐛 Решение проблем

### Ошибка "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install pandas
```

### Файл не найден

Убедитесь, что путь к входному файлу корректный:
```bash
ls -la catalogs/Rezerv-FINAL-V3-20260128_161708.csv
```

### Ошибки кодировки

Скрипт автоматически определяет кодировку. Если возникают проблемы, убедитесь, что входной файл в UTF-8.

## 📞 Поддержка

При возникновении вопросов или проблем:
1. Проверьте логи оптимизации в консоли
2. Изучите JSON-отчёт с ошибками валидации
3. Просмотрите HTML-превью результата

## 📄 Лицензия

Этот скрипт создан для внутреннего использования ТД РУССтанкоСбыт.

---

**Версия:** 1.0.0  
**Дата создания:** 28 января 2026  
**Автор:** GitHub Copilot

---

## Наша продукция и услуги

### Комплектующие для станков
[Шестерни на заказ](https://russtankosbyt.tilda.ws/shesterninazakaz) | [Шестерни для ЧПУ](https://tdrusstankosbyt.ru/shesternidlachpu) | [Резцовый блок](https://russtankosbyt.tilda.ws/rezcovyblok) | [Коробки подач](https://tdrusstankosbyt.ru/korobkipodach) | [ШВП](https://tdrusstankosbyt.ru/shvp) | [Валы](https://tdrusstankosbyt.ru/valy) | [Винты](https://tdrusstankosbyt.ru/vinty) | [Рейки](https://tdrusstankosbyt.ru/rejki)

### Узлы токарных станков
[Шпиндельные бабки](https://tdrusstankosbyt.ru/shpindelnyibabki) | [Задние бабки](https://tdrusstankosbyt.ru/zadniibabki) | [Каретки](https://tdrusstankosbyt.ru/karetki) | [Суппорты](https://tdrusstankosbyt.ru/support) | [Ползушки](https://tdrusstankosbyt.ru/polzushki)

### Механизмы и передачи
[Муфты обгонные](https://tdrusstankosbyt.ru/muftaobgonnaya) | [Фрикционные муфты](https://tdrusstankosbyt.ru/frikcionniyemufty) | [Фрикцион в сборе](https://tdrusstankosbyt.ru/frikcionvsbore) | [Диски](https://tdrusstankosbyt.ru/diski) | [Гайки маточные](https://tdrusstankosbyt.ru/gajkimatochniye) | [Гайки](https://tdrusstankosbyt.ru/gajki) | [Колеса конические](https://tdrusstankosbyt.ru/kolesakonicheskiye) | [Колеса зубчатые](https://tdrusstankosbyt.ru/kolesazubchatiye) | [Червячные пары](https://tdrusstankosbyt.ru/cherwiachniyepary)

### Оснастка и инструмент
[Патроны](https://tdrusstankosbyt.ru/patroni) | [Кулачки](https://tdrusstankosbyt.ru/kulachki) | [Венцы](https://tdrusstankosbyt.ru/venci) | [Сухари](https://tdrusstankosbyt.ru/suchari) | [Захваты и вкладыши](https://tdrusstankosbyt.ru/zachvativkladishi) | [Комплектующие к узлам](https://tdrusstankosbyt.ru/komplektujushiekuzlam)

### Специальное оборудование для железнодорожной отрасли
[Ролики упрочняющие РТ301.01 Ф110](https://tdrusstankosbyt.ru/rolikiuprrt30101f110) | [Ролики сглаживающие РТ301.01 Ф180](https://tdrusstankosbyt.ru/rolikisgalgrt301f180) | [Защитные кожухи для ШВП](https://tdrusstankosbyt.ru/shvp-kozuhi) | [Шпиндель задней бабки 1М65](https://tdrusstankosbyt.ru/shpindel1m65)

### Револьверные головки и запчасти
[Револьверные головки ЧПУ](https://russtankosbyt.tilda.ws/revolvernyagolovkachpu) | [Револьверная головка купить](https://russtankosbyt.tilda.ws/revolvernyagolovkachpu) | [Револьверная головка 16К30Ф3](https://tdrusstankosbyt.ru/remontrevolvernyhgolovok16k30f340000) | [Ремонт револьверных головок](https://tdrusstankosbyt.ru/remontrevolvernyhgolovok) | [Запчасти для револьверных головок](https://russtankosbyt.tilda.ws/remontrevolvernyhgolovokzapchasti) | [Резцовый блок 16К30Ф302.42.000](https://tdrusstankosbyt.ru/rezcovyblok)

### Станки с ЧПУ
[16М30Ф3](https://tdrusstankosbyt.ru/stanokchpu16303) | [16А20Ф3](https://tdrusstankosbyt.ru/stanokchpu1620f3) | [РТ755Ф3](https://tdrusstankosbyt.ru/stanokchpu7553) | [РТ305М](https://tdrusstankosbyt.ru/stanokchpu305) | [РТ779Ф3](https://tdrusstankosbyt.ru/stanokchpu7793)

### Станки токарно-винторезные
[16К20](https://russtankosbyt.tilda.ws/stanokrtrt16k20) | [16К40](https://russtankosbyt.tilda.ws/stanokrtrt16k40) | [16Р25](https://russtankosbyt.tilda.ws/stanokrtrt16p25) | [1М63Н (ДИП-300)](https://tdrusstankosbyt.ru/stanokrtrt1m63ndip300) | [1Н65 (ДИП-500)](https://tdrusstankosbyt.ru/stanokrtrt1n65ndip500) | [РТ117](https://tdrusstankosbyt.ru/stanokrt117) | [РТ817](https://tdrusstankosbyt.ru/stanokrtrt817)

### Станки для железнодорожной отрасли
[РТ5001](https://russtankosbyt.tilda.ws/stanokrt5001) | [РТ5003](https://russtankosbyt.tilda.ws/stanokrt5003) | [РТ5004](https://russtankosbyt.tilda.ws/stanokrt5004) | [РТ301](https://russtankosbyt.tilda.ws/stanokrtrt301) | [РТ301.01](https://russtankosbyt.tilda.ws/stanokrtrt301) | [РТ301.02](https://russtankosbyt.tilda.ws/stanokrtrt30102) | [РТ917](https://russtankosbyt.tilda.ws/stanokrtrt917)

### Станки трубонарезные
[1А983](https://tdrusstankosbyt.ru/stanok1a983) | [1Н983](https://tdrusstankosbyt.ru/stanok1h983) | [РТ783](https://tdrusstankosbyt.ru/stanokrt783)

---

**Связаться с нами:**
📞 [+7 499 390-85-04](tel:+74993908504) | 💬 [Telegram](https://t.me/tdrusstankosbyt?direct) | 📧 [zakaz@tdrusstankosbyt.ru](mailto:zakaz@tdrusstankosbyt.ru)
