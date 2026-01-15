import json
import os
import string
import wordfreq as wq
import pandas as pd
from urllib.parse import unquote
import matplotlib.pyplot as plt

from wordfreq import top_n_list, word_frequency


class Analyzer:
    DICTIONARY_FILE = "word-counts.json"
    WIKI_LANG = 'en'

    # Fajnie byloby miec tylko jeden egzemplarz na cały program?
    def __init__(self):
        self.word_count = {}
        pass

    def update_word_counts(self, loud=True):
        # Aktualizuje slownik
        #1. Pobierz slownik z pliku json
        #2. Polacz aktualne wyniki z wynikami z pliku json
        #3. Zapisz wyniki do pliku json
        current_dict = {}
        if os.path.exists(self.DICTIONARY_FILE):
            try:
                with open(self.DICTIONARY_FILE) as json_file:
                    current_dict = json.load(json_file)
            except json.JSONDecodeError:
                # Plik jest uszkodzony lub pusty. Trzeba nadpisać plik
                if loud:
                    print(f"File {self.DICTIONARY_FILE} is corrupted - file will be overwritten")
        for word, count in self.word_count.items():
            current_dict[word] = current_dict.get(word, 0) + count

        with open(self.DICTIONARY_FILE, 'w') as json_file:
            json.dump(current_dict, json_file)

        self.word_count = current_dict
        if loud:
            print(f"Updated word counts in {self.DICTIONARY_FILE}")

    def count_words(self, content):
        # TODO: trzeba zrobic normalizacje slow - usunac znaki typu . , ? sprowadzic do tylko malych liter (bo slowo na poczatku zdania jest takie samo jak w srodku ale rozni sie wielkoscia znakow)
        translator = str.maketrans('', '', string.punctuation)
        clean_text = content.translate(translator)
        all_words = clean_text.split()

        distinct_words = set(all_words)
        current_count = {}
        #todo: moze bez petli?
        for word in distinct_words:
            word = unquote(word)
            current_count[word] = all_words.count(word)
            self.word_count[word] = current_count.get(word, 0) +all_words.count(word)
        return current_count

    def generate_frequency_table(self, mode, count):
        self.update_word_counts(loud=False)
        if not self.word_count:
            #todo: tutaj wstawic prawdziwy wyjatek
            print("Dictionary is empty - Try using --count_words or --auto_count_words before analyzing!")
            return None

        max_count = max(self.word_count.values())
        max_lang_freq = wq.word_frequency(wq.top_n_list(self.WIKI_LANG, 1)[0], self.WIKI_LANG)

        if mode == "article":
            sorted_words = sorted(self.word_count.items(), key=lambda x: x[1], reverse=True)[:count]
            words = {w for w,c in sorted_words}
        else:
            top_lang_words = wq.top_n_list(self.WIKI_LANG, count)
            words = set(top_lang_words)

        rows = []
        for word in words:
            article_freq = self.word_count.get(word, 0) / max_count
            lang_freq = wq.word_frequency(word, self.WIKI_LANG) / max_lang_freq
            rows.append([word, article_freq, lang_freq])

        df = pd.DataFrame(rows)
        df.columns = ['Word', 'Frequency in article', 'Frequency in language']

        if mode == "article":
            df.sort_values(by=['Frequency in article'], ascending=False, inplace=True)
        else:
            df.sort_values(by=['Frequency in language'], ascending=False, inplace=True)

        return df

    def generate_chart(self, df, chart_path):
        pass
