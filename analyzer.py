import json
import pandas as pd
import matplotlib.pyplot as plt
import logging
from wordfreq import word_frequency, top_n_list

# Konfiguracja loggowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WordAnalyzer:
    def __init__(self, json_file="word-counts.json"):
        self.json_file = json_file

    def load_my_counts(self):
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def analyze(self, mode="article", count=10, chart_path=None):
        my_counts = self.load_my_counts()
        if not my_counts:
            logging.warning("Brak danych do analizy. Uruchom najpierw --count-words.")
            return

        # Pobieramy najczęstsze słowa angielskie jako bazę odniesienia
        lang_top_words = top_n_list('en', 10000)

        max_article_freq = max(my_counts.values()) if my_counts else 1
        freq_the = word_frequency('the', 'en')

        words_to_analyze = []
        if mode == 'article':
            # Słowa najczęstsze w zescrapowanych artykułach
            sorted_my_words = sorted(my_counts.items(), key=lambda item: item[1], reverse=True)
            words_to_analyze = [w[0] for w in sorted_my_words[:count]]
        else:
            # Słowa najczęstsze w języku angielskim
            words_to_analyze = lang_top_words[:count]

        data = []
        for word in words_to_analyze:
            # Częstotliwość w artykule (znormalizowana względem max wystąpień)
            art_val = my_counts.get(word, 0)
            art_freq = round(art_val / max_article_freq, 4) if word in my_counts else None

            # Częstotliwość w języku (znormalizowana względem słowa 'the')
            raw_lang_freq = word_frequency(word, 'en')
            lang_freq = round(raw_lang_freq / freq_the, 4) if raw_lang_freq > 0 else None

            data.append({
                "word": word,
                "frequency in article": art_freq,
                "frequency in wiki language": lang_freq
            })

        df = pd.DataFrame(data)
        logging.info(f"\nANALIZA (Tryb: {mode})")
        print(df.to_string(index=False, na_rep="-"))

        if chart_path:
            # Do wykresu zamieniamy None na 0
            df_plot = df.fillna(0)
            self.plot_chart(df_plot, chart_path)
            logging.info(f"Wykres zapisano do: {chart_path}")

    def plot_chart(self, df, path):
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(df["word"]))
        width = 0.35

        ax.bar([i - width / 2 for i in x], df["frequency in article"], width, label='Artykuł')
        ax.bar([i + width / 2 for i in x], df["frequency in wiki language"], width, label='Język')

        ax.set_xticks(x)
        ax.set_xticklabels(df["word"], rotation=45)
        ax.set_title("Porównanie częstotliwości słów")
        ax.legend()

        plt.tight_layout()
        plt.savefig(path)
        plt.close()