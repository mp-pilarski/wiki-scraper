import time
from urllib.parse import unquote
from wiki_scraper.scraper import Scraper, ScraperError
from wiki_scraper.analyzer import Analyzer, AnalyzerError


class WikiController:
    def __init__(self, phrase, local_html_file=None):
        self.phrase = phrase
        self.scraper = Scraper(phrase, local_html_file)
        self.analyzer = Analyzer()
        pass

    def get_summary(self):
        """
        :return: First paragraph of the wiki page
        """
        return self.scraper.get_summary()

    def get_table(self, number, first_row_is_header=False):
        """
        Gets chosen table from wiki page in Pandas DataFrame and saves it in a csv file.

        Method tries ignoring first_row_is_header when table has a ``<thead>`` or ``<th>`` in first row.
        :param number: Table number on wiki page
        :param first_row_is_header: treat first row as header (optional)
        :return: DataFrame with 2 columns: Value, Count
        """
        table_df = self.scraper.get_table(number, first_row_is_header)
        table_df.to_csv(f"{self.phrase}.csv")
        return self.analyzer.analyze_table(table_df)

    def count_words(self):
        """
        Counts number of occurrences of words on wiki page and updates ``word-counts.json``
        """
        text_content = self.scraper.get_text_content()
        self.analyzer.count_words(text_content)
        self.analyzer.update_word_counts()

    def analyze_relative_word_frequency(self, mode, count, chart_path=None):
        """
        Analyzes relative word frequency
        :param mode: ``"article"`` or ``"language"``
        :param count: number of words to analyze
        :param chart_path: path to chart file (optional)
        :return DataFrame with frequencies of ``count`` most frequent words
        """
        df = self.analyzer.generate_frequency_table(mode, count)
        if chart_path is not None:
            self.analyzer.generate_chart(df, chart_path)
        return df

    def _link_to_phrase(self, link):
        """
        Converts a link to a wiki phrase
        :param link:
        :return: phrase or empty string
        """
        link = link.replace('/wiki/', '')
        link = link.replace('_', ' ')
        return link

    def auto_count_words(self, depth, wait_time, links_limit = None):
        """
        Executes the crawler to count words across linked pages.
        :param depth: How many links deep to crawl
        :param wait_time: Time to wait between visiting links
        :param links_limit: Limit to number of links from one page (optional)
        """
        visited = set()
        queue = [(self.phrase, 0)]
        print(self.phrase)
        while queue:
            cur_phrase, cur_depth = queue.pop(0)
            if cur_phrase in visited:
                continue
            visited.add(cur_phrase)
            print(f"Current phrase: \"{unquote(cur_phrase)}\" current depth: {cur_depth}")
            scraper = Scraper(cur_phrase)
            try:
                text = scraper.get_text_content()
                self.analyzer.count_words(text)
            except ScraperError:
                print(f"Skipping {cur_phrase} - problems with extracting text")

            if cur_depth < depth:
                links = scraper.get_internal_links()
                if links_limit is not None and len(links) > links_limit:
                    print(f"Number of links: {len(links)} but limited to {min(links_limit, len(links))} links")
                    links = links[:links_limit]
                else:
                    print(f"Number of links: {len(links)}")
                for link in links:
                    link = self._link_to_phrase(link)
                    if link not in visited:
                        queue.append((link, cur_depth + 1))
            time.sleep(wait_time)
        self.analyzer.update_word_counts()