import argparse
from wiki_scraper import WikiScraper, ScraperError, AnalyzerError

def print_licence_information(website):
    print(f"Wyjście programu na licencji BY-NC-SA stworzone na podstawie artykułów dostępnych na stronie {website}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Wiki pages using WikiScraper."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--summary", type=str, help="Get summary of a phrase")

    group.add_argument("--table", type=str, help="Get table from a phrase page")

    parser.add_argument("--number", type=int, help="Table number")
    parser.add_argument("--first-row-is-header", action="store_true", help="Treat first row as header")

    group.add_argument("--count-words", type=str, help="Count words in phrase article")

    group.add_argument("--analyze-relative-word-frequency", action="store_true", help="Analyze relative word frequency")
    parser.add_argument("--mode", type=str, choices=["article", "language"], help="Analyze mode")
    parser.add_argument("--count", type=int, help="Number of words to analyze")
    parser.add_argument("--chart", type=str, help="Chart path")

    group.add_argument("--auto-count-words", action="store_true", help="Start frequence for crawler")
    parser.add_argument("--depth", type=int, help="Depth for crawler")
    parser.add_argument("--wait", type=int, help="Wait time between visiting new pages in seconds")
    parser.add_argument("--links_limit", type=int, help="Limit to number of links from one page (optional)")
    website_link = 'https://bulbapedia.bulbagarden.net/'

    args = parser.parse_args()
    try:
        if args.summary:
            scraper = WikiScraper(args.summary)
            print(scraper.get_summary())
        elif args.table:
            scraper = WikiScraper(args.table)
            count_vals = scraper.get_table(args.number, args.first_row_is_header)
            print(count_vals)
        elif args.count_words:
            scraper = WikiScraper(args.count_words)
            scraper.count_words()
        elif args.analyze_relative_word_frequency:
            if not args.mode:
                print("Mode parameter is required [article|language]")
                return
            scraper = WikiScraper("")
            df = scraper.analyze_relative_word_frequency(args.mode, args.count, args.chart)
            print(df)
        elif args.auto_count_words:
            scraper = WikiScraper(args.phrase)
            scraper.auto_count_words(args.depth, args.wait, args.links_limit)
    except ScraperError as err:
        print(f"Scraper error: {err}")
    except AnalyzerError as err:
        print(f"Analyzer error: {err}")
    print_licence_information(website_link)

if __name__ == "__main__":
    main()