import json
import os
import string
from urllib.parse import unquote


class Analyzer:
    DICTIONARY_FILE = "word-counts.json"

    # Fajnie byloby miec tylko jeden egzemplarz na cały program?
    def __init__(self):
        self.word_count = {}
        pass

    def update_word_counts(self):
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
                print(f"File {self.DICTIONARY_FILE} is corrupted - file will be overwritten")
        for word, count in self.word_count.items():
            current_dict[word] = current_dict.get(word, 0) + count

        with open(self.DICTIONARY_FILE, 'w') as json_file:
            json.dump(current_dict, json_file)

        self.word_count = current_dict
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

    def generate_chart(self):

        pass