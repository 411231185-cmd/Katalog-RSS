import os
import logging
import argparse
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

load_dotenv()

MASHPORT_LOGIN = os.getenv("MASHPORT_LOGIN")
MASHPORT_PASSWORD = os.getenv("MASHPORT_PASSWORD")
MASHPORT_BASE_URL = os.getenv("MASHPORT_BASE_URL", "https://mashport.ru")

logging.basicConfig(filename=f'logs/mashport/{time.strftime("%Y-%m-%d")}.log', level=logging.INFO)

def login(driver):
    driver.get(MASHPORT_BASE_URL)
    time.sleep(2)
    driver.find_element(By.NAME, "username").send_keys(MASHPORT_LOGIN)
    driver.find_element(By.NAME, "password").send_keys(MASHPORT_PASSWORD)
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(5)

def create_listing(product):
    driver = webdriver.Chrome()
    login(driver)
    driver.get(f"{MASHPORT_BASE_URL}/create-listing")
    time.sleep(2)

    try:
        driver.find_element(By.NAME, "name").send_keys(product["name"])
        driver.find_element(By.NAME, "category").send_keys(product["category"])
        driver.find_element(By.NAME, "price").send_keys(str(product["price"]))
        driver.find_element(By.NAME, "description").send_keys(product["description"])
        upload_photos(product["photos"])
        driver.find_element(By.NAME, "submit").click()
        logging.info(f"Listing created for {product['name']}")
    except Exception as e:
        logging.error(f"Error creating listing: {e}")
    finally:
        driver.quit()

def upload_photos(photos):
    for photo in photos:
        # Здесь будет код для загрузки фото
        pass

def main(product_id=None):
    if product_id:
        # Получить данные товара по product_id
        product = {
            "name": "Патрон токарный 3-кулачковый 250мм",
            "category": "Комплектующие к станкам",
            "price": 15000,
            "currency": "RUB",
            "description": "...",
            "photos": ["path/to/photo1.jpg"],
            "sku": product_id,
            "manufacturer": "РУССтанкоСбыт"
        }
        create_listing(product)
    else:
        # Логика для публикации всего каталога
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", help="ID товара для публикации")
    parser.add_argument("--all", action="store_true", help="Публикация всего каталога")
    args = parser.parse_args()
    main(args.product_id)
