
"""

# Твои 4 недостающих ТКП (данные подставь свои)
tkp_data = [
    {
        "filename": "Шпиндельные_гайки_1М63_Directus.md",
        "title": "Шпиндельные гайки для токарных станков 1М63, 1М63Н, ДИП300",
        "article": "1М63.03.XXX",
        "compatible": "Токарные станки 1М63, 1М63Н, ДИП300, 16К40",
        "material": "Сталь 40Х, 45, закалка HRC 55-60",
        "type": "Гайки шпинделя с шпоночным пазом",
        "diameter": "Ø80-120 мм",
        "weight": "2.5-5 кг",
        "rpm": "до 2000 об/мин",
        "construction": "Точная нарезка резьбы М80х6, М100х6 с фиксацией",
        "models": "1М63, 1М63Н, ДИП300",
        "notes": "Проверяйте допуск резьбы и состояние шпинделя перед установкой"
    },
    {
        "filename": "ШВП_1П756ДФ3_Directus.md",
        "title": "Шарико-винтовая пара (ШВП) для токарных станков 1П756ДФ3",
        "article": "1П756ДФ3.57.XXX",
        "compatible": "Токарные станки 1П756ДФ3, 16М30Ф3 с ЧПУ",
        "material": "Сталь 40Х + бронза или пластик",
        "type": "ШВП точности C5, C7",
        "diameter": "Ø16-25 мм, шаг 5-10 мм",
        "weight": "3-8 кг",
        "rpm": "до 3000 об/мин",
        "construction": "Преднатяг, защитный кожух, обратчик шариков",
        "models": "1П756ДФ3, 16М30Ф3",
        "notes": "Комплект: винт + гайка + кожух"
    }
]

output_dir = r"C:\GitHub-Repositories\Katalog-RSS\Directus-RSS\Товары\Directus-офферы сайта"

# Создаём недостающие ТКП
created = []
for data in tkp_data:
    filepath = os.path.join(output_dir, data["filename"])
    content = template.format(**data)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    created.append(data["filename"])
    print(f"✅ Создан: {data['filename']}")

print(f"\n🎯 СОЗДАНО {len(created)} ТКП файлов!")
print(f"📁 В папке: {output_dir}")
print("\n🚀 Теперь готовность = 100%! Залей на GitHub:")
print("git add . && git commit -m 'Добавлены 2 недостающих ТКП' && git push")