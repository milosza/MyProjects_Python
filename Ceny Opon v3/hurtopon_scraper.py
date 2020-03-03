import credentials
from lxml import html
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import openpyxl

# URL
url_login = 'http://www.hurtopon.pl/'

# XPATH
xpath_login_input = '//input[@id="ctLogin_usrName"]'
xpath_password_input = '//input[@id="ctLogin_pass"]'
xpath_login_button = '//a[@id="ctLogin_lnkSubm"]'
xpath_search_size_input = '//input[@id="searchCode"]'
xpath_sort_by_size_select = '//select[@id="listSett_ddltMps"]/option[4]'
xpath_50results_per_page_button = '//a[@id="listSett_lnkPrPg3"]/@href'
xpath_product_name = '//span[@class="pricesButton"]/text()'
xpath_product_size = '//div[@class="size"]/text()'
xpath_product_price = '//div[@class="cenaNet"]/span[@class="ct"]/text()'
xpath_next_page_button = '//span[@id="p_1pgtn"]'
xpath_pages_togo = '//div[@id="listSett_upPagerUp"]/strong/text()'
xpath_loader = '//div [@id="loader"]'

# VARIABLES
pages_togo = []
tyres_name = []
tyres_size = []
tyres = []
prices = []
i = 1
timeout = 60
browser = webdriver.Firefox()
wait = WebDriverWait(browser, timeout)
file = None


try:
    print('=== START', time.ctime(time.time()))
    # logowanie
    print("Login...")
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
    search_size_input = browser.find_element_by_xpath(xpath_search_size_input)
    search_size_input.clear()
    #search_size_input.send_keys("205/55R16")
    search_size_input.send_keys(Keys.RETURN)
    time.sleep(1)
    loader_invisible = wait.until(ec.invisibility_of_element_located((By.XPATH, xpath_loader)))
    sort_by_size_select = browser.find_element_by_xpath(xpath_sort_by_size_select)
    sort_by_size_select.click()
    print("Search success!")
    #results50_per_page_button = browser.find_element_by_xpath(xpath_50results_per_page_button)
    #results50_per_page_button.click()
    #browser.execute_script("arguments[0].click();", results50_per_page_button)

    # przygotowywanie zawartosci
    time.sleep(1)
    loader_invisible = wait.until(ec.invisibility_of_element_located((By.XPATH, xpath_loader)))
    page_content = browser.page_source
    parsing = html.fromstring(page_content)
    pages_togo.append(parsing.xpath(xpath_pages_togo))
    print(pages_togo)
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
            tyres_size = [cena[:12]+cena[13] for cena in tyres_size]
            tyres_size = [size.replace('\n        ', '') for size in tyres_size]
            tyres = [name+size for name,size in zip(tyres_name,tyres_size)]
            print(len(tyres), tyres)

            prices.append(parsing.xpath(xpath_product_price))
            prices = sum(prices, [])
            prices = [price.replace('od ', '') for price in prices]
            print(len(prices), prices)

            i=i+1
            if len(tyres) >= 10:
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
                sheet.append([tyres[row], prices[row]])
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
    # zamykam przegladarke
    browser.quit()
    file.close()

