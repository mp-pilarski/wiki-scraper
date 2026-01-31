import pytest
from wiki_scraper import scraper
from wiki_scraper.analyzer import Analyzer
from wiki_scraper import WikiScraper
from unittest.mock import mock_open, patch
import json

# Run unit tests with 'pytest -v' in main project directory


@pytest.mark.parametrize("link, result", [("/wiki/Team_Rocket", True), ("", False),
                                          ("/wiki/File:SSBU_Team_Rocket_Outfit_and_Hat.png", False), (None, False),
                                          ("https://www.mimuw.edu.pl/pl/", False)])
def test_is_internal(link, result):
    assert scraper.is_internal(link) == result


@pytest.mark.parametrize("link, phrase", [("/wiki/Team_Rocket", "Team Rocket"), ("/wiki/", ''), ("/wiki/Team", 'Team')])
def test_link_to_phrase(link, phrase):
    wikiscraper = WikiScraper("")
    assert wikiscraper._link_to_phrase(link) == phrase


@pytest.fixture
def analyzer():
    return Analyzer()


# todo: pozniej rozbudowac test o dodatkowe funkcjonalnosci po rozbudowaniu normalizacji
def test_counting_words(analyzer):
    assert analyzer.count_words("AAA.. AAA").get("aaa", 0) == 2  # pomijanie znaków interpunkcyjnych
    assert analyzer.count_words("./<> <>!@#$ ^#$%@!") == {}

    content = "Ala ma kota ma Ala"
    result = analyzer.count_words(content)
    assert result["ala"] == 2
    assert result["ma"] == 2
    assert result["kota"] == 1

    content2 = "ala, ma! kota."
    result = analyzer.count_words(content2)
    assert 'ala' in result
    assert 'ala,' not in result
    assert 'kota' in result
    assert 'kota.' not in result

    # sprawdzenie czy globalny stan słownika się aktualizuje
    assert analyzer.word_count['kota'] == 2  # slowo pojawilo sie w 2 miejscach


# Tests for basic_update_word_counts with mocking JSON file

# 1. Basic test
def test_basic_update_word_counts(analyzer):
    initial_file_content = json.dumps({'stare': 5})
    analyzer.count_words("stare stare stare. nowe nowe")
    print(analyzer.word_count)

    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=initial_file_content)) as mocked_file:
            analyzer.update_word_counts()
            mocked_file.assert_called_with(analyzer.DICTIONARY_FILE, "w")

            handle = mocked_file()
            # JSON library uses write() multiple times and we want every write() call
            written_str = "".join(call.args[0] for call in handle.write.call_args_list)
            saved_data = json.loads(written_str)
            # Check JSON file
            expected_dictionary = {'stare': 8, 'nowe': 2}
            assert saved_data == expected_dictionary
            # Check analyzer.word_count dictionary
            assert analyzer.word_count['stare'] == 8
            assert analyzer.word_count['nowe'] == 2


# 2. JSON file does not exist and new file must be created
def test_update_word_counts_new_file(analyzer):
    analyzer.count_words("nowe")

    with patch('os.path.exists', return_value=False):
        with patch('builtins.open', mock_open()) as mocked_file:
            analyzer.update_word_counts()

            handle = mocked_file()
            # JSON library uses write() multiple times and we want every write() call
            written_str = "".join(call.args[0] for call in handle.write.call_args_list)
            saved_data = json.loads(written_str)
            expected_dictionary = {'nowe': 1}
            assert saved_data == expected_dictionary
