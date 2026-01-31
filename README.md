# WikiScraper

Narzędzie do pobierania i analizy danych z Bulbapedii. Do programu jest również dołączona analiza językowa.

Funkcjonalności:
* uruchomienie: `python3 wiki_scraper.py`
* help: `python3 wiki_scraper.py -h`
```
usage: wiki_scraper.py [-h] [--summary SUMMARY] [--table TABLE] [--number NUMBER] [--first-row-is-header] [--count-words COUNT_WORDS] [--analyze-relative-word-frequency] [--mode {article,language}] [--count COUNT] [--chart CHART] [--auto-count-words] [--depth DEPTH] [--wait WAIT] [--links_limit LINKS_LIMIT]

Scrape Wiki pages using WikiScraper.

options:
  -h, --help            show this help message and exit
  --summary SUMMARY     Get summary of a phrase
  --table TABLE         Get table from a phrase page
  --number NUMBER       Table number
  --first-row-is-header
                        Treat first row as header
  --count-words COUNT_WORDS
                        Count words in phrase article
  --analyze-relative-word-frequency
                        Analyze relative word frequency
  --mode {article,language}
                        Analyze mode
  --count COUNT         Number of words to analyze
  --chart CHART         Chart path
  --auto-count-words    Start frequence for crawler
  --depth DEPTH         Depth for crawler
  --wait WAIT           Wait time between visiting new pages in seconds
  --links_limit LINKS_LIMIT
                        Limit to number of links from one page (optional)
```
## Instalacja pakietu
```
python3 -m venv .venv
source .venv/bin/acivate
pip install -r requirements.txt
pip install .
```

## Struktura projektu:
* `/wiki_scraper` - implementacja pakietu `wiki_scraper`
* `/tests` - testy jednostkowe i integracyjne
* `/language_analysis` - notatnik Jupyter z przeprowadzoną analizą językową
* `wiki_scraper.py` - główny program CLI

## Testy:
* Uruchomienie testów jednostkowych: `pytest` w katalogu głównym
* Uruchomienie testu integracyjnego: `python3 tests/wiki_scraper_integration_test.py`

# Przykładowe użycie programu:
* Summary: `python3 wiki_scraper.py --summary "Team Rocket"`
* Table: `python3 wiki_scraper.py --table "Type" --number 2`
* Count words: `python3 wiki_scraper.py --count-words "Team Rocket"`
* Analyze relative word frequency: `python3 wiki_scraper.py --analyze-relative-word-frequency --mode "article" --count 5 --chart article-chart.png`
* Auto-count-words: `python3 wiki_scraper.py --auto-count-words "Item underflow" --depth 2 --wait 0.5 --links-limit 10` Użycie opcji `--links-limit` jest rekomendowane!