#!/usr/bin/env python

from lxml import html
import requests

urlwyborcza = 'http://horoskopy.gazeta.pl/horoskop/rak/dzienny'
# składam adres strony i daty w celu pobierania aktualnego horoskopu
# ścieżka do elementu XPATH
#xpathdata = '//*[@id="holder_217"]/section/div[2]/div[3]/b[1]/text()'
xpathdata = '//*[@id="holder_217"]/section/div[1]/div[2]/text()'

#xpathwyborcza = '//*[@id="holder_217"]/section/div[2]/div[3]/p[1]/text()'
xpathwyborcza = '//*[@id="holder_217"]/section/p/text()'

# pobiera stronę z horoskopem
pagewyborcza = requests.get(urlwyborcza)
# parsuje stronę
tree = html.fromstring(pagewyborcza.content)
# wyszukuje interesujący nas element
datawyborcza = tree.xpath(xpathdata)
textwyborcza = tree.xpath(xpathwyborcza)
# wyświetla wyniki działania
print(datawyborcza)
print(textwyborcza)