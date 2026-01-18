# Сбор описаний станков

## Описание

Система для автоматического сбора и структурирования описаний станков с сайта rosstanko.com.

## Структура файлов

```
Katalog-RSS/
├── descriptions/              # Markdown файлы для каждого станка
│   ├── README.md             # Документация каталога
│   ├── 1M63.md               # Описание станка 1М63
│   ├── 16K40.md              # Описание станка 16К40
│   └── ...                   # Остальные станки
├── descriptions.json          # JSON формат (для API/программ)
├── descriptions.csv           # CSV формат (для Tilda/Excel)
├── scrape_stanok_descriptions.py    # Скрипт парсинга сайта
└── update_descriptions_from_markdown.py  # Обновление JSON/CSV из MD
```

## Использование

### 1. Автоматический сбор данных с сайта

```bash
python scrape_stanok_descriptions.py
```

Скрипт:
- Ищет страницы станков на rosstanko.com
- Извлекает назначение, характеристики, комплектацию
- Создает Markdown, JSON и CSV файлы

### 2. Ручное редактирование

После автоматического сбора можно отредактировать Markdown файлы вручную:

```bash
# Редактируйте файлы в descriptions/*.md
nano descriptions/1M63.md

# Затем обновите JSON и CSV
python update_descriptions_from_markdown.py
```

## Форматы данных

### Markdown (descriptions/*.md)

```markdown
# SKU - Название станка

## Назначение
Описание назначения станка...

## Основные характеристики
- Характеристика 1
- Характеристика 2
- ...

## Комплектация
- Элемент 1
- Элемент 2
- ...

**Источник:** https://rosstanko.com/...
```

### JSON (descriptions.json)

```json
{
  "stanks": [
    {
      "sku": "1M63",
      "name": "Токарно-винторезный станок 1М63",
      "purpose": "Предназначен для...",
      "characteristics": ["...", "..."],
      "equipment": ["...", "..."],
      "source_url": "https://rosstanko.com/..."
    }
  ]
}
```

### CSV (descriptions.csv)

Колонки: SKU, Name, Purpose, Characteristics, Equipment, SourceURL

Подходит для импорта в:
- Tilda (каталог товаров)
- Excel/Google Sheets
- Базы данных

## Список станков

1. STANOK.RT5001 - Станок лентобандажировочный РТ5001
2. 1M63 - Токарно-винторезный станок 1М63 ✅ *обновлено*
3. 16K40 - Токарный станок 16К40
4. 1N65 - Токарно-винторезный станок 1Н65
5. 1N98 - Токарно-винторезный станок 1Н98
6. 16K30 - Токарный станок 16К30
7. 16M30 - Токарный станок 16М30
8. 1N62 - Токарно-винторезный станок 1Н62
9. 1K62 - Токарный станок 1К62
10. GS526 - Фрезерный станок GS-526
11. UBB112 - Фрезерный станок UBB-112

## Зависимости

```bash
pip install requests beautifulsoup4 pandas
```

## Примеры использования

### Python - чтение JSON

```python
import json

with open('descriptions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for stanok in data['stanks']:
    print(f"{stanok['sku']}: {stanok['name']}")
    print(f"  Характеристик: {len(stanok['characteristics'])}")
```

### Python - чтение CSV

```python
import csv

with open('descriptions.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['SKU']}: {row['Name']}")
```

### Bash - поиск по файлам

```bash
# Найти все упоминания диаметра
grep -r "диаметр" descriptions/

# Показать характеристики конкретного станка
cat descriptions/1M63.md
```

## Обновление данных

1. **Автоматическое обновление всех станков:**
   ```bash
   python scrape_stanok_descriptions.py
   ```

2. **Обновление конкретного станка вручную:**
   ```bash
   # Отредактируйте MD файл
   nano descriptions/1M63.md
   
   # Регенерируйте JSON/CSV
   python update_descriptions_from_markdown.py
   ```

3. **Добавление нового станка:**
   - Добавьте SKU в список STANKI в scrape_stanok_descriptions.py
   - Запустите скрипт или создайте MD файл вручную

## Примечания

- Все данные в UTF-8 кодировке
- CSV использует точку с запятой как разделитель (для Excel)
- Характеристики и комплектация разделяются "; " в CSV
- Markdown файлы являются основным источником данных
- JSON и CSV регенерируются из Markdown

## Источники

- Основной: https://rosstanko.com/
- Техническая документация производителей
- Каталог запчастей Katalog-RSS
