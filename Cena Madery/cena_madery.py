#!/usr/bin/env python
from lxml import html
from datetime import date
import time
from selenium import webdriver
import xlwt
import openpyxl
import re

# adres strony
url_tui1 = 'https://www.tui.pl/wypoczynek/portugalia/madera/dorisol-florasol-residence-fnc11036/OfferCodeWS/WROFNC20200915050020200915202009222140L07FNC11036STX1GA02'
# ścieżka XPATH dla ceny
xpath_cena = '//*[@id="content"]/main/div[1]/div/div[1]/div[1]/div[1]/div/div[3]/div[1]/div[2]/div/div/span/text()'

# otwieram przegladarke i pobieram stronę
driver = webdriver.Firefox(service_log_path="D:\PROGRAMY\PyCharm Community Edition 2018.3\PycharmProjects\LittleProjects\geckodriver.log")
driver.get(url_tui1)
#driver.maximize_window()
print(url_tui1)

# czekam na załadowanie strony
time.sleep(10)

# pobieram i parsuje stronę
strona = driver.page_source
tree = html.fromstring(driver.page_source)

# wyszukuje interesujący nas element i oczyszczam dane
cena = tree.xpath(xpath_cena)
print(cena)
cena = [word.replace(' ', '') for word in cena]
print(cena)
cena = int(cena[0])
print(cena)

#ustawiam date wykonania skryptu
dzis = date.today()
data = dzis.strftime("%Y-%m-%d")
print(data)

#zamykam przegladarke
driver.quit()

#wrtie lists to xls
print("Zapisuję do xlsx...")
file = openpyxl.load_workbook('D:\PROGRAMY\PyCharm Community Edition 2018.3\PycharmProjects\LittleProjects\madera2020.xlsx')
sheet = file.active
sheet.append([data, cena, url_tui1])
file.save('D:\PROGRAMY\PyCharm Community Edition 2018.3\PycharmProjects\LittleProjects\madera2020.xlsx')
file.close()
print("OK. Naciśnij cokolwiek, aby wyjść.")

