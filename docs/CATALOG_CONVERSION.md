# Конвертация каталога для Tilda

## Проблема

При загрузке каталога с дополнительными колонками (PrefixOffer, PrefixPhoto, PhotoFile) в Tilda происходит некорректное отображение: колонка TEXT попадает в заголовок, и структура выглядит криво.

## Решение

Скрипт `convert_catalog_structure.py` конвертирует каталог в стандартный формат Tilda:

1. **Удаляет лишние колонки** (PrefixOffer, PrefixPhoto, PhotoFile)
2. **Оставляет только 22 стандартные колонки Tilda**
3. **Добавляет кавычки вокруг всех полей** (формат CSV с QUOTE_ALL)

## Использование

```bash
python convert_catalog_structure.py
```

### Результат

- **Входной файл:** `catalogs/TOP-KATALOG-s-prefiksami-i-foto copy 2.csv` (25 колонок)
- **Выходной файл:** `TOP-KATALOG-s-prefiksami-i-foto copy 2-CHPU-TEXT.csv` (22 колонки)

## Стандартные колонки Tilda (22)

1. Tilda UID
2. Brand
3. SKU
4. Mark
5. Category
6. Title
7. Description
8. Text
9. Photo
10. Price
11. Quantity
12. Price Old
13. Editions
14. Modifications
15. External ID
16. Parent UID
17. Weight
18. Length
19. Width
20. Height
21. Url
22. UID

## Пример

**До (с ошибкой):**
```csv
Tilda UID;Brand;SKU;...;Text;...;PrefixOffer;PrefixPhoto;PhotoFile
VALUE1;VALUE2;...;LONG TEXT;...;PREFIX1;PREFIX2;FILE.jpg
```

**После (корректно):**
```csv
"Tilda UID";"Brand";"SKU";...;"Text";...;"UID"
"VALUE1";"VALUE2";...;"LONG TEXT";...;"12345"
```

## Тестовый файл

`TEST_2_OFFERA.csv` - пример файла с 2 офферами в правильном формате для загрузки в Tilda.

## Требования

- Python 3.6+
- pandas

```bash
pip install pandas
```
