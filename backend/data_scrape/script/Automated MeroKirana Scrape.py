# Importing Libraries
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

# Function to initialize the WebDriver
def init_driver(chrome_binary_path, chrome_driver_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_binary_path
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver

# Function to click "Load More" until all items are loaded
def load_all_items(driver):
    while True:
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Load More ']"))
            )
            load_more_button.click()
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            break

# Function to scrape product names, quantities, and prices
def scrape_data(driver, name_xpath, price_xpath):
    names_elements = driver.find_elements(By.XPATH, name_xpath)
    prices_elements = driver.find_elements(By.XPATH, price_xpath)

    names_list = []
    quantities = []
    prices = []

    for elem in names_elements:
        parts = elem.text.split(',')
        names_list.append(parts[0].strip())
        quantities.append(parts[-1].strip())

    for price in prices_elements:
        prices.append(price.text.strip())

    return names_list, quantities, prices

# Function to write data to CSV file
def write_to_csv(filename, date, names, quantities, prices):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        for name, qty, price in zip(names, quantities, prices):
            csvwriter.writerow([date, name, qty, price])

# Main function to scrape different categories
def scrape_category(driver, category_name, category_xpath, name_xpath, price_xpath, output_file):
    category = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, category_xpath))).click()
    load_all_items(driver)
    names, quantities, prices = scrape_data(driver, name_xpath, price_xpath)
    current_date = datetime.now().strftime("%Y-%m-%d")
    write_to_csv(output_file, current_date, names, quantities, prices)

# Specifying paths
chrome_binary_path = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
chrome_driver_path = r"D:\\chromedriver-win64\\chromedriver.exe"

# Initializing driver and opening the website
driver = init_driver(chrome_binary_path, chrome_driver_path)
driver.get('https://merokirana.com/#/')

# Defining XPaths for different categories and their respective output files
categories = [
    {
        "name": "Fruits",
        "xpath": "//*[contains(text(), 'Veg & Fruits')]",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_fruits.csv"
    },
    {
        "name": "Vegetables",
        "xpath": "//*[contains(text(), 'Veg & Fruits')]/following::a[2]",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_veggies.csv"
    },
    {
        "name": "Dairy",
        "xpath": "//*[contains(text(), 'Bakery & Dairy')]",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_dairy.csv"
    },
    {
        "name": "Rice",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_rice.csv"
    },
    {
        "name": "Flour",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_flour.csv"
    },
    {
        "name": "Oil",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_oil.csv"
    },
    {
        "name": "Pulses",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_pulses.csv"
    },
    {
        "name": "Dry Fruits",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_dry_fruits.csv"
    },
    {
        "name": "Salt",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_salt.csv"
    },
    {
        "name": "Spices",
        "xpath": "//a[@id='menu-05f8fd1183e14d7e-9e68202448f2de5f']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_spices.csv"
    },
    {
        "name": "Eggs",
        "xpath": "//a[@id='menu-8ac3e639f1224f43-999c081adb4d0794']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_eggs.csv"
    },
    {
        "name": "Meat",
        "xpath": "//a[@id='menu-8ac3e639f1224f43-999c081adb4d0794']",
        "name_xpath": "//div[@class='product-card__info']/h2/a",
        "price_xpath": "//span[@class='product-card__actual-price']/span[2]",
        "output_file": "MK_meat.csv"
    },
]

# Scraping each category
for category in categories:
    scrape_category(driver, category["name"], category["xpath"], category["name_xpath"], category["price_xpath"], category["output_file"])

# Closing the driver
driver.quit()
