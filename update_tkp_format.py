# -*- coding: utf-8 -*-
"""
Обновление ТКП в новом формате для Tilda
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TKP_DIR = BASE_DIR / "docs" / "tkp_machines"
MACHINES_JSON = BASE_DIR / "tkp_machines.json"

def create_new_format_tkp(machine):
    """Создание ТКП в новом формате"""
    content = f"""# {machine['name']}

## ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ

### Назначение и возможности

{machine['purpose']}

"""
    
    # Add applications
    if machine.get('applications'):
        apps_text = ' '.join(machine['applications'][:3])
        content += f"{apps_text}\n\n"
    
    content += "## ОСНОВНЫЕ ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ\n\n"
    
    # Group characteristics
    char_dict = machine.get('characteristics', {})
    
    size_params = {}
    precision_params = {}
    spindle_params = {}
    quality_params = {}
    power_params = {}
    other_params = {}
    
    for key, value in char_dict.items():
        key_lower = key.lower()
        if any(word in key_lower for word in ['диаметр', 'длина', 'масса', 'рмц', 'вес', 'габарит']):
            size_params[key] = value
        elif any(word in key_lower for word in ['ход', 'перемещение', 'скорость', 'подач', 'дискретность']):
            precision_params[key] = value
        elif any(word in key_lower for word in ['шпиндел', 'вращени', 'оборот', 'момент', 'частот']):
            spindle_params[key] = value
        elif any(word in key_lower for word in ['точность', 'шероховатость', 'резц']):
            quality_params[key] = value
        elif any(word in key_lower for word in ['мощность', 'электро', 'привод']):
            power_params[key] = value
        else:
            other_params[key] = value
    
    if size_params:
        content += "### Размеры и масса обработки\n\n"
        for key, value in size_params.items():
            content += f"**{key}:** {value}\n\n"
    
    if precision_params:
        content += "### Точность и перемещения\n\n"
        for key, value in precision_params.items():
            content += f"**{key}:** {value}\n\n"
    
    if spindle_params:
        content += "### Характеристики шпинделя\n\n"
        for key, value in spindle_params.items():
            content += f"**{key}:** {value}\n\n"
    
    if quality_params:
        content += "### Качество обработки\n\n"
        for key, value in quality_params.items():
            content += f"**{key}:** {value}\n\n"
    
    if power_params:
        content += "### Энергетические показатели\n\n"
        for key, value in power_params.items():
            content += f"**{key}:** {value}\n\n"
    
    if other_params:
        content += "### Дополнительные параметры\n\n"
        for key, value in other_params.items():
            content += f"**{key}:** {value}\n\n"
    
    # Dimensions table
    content += """## ГАБАРИТНЫЕ РАЗМЕРЫ И МАССА

| Параметр | Значение |
|----------|----------|
"""
    
    gabarity = char_dict.get('Габариты', 'уточняется')
    massa = char_dict.get('Масса', char_dict.get('Вес', 'уточняется'))
    
    content += f"| Габаритные размеры | {gabarity} |\n"
    content += f"| Масса станка | {massa} |\n\n"
    
    content += """## КОМПЛЕКТАЦИЯ

### Стандартная комплектация включает:

"""
    
    # Equipment with emojis
    emoji_map = {
        'патрон': '🔧',
        'центр': '🎯',
        'резцедержатель': '⚙️',
        'шестер': '⚡',
        'сож': '💧',
        'защит': '🛡️',
        'светильник': '💡',
        'винт': '🔩',
        'ключ': '🔑',
        'инструмент': '🛠️',
        'головка': '🎪',
        'люнет': '📍',
        'транспортер': '🧹',
        'система': '⚙️',
        'пульт': '🎮',
        'документац': '📋',
        'зип': '🔧'
    }
    
    equipment_list = machine.get('equipment', [])
    for eq in equipment_list:
        emoji = '🔧'
        for keyword, em in emoji_map.items():
            if keyword in eq.lower():
                emoji = em
                break
        content += f"{emoji} {eq}\n"
    
    content += """
### Опциональное оборудование:

🎪 Люнеты (подвижные и неподвижные)
🛠️ Дополнительные инструментальные блоки
🔄 Специализированная оснастка
🧹 Система автоматической уборки стружки

"""
    
    # Advantages
    content += "## ПРЕИМУЩЕСТВА\n\n"
    advantages = machine.get('advantages', [])
    for adv in advantages:
        content += f"✅ {adv}\n"
    
    content += f"""

## ПОСТАВКА И СЕРВИС

**ТД РУССтанкоСбыт** предлагает полный комплекс услуг:

🚚 **Доставка** по России и СНГ
🏗️ **Шеф-монтаж** и пусконаладочные работы
👨‍🏫 **Обучение персонала** работе на станке
🔧 **Гарантийное обслуживание**
📞 **Техническая поддержка** 24/7
🔩 **Поставка запасных частей** в кратчайшие сроки

### Запасные части в наличии:

- Шпиндельные бабки и узлы
- Коробки подач и коробки скоростей
- Фартуки и суппорты
- Задние бабки
- Электрооборудование
- Гидравлические и пневматические компоненты
- Шестерни, валы, подшипники
- Направляющие и винтовые пары

## КОНТАКТНАЯ ИНФОРМАЦИЯ

**ТД РУССтанкоСбыт**

📞 Телефон: +7 (XXX) XXX-XX-XX
📧 Email: info@tdrusstankosbyt.ru
🌐 Сайт: https://tdrusstankosbyt.ru
📍 Адрес: Москва, Россия

---

*Для получения коммерческого предложения на {machine['name']} ({machine['sku']}) свяжитесь с нашими специалистами.*

*Технические характеристики могут быть изменены производителем без предварительного уведомления.*
"""
    
    return content

def update_all_tkp():
    """Обновление всех ТКП файлов"""
    print("=" * 80)
    print("ОБНОВЛЕНИЕ ТКП В НОВОМ ФОРМАТЕ")
    print("=" * 80)
    
    # Load machines data
    with open(MACHINES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        machines = data['machines']
    
    print(f"\nОбновление {len(machines)} ТКП файлов...\n")
    
    for i, machine in enumerate(machines, 1):
        filename = f"{machine['sku']}.md"
        filepath = TKP_DIR / filename
        
        content = create_new_format_tkp(machine)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[{i}/{len(machines)}] ✅ {machine['sku']} - {machine['name'][:50]}...")
    
    print("\n" + "=" * 80)
    print("✅ ГОТОВО!")
    print("=" * 80)
    print(f"\nОбновлено {len(machines)} ТКП файлов в новом формате")
    print("Файлы готовы для Tilda!")
    print("=" * 80)

if __name__ == "__main__":
    update_all_tkp()
