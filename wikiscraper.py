import time
from urllib.parse import unquote
from scraper import Scraper
from analyzer import Analyzer
import pandas as pd

class WikiScraper:
    def __init__(self, phrase):
        self.phrase = phrase
        self.scraper = Scraper(phrase)
        self.analyzer = Analyzer()
        pass

    def summary(self):
        #todo: "Obsłuż przypadki, w których artykuł dla podanej frazy nie jest dostępny na wiki."
        return self.scraper.get_summary()

    def table(self, number, first_row_is_header=False):
        table_df = self.scraper.get_table(number, first_row_is_header)
        table_df = table_df.dropna(axis="columns", how="all")
        table_df.to_csv(f"{self.phrase}.csv")
        # todo: trzeba jeszcze: "Ponadto program powinien wypisać w formie tabeli , ile razy dana wartość wystąpiła w tabeli z wyłączeniem nagłówków."


    def count_words(self):
        text_content = self.scraper.get_text_content()
        self.analyzer.count_words(text_content)
        pass

    def analyze_relative_word_frequency(self, mode, count, chart_path=None):

        pass

    def _link_to_phrase(self, link):
        link = link.replace('/wiki/', '')
        link = link.replace('_', ' ')
        return link

    def auto_count_words(self, depth, wait_time, links_limit = None):
        visited = set()
        queue = [(self.phrase, 0)]
        print(self.phrase)
        while queue:
            cur_phrase, cur_depth = queue.pop(0)
            if cur_phrase in visited:
                continue
            visited.add(cur_phrase)
            print(f"Current phrase: \"{unquote(cur_phrase)}\" current depth: {cur_depth}")
            #todo: ten fragment trzeba zabezpieczyc przed bledami
            scraper = Scraper(cur_phrase)
            text = scraper.get_text_content()
            self.analyzer.count_words(text)

            if cur_depth < depth:
                links = scraper.get_internal_links()
                if links_limit is not None and len(links) > links_limit:
                    print(f"Number of links: {len(links)} but limited to {min(links_limit, len(links))} links")
                    links = links[:links_limit]
                else:
                    print(f"Number of links: {len(links)}")
                #todo: może zrobic funkcyjnie (?) oraz ulepszyc, zeby niepotrzebnie nie wstawialo do kolejki elementow, ktore juz sa w kolejce
                #todo: dodatkowo fraza powinna być znormalizowana
                #todo: metoda nie jest deterministyczna -> w zaleznosci od wykonania zwraca rozne wyniki
                for link in links:
                    link = self._link_to_phrase(link)
                    if link not in visited:
                        queue.append((link, cur_depth + 1))
            time.sleep(wait_time)
