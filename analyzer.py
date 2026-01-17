import json
import pandas as pd
import matplotlib.pyplot as plt
from wordfreq import word_frequency, top_n_list


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
            print("Brak danych do analizy. Uruchom najpierw --count-words.")
            return

        lang_top_words = top_n_list('en', 10000)
        max_article_freq = max(my_counts.values()) if my_counts else 1
        freq_the = word_frequency('the', 'en')

        words_to_analyze = []
        if mode == 'article':
            sorted_my_words = sorted(my_counts.items(), key=lambda item: item[1], reverse=True)
            words_to_analyze = [w[0] for w in sorted_my_words[:count]]
        else:
            words_to_analyze = lang_top_words[:count]

        data = []
        for word in words_to_analyze:
            # Nasza częstotliwość (znormalizowana)
            art_val = my_counts.get(word, 0)
            art_freq = round(art_val / max_article_freq, 4) if word in my_counts else None

            # Częstotliwość w języku
            raw_lang_freq = word_frequency(word, 'en')
            lang_freq = round(raw_lang_freq / freq_the, 4) if raw_lang_freq > 0 else None

            data.append({
                "word": word,
                "frequency in article": art_freq,
                "frequency in wiki language": lang_freq
            })

        df = pd.DataFrame(data)
        print(f"\n--- ANALIZA (Tryb: {mode}) ---")
        print(df.to_string(index=False, na_rep="-"))  # na_rep="-" robi luki tam gdzie None

        if chart_path:
            # Do wykresu musimy zamienić luki na 0, żeby matplotlib nie płakał
            df_plot = df.fillna(0)
            self.plot_chart(df_plot, chart_path)

    def plot_chart(self, df, path):
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(df["word"]))
        width = 0.35
        ax.bar([i - width / 2 for i in x], df["frequency in article"], width, label='Artykuł')
        ax.bar([i + width / 2 for i in x], df["frequency in wiki language"], width, label='Język')
        ax.set_xticks(x)
        ax.set_xticklabels(df["word"], rotation=45)
        ax.legend()
        plt.tight_layout()
        plt.savefig(path)
        plt.close()