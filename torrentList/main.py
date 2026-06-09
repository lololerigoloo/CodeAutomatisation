from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.get("https://letterboxd.com/films/popular/page/2/")

time.sleep(5)

print(driver.page_source[:10000])
print("film-poster" in driver.page_source)
print(driver.find_elements(By.CSS_SELECTOR, ".film-poster"))