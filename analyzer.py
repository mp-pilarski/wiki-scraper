import json
import os
import string
import wordfreq as wq
import pandas as pd
from urllib.parse import unquote
import matplotlib.pyplot as plt
import numpy as np



class Analyzer:
    DICTIONARY_FILE = "word-counts.json"
    WIKI_LANG = 'en'

    # todo: Fajnie byloby miec tylko jeden egzemplarz na cały program?
    def __init__(self):
        self.word_count = {}
        pass

    def update_word_counts(self, loud=True):
        """
        Update the JSON file containing cumulative count of words.

        Reads the existing JSON file (if exists), updates the counts
        with words from self.word_count and saves it back to the file.

        :param loud: print information about JSON file state
        """
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
        """
        Count the number of words in a given string
        :param content: text to count words from
        :return: dictionary with words as keys and number of occurrences as values
        """
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
            self.word_count[word] = self.word_count.get(word, 0) + all_words.count(word)
        return current_count

    def generate_frequency_table(self, mode, count):
        """
        Compare the frequency of collected words against the wiki's language
        :param mode: Number of rows to be returned
        :param count: 'article' (sorted by article frequency), 'language' (sorted by language frequency)
        :return: dataFrame
        """
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
        df.set_index('Word', inplace=True)

        if mode == "article":
            df.sort_values(by=['Frequency in article'], ascending=False, inplace=True)
        else:
            df.sort_values(by=['Frequency in language'], ascending=False, inplace=True)
        return df

    def generate_chart(self, df, chart_path):
        """
        Generate and save a bar chart comparing word frequencies
        :param df: DataFrame containing word frequencies
        (usually from ``generate_frequency_table``)
        :param chart_path: path to save a PNG chart
        """
        ax = df[['Frequency in article', 'Frequency in language']].plot(
            kind='bar',
            figsize=(12, 6),
            color=['#f1c40f', '#e74c3c'],
            width=0.8,
            edgecolor='black'
        )

        plt.title('Frequency of some words on Wiki', fontsize=16)
        plt.ylabel('Frequency')
        plt.xlabel('Word')
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        plt.legend(['Wiki', 'English'])

        plt.tight_layout()
        plt.savefig(chart_path)

    def analyze_table(self, df):
        """
        Basic statistics of table
        :param df: dataframe with parsed table
        :return: DataFrame with 2 columns: Value, Count
        """
        #1. Get all values from dataFrame and flatten it to get a Series
        values_series = pd.Series(df.to_numpy().flatten())
        #2. Count all values in Series
        df_counts = values_series.value_counts().reset_index()
        df_counts.columns = ['value', 'count']
        return df_counts