#!/usr/bin/env python

import requests
from lxml import html
import re
import xlwt

#tworzenie pustych list na pobrane elementy
ilosc = 500
linki = []
kategorie = []
nagrody = []
punkty = []
punkty_temp = []
ceny = []
ceny_temp = []
ilosci = []
ilosci_temp = []
popularnosc = []
popularnosc_temp = []

#prizes catalogue check - wejscie pod url vitay.pl
def download_prizes_vitaypl(ilosc):
    global kategorie
    global nagrody
    global punkty
    global punkty_temp
    #pobranie zawartosci strony
    page = requests.get("http://www.vitay.pl/katalog-Vitay/wyszukiwarka/-1,-1,-1,false,false,1,Points,Desc,Full,"+str(ilosc)+".html")
    tree = html.fromstring(page.content)
    #tworzenie listy linków do konkretnych nagród ze strony
    linki = tree.xpath('//h4[@class="prizeName"]/a/@href')
    linki = ['http://www.vitay.pl' + link for link in linki]
    #parsing every prize page

    '''if len(linki) == ilosc:
        print("Katalog nagród jest wiekszy niz zadeklarowany przedział przeszukiwania. Sprawdź przedział")
        exit()'''

    for i in range(len(linki)):
        print("Pobieranie nagrody " + str(i+1) + " z " + str(len(linki)) +": "+ str(linki[i]))
        # pobieranie zawartosci strony z nagrodą
        page = requests.get(linki[i])
        tree = html.fromstring(page.content)
        # tworzenie listy kategorii
        kategorie.append(tree.xpath('//*[@id="ctl00_ctl00_breadcrumb_rptBreadcrumb_ctl05_hlBreadcrumbItem"]/text()'))
        #tworzenie listy nazw nagród
        nagrody.append(tree.xpath('//*[@id="prizePage"]/div[1]/h4/text()'))
        #tworzenie listy punktów nagród
        punkty.append(tree.xpath('//*[@id="mainCol"]/script/text()'))

    #list quality improvement for vitay.pl
    kategorie = sum(kategorie, [])

    nagrody = sum(nagrody, [])
    nagrody = [word.replace('\r\n                    ', '') for word in nagrody]
    nagrody = [word.replace('%', '%25') for word in nagrody]

    punkty = sum(punkty, [])
    #regex for 'pointsMax' from <script>
    for i in range(len(punkty)):
        match = re.search(r'pointsMax: \d+', punkty[i])
        if match:
            punkty_temp.append(match.group())
        else:
            punkty_temp.append('błąd')
    punkty = punkty_temp
    #number of ponts extraction
    punkty = [punkt.replace('pointsMax: ', '') for punkt in punkty]
    punkty = [int(i) for i in punkty]
    return (linki, kategorie, nagrody, punkty)


#market price check of prizes - wejscie pod url allegro.pl
def check_prices_allegropl(nagrody):
    global ceny
    ceny_temp = []
    global ilosci
    ilosci_temp = []
    global popularnosc
    popularnosc_temp = []
    for i in range(len(nagrody)):
        print("Sprawdzanie cen "+ str(i+1) +" z "+ str(len(nagrody)) +": "+ str(nagrody[i]))
        # pobranie zawartosci strony
        page = requests.get("https://allegro.pl/listing?string="+nagrody[i]+"&order=d")
        tree = html.fromstring(page.content)

        # tworzenie listy ilosci aukcji
        ilosci_temp = tree.xpath('//*[@class="listing-title__counter-value"]/text()')
        ilosci_temp = [ilosc.replace(' ', '') for ilosc in ilosci_temp]
        ilosci_temp = [int(i) for i in ilosci_temp]
        print("Ilosc aukcji: " +str(ilosci_temp[0]))
        ilosci.append(ilosci_temp[0])
        ilosci_temp = []

        # tworzenie listy ile osob kupilo
        popularnosc_temp.append(tree.xpath('//section[@class="_2e710a1"] | //span[@class ="_537f013"]/text()'))
        popularnosc_temp = sum(popularnosc_temp, [])
        popularnosc_temp = [popular.replace(' osoba kupiła', '') for popular in popularnosc_temp]
        popularnosc_temp = [popular.replace(' osoby kupiły', '') for popular in popularnosc_temp]
        popularnosc_temp = [popular.replace(' osób kupiło', '') for popular in popularnosc_temp]
        popularnosc_temp = [popular.replace(' osoba licytuje', '') for popular in popularnosc_temp]
        popularnosc_temp = [popular.replace(' osoby licytują', '') for popular in popularnosc_temp]
        popularnosc_temp = [popular.replace(' osób licytuje', '') for popular in popularnosc_temp]
        popularnosc_temp = [popular.replace('nikt nie licytuje', '0') for popular in popularnosc_temp]
        popularnosc_temp = [int(popular) for popular in popularnosc_temp]
        popularnosc_temp = sum(popularnosc_temp)
        print("Ilosc kupionych: "+str(popularnosc_temp))
        popularnosc.append(popularnosc_temp)
        popularnosc_temp = []

        # tworzenie listy cen
        ceny_temp.append(tree.xpath('//section[@class="_2e710a1"] | //*[@class="ecb7eff"]/text()'))
        ceny_temp = sum(ceny_temp, [])
        if not ceny_temp:
            ceny_temp = '0'
        ceny_temp = [cena.replace(' ', '') for cena in ceny_temp]
        ceny_temp = [int(cena) for cena in ceny_temp]
        print("Cena minimalna: "+str(min(ceny_temp)))
        ceny.append(min(ceny_temp))
        ceny_temp = []
    return (ilosci, popularnosc, ceny)

    #show lists
def show_lists():
    print("Podsumowanie pobierania:")
    print("Lista linków: " + str(linki))
    print("Lista kategorii: "+ str(kategorie))
    print("Lista nagród: "+ str(nagrody))
    print("Lista punktów: " + str(punkty))
    print("Lista ilsci aukcji: " + str(ilosci))
    print("Lista ilosci kupionych: " + str(popularnosc))
    print("Lista cen minimalnych: " + str(ceny))

#wrtie lists to xls
def write_lists_to_xls():
    print("Zapisuję do xls...")
    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("vitay")
    sheet1.write(0, 0, "Link")
    sheet1.write(0, 1, "Kategoria")
    sheet1.write(0, 2, "Nagroda")
    sheet1.write(0, 3, "Punkty")
    sheet1.write(0, 4, "Ilosc aukcji")
    sheet1.write(0, 5, "Ilosc kupionych")
    sheet1.write(0, 6, "Cena min")
    sheet1.write(0, 7, "Ilosc do kupienia za punkty")
    sheet1.write(0, 8, "Wartosc sprzedazy")
    i=0
    for n in linki:
        i = i + 1
        sheet1.write(i, 0, n)
    i=0
    for n in kategorie:
        i = i + 1
        sheet1.write(i, 1, n)
    i=0
    for n in nagrody:
        i = i + 1
        sheet1.write(i, 2, n)
    i = 0
    for n in punkty:
        i = i + 1
        sheet1.write(i, 3, n)
    i = 0
    for n in ilosci:
        i = i + 1
        sheet1.write(i, 4, n)
    i = 0
    for n in popularnosc:
        i = i + 1
        sheet1.write(i, 5, n)
    i = 0
    for n in ceny:
        i = i + 1
        sheet1.write(i, 6, n)
    i = 0
    book.save("vitay.xls")
    print("OK")

#download_prizes_vitaypl(ilosc)
nagrody =['MPM MPR-08']
check_prices_allegropl(nagrody)
#show_lists()
#write_lists_to_xls()