import os

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
        if self.local_html_file:
            if not os.path.exists(self.local_html_file):
                raise FileNotFoundError(f"File {self.local_html_file} does not exist")
            with open(self.local_html_file, "r") as f:
                html = f.read()
        else:
            response = requests.get(self._get_url())
            response.raise_for_status() #todo: czy to wymaga try..catch ?
            html = response.text

        self.soup = BeautifulSoup(html, "html.parser")

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

    def get_table(self, number, first_row_is_header=False):
        """
        Scrapes chosen table from wiki page and converts it to the pandas DataFrame.

        Method tries ignoring first_row_is_header when table has a ``<thead>`` or ``<th>`` in first row.
        :param number: number of the table on page (from 1)
        :param first_row_is_header: should the first row be treated as header (optional)
        :return: Pandas dataframe with parsed table data
        """
        content = self._get_content()
        html_tables = content.find_all("table")
        if number < 0 or number > len(html_tables):
            #todo: czy to powinien być pełnoprawny wyjątek?
            print(f"There is no table with that number. Found only {len(html_tables)} tables.")
            return None
        html_table = html_tables[number-1]

        # Sprawdzenie czy ignorowac first_row_is_header
        # Pierwszy zwykly wiersz nie jest nagłówkiem, gdy tabela ma <thead> lub <th> w pierwszym wierszu
        has_thead = html_table.find("thead") is not None
        has_th = False
        if not has_thead:
            first_row = html_table.find("tr")
            if first_row and first_row.find("th"):
                has_th = True
        has_header = has_thead or has_th

        if has_header or not first_row_is_header:
            df = pd.read_html(StringIO(str(html_table)))[0]
        else:
            # Ustawia pierwszy wiersz tabeli jako naglowek
            df = pd.read_html(str(html_table), header=0)[0]
        # Czyszczenie kolumn z samymi NaN
        df = df.dropna(axis="columns", how="all")
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
