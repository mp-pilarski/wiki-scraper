import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

# TODO: wiele metod musi sprawdzac czy strona jest juz zescapowana -> czy to zmienić (kosztem prostoty konstruktora?)
# TODO: wiele metod musi pobierac content -> moze powinien to byc atrybut klasy?

def is_internal(link):
    #TODO: Metoda moze byc statyczna!
    return link.startswith("/wiki") and "File:" not in link


class Scraper:
    BASE_URL = "https://bulbapedia.bulbagarden.net/wiki/"

    def __init__(self, phrase, local_html_file = None):
        self.phrase = phrase
        self.local_html_file = local_html_file
        self.soup = None

    def _get_url(self):
        # Zamiana spacji na _
        # czy trzeba zmieniac wielkosc liter?
        phrase = self.phrase.replace(' ', '_')
        return f"{self.BASE_URL}{phrase}"

    def scrape(self):
        # TODO: gdy zaznaczono use_local_file_instead, to powinno zamiast request uzyc lokalnego pliku html
        print(self._get_url())
        self.soup = BeautifulSoup(requests.get(self._get_url()).text, "html.parser")

    def _get_content(self):
        if self.soup is None:
            self.scrape()
        return self.soup.find("div", id="mw-content-text")

    def get_text_content(self):
        return self._get_content().get_text(separator=' ')

    def get_summary(self):
        content = self._get_content()
        first_paragraph = content.findAll("p")[0]
        return first_paragraph.get_text()

    def get_table(self, number, header_row=False):
        # todo: Czy zwracanie dataFrame to nie jest za duzo jak na tą metodę?
        # todo: sprawdzac czy number jest dobry i rzucac wyjatek
        content = self._get_content()
        html_table = content.findAll("table")[number-1]
        df = pd.read_html(StringIO(str(html_table)))[0]
        #TODO: ignorowac nietypowe kolumny, respektowac first-row-is-header
        #TODO: dane tekstowe trzeba zapisac do pliku szukana fraza.csv (zadanie dla CLI toola)
        #TODO: Ponadto program powinien wypisać w formie tabeli (tj. z wyraźnie widocznymi kolumnami;wystarczy tak, jak to robi pandas), ile razy dana wartość wystąpiła w tabeli z wyłączeniem nagłówków. => zadanie dla analizatora?
        return df

    def get_internal_links(self):
        content = self._get_content()
        unique_links = set()
        links = [] # Potrzebne, żeby metoda była deterministyczna
        #todo: można spróbować przepisać na funkcyjną wersję?
        for link in content.findAll('a'):
            try:
                if is_internal(link['href']):
                    #usuwanie linkow do konkretnej sekcji (todo: moze jako dodatkowa funkcja)
                    if '#' in link['href']:
                        link['href'] = link['href'].split('#')[0]
                    if link['href'] not in unique_links:
                        links.append(link['href'])
                #else:
                #    print(f"Skipping {link['href']}")
            except:
                pass
                #TODO: Takie lapanie wyjatkow jest brzydkie
        return links
