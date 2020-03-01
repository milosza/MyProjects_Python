#!/usr/bin/env python
from lxml import html
from datetime import date
import time
from selenium import webdriver
import openpyxl
from random import randint

while True:
    try:
        # adres strony
        url_tui1 = 'https://www.tui.pl/wypoczynek/portugalia/madera/dorisol-florasol-residence-fnc11036/OfferCodeWS/WROFNC20200901044020200901202009082145L07FNC11036STX1GA02'
        # ścieżka XPATH dla ceny
        xpath_cena = '//*[@id="content"]/main/div[1]/div/div[1]/div[1]/div[1]/div/div[3]/div[1]/div[2]/div/div/span/text()'

        print('=== START', time.ctime(time.time()))

        # otwieram przegladarke i pobieram stronę
        driver = webdriver.Firefox()
        driver.get(url_tui1)
        # driver.maximize_window()
        print('URL:', url_tui1)

        # czekam na załadowanie strony
        time.sleep(120)

        # pobieram i parsuje stronę
        strona = driver.page_source
        tree = html.fromstring(driver.page_source)

        # wyszukuje interesujący nas element i pobieram czas
        cena = tree.xpath(xpath_cena)
        dzis = date.today()

        # oczyszczam i przygotowuje dane
        cena = [word.replace(' ', '') for word in cena]
        cena = int(cena[0])
        data = dzis.strftime("%Y-%m-%d")
        print('Uzyskana cena:', cena)
        print('Data ceny:', data)

        # zamykam przegladarke
        driver.quit()

        # zapisuje dane do xls
        print("Zapisuję do xlsx...")
        file = openpyxl.load_workbook('.\madera2020.xlsx')
        sheet = file.active
        sheet.append([data, cena, url_tui1])
        file.save('.\madera2020.xlsx')
        file.close()
        print("Zapisane. Za 24h uruchomię się ponownie.")
        print('=== KONIEC', time.ctime(time.time()))
        print()
        time.sleep(60*60*24)
    except Exception as error:
        # w przypadku błędu, wypisuje błąd
        print('=== BLAD', time.ctime(time.time()))
        print(error)
        # zamykam przegladarke
        driver.quit()
        # czekam na kolejne wywolanie skryptu
        timeout = randint(120, 240)
        print("Spróbuję ponownie za", timeout, "sekund...")
        time.sleep(timeout)
        pass
    else:
        pass
