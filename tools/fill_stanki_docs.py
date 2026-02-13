import os
from pathlib import Path

# База характеристик для 22 моделей
STANKI_DB = {
    "16k20": {"title": "16К20", "diameter": "400 мм", "power": "11 кВт", "rmc": "710-2000 мм"},
    "1m63n": {"title": "1М63Н (ДИП-300)", "diameter": "630 мм", "power": "15 кВт", "rmc": "750-5000 мм"},
    "1n65": {"title": "1Н65 (ДИП-500)", "diameter": "1000 мм", "power": "22-30 кВт", "rmc": "1000-12000 мм"},
    "16k40": {"title": "16К40", "diameter": "800 мм", "power": "18.5 кВт", "rmc": "750-10000 мм"},
    "16p25": {"title": "16Р25", "diameter": "500 мм", "power": "11 кВт", "rmc": "750-2000 мм"},
    "rt117": {"title": "РТ117", "diameter": "1100 мм", "power": "30 кВт", "rmc": "1000-12000 мм"},
    "rt817": {"title": "РТ817", "diameter": "1300 мм", "power": "30 кВт", "rmc": "1000-12000 мм"},
    "16m30f3": {"title": "16М30Ф3 (ЧПУ)", "diameter": "630 мм", "power": "37 кВт", "rmc": "1500-8000 мм"},
    "rt755f3": {"title": "РТ755Ф3 (ЧПУ)", "diameter": "800 мм", "power": "37 кВт", "rmc": "1500-10000 мм"},
    "16a20f3": {"title": "16А20Ф3 (ЧПУ)", "diameter": "400 мм", "power": "11 кВт", "rmc": "1000 мм"},
    "1a983": {"title": "1А983 (Трубонарезной)", "diameter": "800 мм (отверстие 300 мм)", "power": "15 кВт", "rmc": "750-1000 мм"},
    "rt5001": {"title": "РТ5001 (Колесотокарный)", "diameter": "1100 мм (колеса)", "power": "30 кВт", "rmc": "спец"},
    "rt301": {"title": "РТ301 (Токарно-накатной)", "diameter": "630 мм", "power": "15 кВт", "rmc": "спец"},
}

def fill():
    root = Path(__file__).resolve().parents[1]
    stanki_dir = root / "docs" / "Станки"
    stanki_dir.mkdir(parents=True, exist_ok=True)
    
    for model, data in STANKI_DB.items():
        file_path = stanki_dir / f"{model}.md"
        content = f"""# Станок {data['title']}

## Описание
ТКП и техническая документация для модели {data['title']}. Подробное описание в процессе подготовки.

## Технические характеристики
"""
        file_path.write_text(content, encoding="utf-8")
        print(f"Файл создан: {model}.md")

if __name__ == "__main__":
    fill()
