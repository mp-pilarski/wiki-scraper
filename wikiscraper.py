import time
from urllib.parse import unquote
from scraper import Scraper
from analyzer import Analyzer
import argparse
import pandas as pd

#todo: obecny design nie ma sensu, poniewaz część metod nie jest zwiazana z konkretną frazą! -> trzeba zmienic konstruktor?
class WikiScraper:
    def __init__(self, phrase, local_html_file=None):
        self.phrase = phrase
        self.scraper = Scraper(phrase, local_html_file)
        self.analyzer = Analyzer()
        pass

    def get_summary(self):
        #todo: "Obsłuż przypadki, w których artykuł dla podanej frazy nie jest dostępny na wiki."
        return self.scraper.get_summary()

    def get_table(self, number, first_row_is_header=False):
        table_df = self.scraper.get_table(number, first_row_is_header)
        table_df.to_csv(f"{self.phrase}.csv")
        print(self.analyzer.analyze_table(table_df))


    def count_words(self):
        text_content = self.scraper.get_text_content()
        self.analyzer.count_words(text_content)
        self.analyzer.update_word_counts()

    def analyze_relative_word_frequency(self, mode, count, chart_path=None):
        df = self.analyzer.generate_frequency_table(mode, count)
        print(df)
        if chart_path is not None:
            self.analyzer.generate_chart(df, chart_path)

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
                for link in links:
                    link = self._link_to_phrase(link)
                    if link not in visited:
                        queue.append((link, cur_depth + 1))
            time.sleep(wait_time)
        self.analyzer.update_word_counts()


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Wiki pages using WikiScraper."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--summary", type=str, help="Searched phrase")

    group.add_argument("--table", type=str, help="Searched phrase")

    parser.add_argument("--number", type=int, help="Table number")
    parser.add_argument("--first-row-is-header", action="store_true", help="Ignore first row")

    group.add_argument("--count-words", type=str, help="Count words on phrase page")

    group.add_argument("--analyze-relative-word-frequency", action="store_true", help="Analyze relative word frequency")
    parser.add_argument("--mode", type=str, choices=["article", "language"], help="Analyze mode")
    parser.add_argument("--count", type=int, help="Number of words to analyze")
    parser.add_argument("--chart", type=str, help="Chart path")

    group.add_argument("--auto-count-words", action="store_true", help="Auto count words")
    parser.add_argument("--depth", type=int, help="Depth to analyze")
    parser.add_argument("--wait", type=int, help="Wait time between visiting new pages in seconds")

    args = parser.parse_args()

    if args.summary:
        scraper = WikiScraper(args.summary)
        print(scraper.get_summary())
    elif args.table:
        scraper = WikiScraper(args.table)
        scraper.get_table(args.number, args.first_row_is_header)
    elif args.count_words:
        scraper = WikiScraper(args.count_words)
        scraper.count_words()
    elif args.analyze_relative_word_frequency:
        if not args.mode:
            print("Mode parameter is required [article|language]")
            return
        scraper = WikiScraper("")
        scraper.analyze_relative_word_frequency(args.mode, args.count, args.chart)
    elif args.auto_count_words:
        scraper = WikiScraper(args.phrase)
        scraper.auto_count_words(args.depth, args.wait)

if __name__ == "__main__":
    main()