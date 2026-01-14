
class Analyzer:
    DICTIONARY_FILE = "word-counts.json"

    def __init__(self):
        pass

    def update_word_counts(self):
        # Aktualizuje slownik
        pass

    def count_words(self, content):
        # TODO: trzeba zrobic normalizacje slow - usunac znaki typu . , ? sprowadzic do tylko malych liter (bo slowo na poczatku zdania jest takie samo jak w srodku ale rozni sie wielkoscia znakow)
        all_words = content.strip().split()

        distinct_words = set(all_words)
        current_count = {}
        #todo: moze bez petli?
        for word in distinct_words:
            current_count[word] = all_words.count(word)
        #TODO: current_count trzeba dac do update_word_count lub zwrocic jako wynik funkcji

    def generate_chart(self):
        pass