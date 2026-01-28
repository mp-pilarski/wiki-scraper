import json
import os
import re
import wordfreq as wq
import pandas as pd
from urllib.parse import unquote
import matplotlib.pyplot as plt
import numpy as np

class AnalyzerError(Exception):
    pass

class Analyzer:
    DICTIONARY_FILE = "word-counts.json"
    WIKI_LANG = 'en'

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
        json_dict = {}
        if os.path.exists(self.DICTIONARY_FILE):
            try:
                with open(self.DICTIONARY_FILE) as json_file:
                    json_dict = json.load(json_file)
            except json.JSONDecodeError:
                # File is corrupted or empty - it must be overwritten
                if loud:
                    print(f"File {self.DICTIONARY_FILE} is corrupted - file will be overwritten")
        # Update JSON dictionary
        for word, count in self.word_count.items():
            json_dict[word] = json_dict.get(word, 0) + count

        with open(self.DICTIONARY_FILE, 'w') as json_file:
            json.dump(json_dict, json_file)

        # Update word_count dictionary - it will be useful for further analysis
        self.word_count = json_dict
        if loud:
            print(f"Updated word counts in {self.DICTIONARY_FILE}")

    def get_clean_text(self, text):
        """
        Convert the given text to a list of cleaned words
        :param text: text to be cleaned
        :return: list of cleaned words (without punctuation)
        """
        text = text.lower()
        # Find all sequences of letters (ignores - and apostrophes)
        return re.findall(r"[^\W\d_]+", text)

    def count_words(self, content):
        """
        Count the number of words in a given string

        JSON dictionary file will NOT BE UPDATED (use update_word_counts after this method if you want to update it)
        :param content: text to count words from
        :return: dictionary with words as keys and number of occurrences as values
        """
        all_words = self.get_clean_text(content)

        distinct_words = set(all_words)
        current_count = {}
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
            raise AnalyzerError("Dictionary is empty - Try using --count_words or --auto_count_words before analyzing!")

        max_count = max(self.word_count.values())
        max_lang_freq = wq.word_frequency(wq.top_n_list(self.WIKI_LANG, 1)[0], self.WIKI_LANG)

        # Get 'count' most frequent words from article or wiki language
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
        # Index is set for better readability and for easier chart plotting
        df = df.set_index('Word')

        if mode == "article":
            df = df.sort_values(by=['Frequency in article'], ascending=False)
        else:
            df = df.sort_values(by=['Frequency in language'], ascending=False)
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
        # Get all values from dataFrame and flatten it to get a Series
        values_series = pd.Series(df.to_numpy().flatten())
        # Count all values in Series
        df_counts = values_series.value_counts().reset_index()
        df_counts.columns = ['value', 'count']
        return df_counts