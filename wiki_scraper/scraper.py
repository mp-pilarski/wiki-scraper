import os

import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO


def is_internal(link):
    return link is not None and link.startswith("/wiki") and "File:" not in link


class ScraperError(Exception):
    pass


class Scraper:
    BASE_URL = "https://bulbapedia.bulbagarden.net/wiki/"

    def __init__(self, phrase, local_html_file=None):
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
            try:
                response = requests.get(self._get_url())
                response.raise_for_status()
                html = response.text
            except requests.exceptions.RequestException as e:
                raise ScraperError(f"Request error: {e}")

        self.soup = BeautifulSoup(html, "html.parser")

    def _get_content(self):
        if self.soup is None:
            self.scrape()
        content = self.soup.find("div", id="mw-content-text")
        if not content:
            raise ScraperError("No content found")
        return content

    def get_text_content(self):
        """
        Extracts the entire text content of the article page

        Excludes navigation, footers and other side-wide elements
        :return: A string containing the full text of the article
        """
        return self._get_content().get_text(separator=' ')

    def get_summary(self):
        """
        Extract the text content of the first paragraph of the article

        :return: The text of the first paragraph
        """
        content = self._get_content()
        paragraphs = content.findAll("p")
        if not paragraphs:
            raise ScraperError("No paragraphs found")
        first_paragraph = paragraphs[0]
        return first_paragraph.get_text()

    def get_table(self, number, first_row_is_header=False):
        """
        Extracts n-th table from wiki page and converts it to the pandas DataFrame.

        Method tries ignoring first_row_is_header when table has a ``<thead>`` or ``<th>`` in first row.
        :param number: number of the table on page (from 1)
        :param first_row_is_header: should the first row be treated as header (optional)
        :raises ValueError: if there is a table with that number
        :return: Pandas dataframe with parsed table data
        """
        content = self._get_content()
        html_tables = content.find_all("table")
        if not html_tables:
            raise ScraperError("No tables found")
        if number < 0 or number > len(html_tables):
            raise ValueError(f"There is no table with that number. Found only {len(html_tables)} tables.")
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
        """
        Extracts all internal links from the article page

        Excludes special pages (like: ``File:``)
        :return: A list of unique string representing the phrases (titles) of the links
        """
        content = self._get_content()
        unique_links = set()
        links = []  # Necessary for deterministic crawler behavior
        link_tags = content.find_all("a")
        if not link_tags:
            return []  # Not having any links is not an error
        for link in link_tags:
            if 'href' in link and is_internal(link['href']):
                # Delete anchors from links
                if '#' in link['href']:
                    link['href'] = link['href'].split('#')[0]
                if link['href'] not in unique_links:
                    links.append(link['href'])
        return links
