import pytest
import scraper
import wikiscraper
from analyzer import Analyzer
from wikiscraper import WikiScraper


#todo: sparametryzowac testy kiedy sie da
def test_is_internal():
    assert scraper.is_internal("/wiki/Team_Rocket") == True
    assert scraper.is_internal("") == False
    assert scraper.is_internal("/wiki/File:SSBU_Team_Rocket_Outfit_and_Hat.png") == False
    assert scraper.is_internal(None) == False
    assert scraper.is_internal("https://www.mimuw.edu.pl/pl/") == False

def test_link_to_phrase():
    wikiscraper = WikiScraper("") #todo: konstruktor do zmiany (poza tym to metoda statyczna)
    assert wikiscraper._link_to_phrase("/wiki/Team_Rocket") == "Team Rocket"
    assert wikiscraper._link_to_phrase("/wiki/") == ''
    assert wikiscraper._link_to_phrase("/wiki/Team") == 'Team'

#todo: tutaj zrobic fixture
#todo: pozniej rozbudowac test o dodatkowe funkcjonalnosci po rozbudowaniu normalizacji

@pytest.fixture
def analyzer():
    return Analyzer()

def test_counting_words(analyzer):
    assert analyzer.count_words("AAA.. AAA").get("AAA", 0) == 2 #pomijanie znaków interpunkcyjnych
    assert analyzer.count_words("./<> <>!@#$ ^#$%@!") == {}

    content = "Ala ma kota ma Ala"
    result = analyzer.count_words(content)
    assert result["Ala"] == 2
    assert result["ma"] == 2
    assert result["kota"] == 1

    content2 = "ala, ma! kota."
    result = analyzer.count_words(content2)
    assert 'ala' in result
    assert 'ala,' not in result
    assert 'kota' in result
    assert 'kota.' not in result

    #sprawdzenie czy globalny stan słownika się aktualizuje
    assert analyzer.word_count['kota'] == 2 #slowo pojawilo sie w 2 miejscach

def test_analyze_table(analyzer):
    #todo: do uzupelnienia
    pass
