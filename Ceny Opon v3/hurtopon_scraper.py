import credentials
from lxml import html
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import openpyxl

# URL
url_login = 'http://www.hurtopon.pl/'

# XPATH
xpath_login_input = '//input[@id="ctLogin_usrName"]'
xpath_password_input = '//input[@id="ctLogin_pass"]'
xpath_login_button = '//a[@id="ctLogin_lnkSubm"]'
xpath_search_size_input = '//input[@id="searchCode"]'
xpath_search_season_select = '//select[@id="_ctProductSearch_StandardSearchV2CT_ddlSsn"]'
xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[4]'
xpath_50results_per_page_button = '//a[@id="listSett_lnkPrPg3"]/@href'
xpath_product_name = '//span[@class="pricesButton"]/text()'
xpath_product_size = '//div[@class="size"]/text()'
xpath_product_link = '//a[@class="hidden pricesButton"]'
xpath_product_price = '//div[@class="cenaNet"]/span[@class="ct"]/text()'
xpath_next_page_button = '//span[@id="p_1pgtn"]'
xpath_pages_togo = '//div[@id="listSett_upPagerUp"]/strong/text()'
xpath_loader = '//div [@id="loader"]'

# VARIABLES
pages_togo = []
tyres_name = []
tyres_size = []
tyres = []
links = []
prices = []
i = 1
timeout = 90
file = None

print("hurtopon.pl scraper v.1.1.20200529 \n")
print("Podaj parametry opon do importu")

while True:
    wybor = input("Sezon (1 - letnie, 2 - zimowe, 3 - całoroczne, 4 - wszystkie):")
    if wybor == '1':
        xpath_search_season_select = '//select[@id="_ctProductSearch_StandardSearchV2CT_ddlSsn"]/option[1]'
    elif wybor == '2':
        xpath_search_season_select = '//select[@id="_ctProductSearch_StandardSearchV2CT_ddlSsn"]/option[2]'
    elif wybor == '3':
        xpath_search_season_select = '//select[@id="_ctProductSearch_StandardSearchV2CT_ddlSsn"]/option[3]'
    elif wybor == '4':
        xpath_search_season_select = '//select[@id="_ctProductSearch_StandardSearchV2CT_ddlSsn"]/option[4]'
    else:
        continue
    break

while True:
    wybor = input("Kolejnosc pobierania (1 - Cena: od najniższej, 2 - Cena: od najniższej 3 - Dostępność: od najmniejszej, 4 - Dostępność: od najwiekszej, 5 - Nazwa: A-Z, 6 - Nazwa: Z-A):")
    if wybor == '1':
        xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[1]'
    elif wybor == '2':
        xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[2]'
    elif wybor == '3':
        xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[3]'
    elif wybor == '4':
        xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[4]'
    elif wybor == '5':
        xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[5]'
    elif wybor == '6':
        xpath_sort_by_select = '//select[@id="listSett_ddltMps"]/option[6]'
    else:
        continue
    break

try:
    print('=== START', time.ctime(time.time()))
    # logowanie
    print("Login...")
    browser = webdriver.Firefox()
    wait = WebDriverWait(browser, timeout)

    browser.get(url_login)
    login_input = browser.find_element_by_xpath(xpath_login_input)
    login_input.send_keys(credentials.login)
    password_input = browser.find_element_by_xpath(xpath_password_input)
    password_input.send_keys(credentials.password)
    login_button = browser.find_element_by_xpath(xpath_login_button)
    login_button.click()
    print("Login success!")

    # przygotowywanie strony do parsowania
    print("Searching...")
    search_season_select = browser.find_element_by_xpath(xpath_search_season_select)
    search_season_select.click()

    search_size_input = browser.find_element_by_xpath(xpath_search_size_input)
    search_size_input.clear()
    # search_size_input.send_keys("205/55R16")
    search_size_input.send_keys(Keys.RETURN)

    time.sleep(1)

    loader_invisible = wait.until(ec.invisibility_of_element_located((By.XPATH, xpath_loader)))
    sort_by_select = browser.find_element_by_xpath(xpath_sort_by_select)
    sort_by_select.click()

    #results50_per_page_button = browser.find_element_by_xpath(xpath_50results_per_page_button)
    #results50_per_page_button.click()
    #browser.execute_script("arguments[0].click();", results50_per_page_button)
    print("Search success!")

    # przygotowywanie zawartosci
    time.sleep(1)
    loader_invisible = wait.until(ec.invisibility_of_element_located((By.XPATH, xpath_loader)))
    page_content = browser.page_source
    parsing = html.fromstring(page_content)
    pages_togo.append(parsing.xpath(xpath_pages_togo))
    pages_togo = sum(pages_togo, [])
    pages_togo = [number.replace(' z ', '') for number in pages_togo]
    pages = ''.join(pages_togo)
    pages = int(pages)

    while i != pages:
        # parsowanie zawartosci
        while True:
            print('Page', i, 'of', pages)
            print("Parsing...")
            time.sleep(1)
            loader_invisible = wait.until(ec.invisibility_of_element_located((By.XPATH, xpath_loader)))
            page_content = browser.page_source
            parsing = html.fromstring(page_content)

            tyres_name.append(parsing.xpath(xpath_product_name))
            tyres_name = sum(tyres_name, [])
            tyres_name = [name.replace('\n        ', '') for name in tyres_name]

            tyres_size.append(parsing.xpath(xpath_product_size))
            tyres_size = sum(tyres_size, [])
            tyres_size = [re.findall("\w+/\w+R\w+\s\w+\s\w+", size) for size in tyres_size]
            tyres_size = sum(tyres_size, [])
            tyres_size = [size[:-2] + size[-1:] for size in tyres_size]

            tyres = [name+size for name,size in zip(tyres_name,tyres_size)]
            print(len(tyres), tyres)

            links = browser.find_elements_by_xpath(xpath_product_link)
            links = [link.get_attribute('href') for link in links]
            print(len(links), links)

            prices.append(parsing.xpath(xpath_product_price))
            prices = sum(prices, [])
            prices = [price.replace('od ', '') for price in prices]
            print(len(prices), prices)

            i=i+1
            if len(tyres) >= 10:
                browser.save_screenshot('.\error.png')
                break
            print("Parsing success!")



        # zapisywanie
        if len(tyres) == len(prices):
            print("Creating/opening xlsx...")
            try:
                file = openpyxl.load_workbook('.\hurtopon.xlsx')
            except Exception as error:
                print('=== ERROR', time.ctime(time.time()), error)
                print('Creating hurtopon.xlsx')
                file = openpyxl.Workbook()
                pass
            print("Writing xlsx...")
            sheet = file.active
            for row in range(len(tyres)):
                sheet.append([tyres[row], links[row], prices[row]])
            try:
                file.save('.\hurtopon.xlsx')
            except Exception as error:
                print('=== ERROR', time.ctime(time.time()), error)
                print('Renaming xlsx to hurtopon_'+str(int(time.time()))+'.xlsx')
                file.save('.\hurtopon_'+str(int(time.time()))+'.xlsx')
                pass
            file.close()
            print("Done!")
        else:
            print('Data mismatch')
            print(len(tyres), '!=', len(prices))
            browser.save_screenshot('.\error.png')

        # przechodzenie na kolejna stronę
        print('Next page...')
        tyres_name.clear()
        tyres_size.clear()
        tyres.clear()
        prices.clear()
        next_page_button = browser.find_element_by_xpath(xpath_next_page_button)
        next_page_button.click()
        print('Next page!')
    else:
        print('=== END', time.ctime(time.time()))
        browser.quit()
        file.close()

except Exception as error:
    # w przypadku błędu, wypisuje błąd
    print('=== ERROR', time.ctime(time.time()), error)
    browser.save_screenshot('.\error.png')
    # zamykam przegladarke
    browser.quit()
    file.close()


