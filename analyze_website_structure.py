import requests
from bs4 import BeautifulSoup

def analyze_rosstanko_com():
    """Анализ структуры rosstanko.com"""
    print("=" * 80)
    print("АНАЛИЗ: rosstanko.com")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        url = "https://rosstanko.com"
        print(f"\nПроверка главной страницы: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем все ссылки
            all_links = soup.find_all('a', href=True)
            print(f"\nВсего ссылок на странице: {len(all_links)}")
            
            # Фильтруем ссылки на товары/каталог
            product_keywords = ['product', 'tovar', 'catalog', 'katalog', 'stanok', 'запчаст']
            product_links = []
            
            for link in all_links:
                href = link.get('href', '').lower()
                text = link.text.strip().lower()
                
                if any(keyword in href or keyword in text for keyword in product_keywords):
                    product_links.append({
                        'href': link.get('href'),
                        'text': link.text.strip()[:60]
                    })
            
            if product_links:
                print(f"\nНайдено ссылок на товары/каталог: {len(product_links)}")
                print("\nПервые 10 ссылок:")
                for i, link in enumerate(product_links[:10], 1):
                    print(f"  {i}. {link['href']}")
                    print(f"     Текст: {link['text']}")
            
            # Проверяем форму поиска
            search_forms = soup.find_all('form')
            print(f"\nНайдено форм на странице: {len(search_forms)}")
            
            for i, form in enumerate(search_forms, 1):
                action = form.get('action', 'нет')
                print(f"  Форма {i}: action='{action}'")
                
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f"    - input: name='{inp.get('name')}', type='{inp.get('type')}'")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def analyze_russtanko_rzn():
    """Анализ структуры russtanko-rzn.ru"""
    print("\n" + "=" * 80)
    print("АНАЛИЗ: russtanko-rzn.ru")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    sites = ["https://russtanko-rzn.ru", "https://tdrusstankosbyt.ru"]
    
    for url in sites:
        try:
            print(f"\nПроверка: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Статус: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем ссылки на товары
                all_links = soup.find_all('a', href=True)
                print(f"Всего ссылок: {len(all_links)}")
                
                product_keywords = ['product', 'tovar', 'catalog', 'katalog', 'stanok']
                product_links = []
                
                for link in all_links:
                    href = link.get('href', '').lower()
                    text = link.text.strip().lower()
                    
                    if any(keyword in href or keyword in text for keyword in product_keywords):
                        product_links.append({
                            'href': link.get('href'),
                            'text': link.text.strip()[:60]
                        })
                
                if product_links:
                    print(f"\nНайдено ссылок на товары: {len(product_links)}")
                    print("\nПервые 5 ссылок:")
                    for i, link in enumerate(product_links[:5], 1):
                        print(f"  {i}. {link['href']}")
                        print(f"     Текст: {link['text']}")
                
                # Форма поиска
                search_forms = soup.find_all('form')
                print(f"\nФорм на странице: {len(search_forms)}")
                
                for i, form in enumerate(search_forms[:3], 1):
                    action = form.get('action', 'нет')
                    print(f"  Форма {i}: action='{action}'")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def get_example_product_page():
    """Получить пример страницы товара для анализа"""
    print("\n" + "=" * 80)
    print("ИНСТРУКЦИЯ ДЛЯ РУЧНОЙ ПРОВЕРКИ")
    print("=" * 80)
    print("""
Чтобы найти правильные CSS-селекторы:

1. Откройте rosstanko.com в браузере
2. Найдите ЛЮБОЙ товар (например, "вал шпиндельной бабки")
3. Откройте страницу товара
4. Нажмите F12 (откроется DevTools)
5. Найдите блок с описанием товара
6. Скопируйте сюда:
   - URL страницы товара
   - CSS-класс блока с кратким описанием
   - CSS-класс блока с полным описанием/ТКП

Пример:
  URL: https://rosstanko.com/product/val-shpindelnoy-babki
  Краткое описание: <div class="product-short-desc">...</div>
  Полное описание: <div class="product-full-desc">...</div>

То же самое для russtanko-rzn.ru или tdrusstankosbyt.ru
    """)

def main():
    print("=" * 80)
    print("АНАЛИЗ СТРУКТУРЫ САЙТОВ ДЛЯ ПАРСИНГА")
    print("=" * 80)
    
    analyze_rosstanko_com()
    analyze_russtanko_rzn()
    get_example_product_page()
    
    print("\n" + "=" * 80)
    print("СЛЕДУЮЩИЙ ШАГ")
    print("=" * 80)
    print("""
После получения информации о структуре сайтов:
1. Скопируйте мне URL примера товара с каждого сайта
2. Укажите CSS-классы для описаний
3. Я создам финальный парсер с правильными селекторами
    """)

if __name__ == "__main__":
    main()
