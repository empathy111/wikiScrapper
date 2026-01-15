import json
import pandas as pd
import matplotlib.pyplot as plt
from wordfreq import word_frequency, top_n_list


class WordAnalyzer:
    def __init__(self, json_file="word-counts.json"):
        self.json_file = json_file

    def load_my_counts(self):
        """Wczytuje policzone przez nas słowa z pliku JSON."""
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("[ANALYZER] Błąd: Brak pliku word-counts.json. Najpierw policz słowa!")
            return {}

    def analyze(self, mode="article", count=10, chart_path=None):
        """
        Główna funkcja analityczna.
        :param mode: 'article' (sortuj wg naszych słów) lub 'language' (wg języka ang.)
        :param count: ile słów pokazać (n)
        :param chart_path: ścieżka do zapisu wykresu (opcjonalne)
        """
        my_counts = self.load_my_counts()
        if not my_counts:
            return

        # 1. Przygotowanie danych
        data = []

        # Pobieramy najpopularniejsze słowa w angielskim (jako tło/kontekst)
        lang_top_words = top_n_list('en', 10000)

        # Znajdź najczęstsze słowo w naszym artykule (do normalizacji)
        if not my_counts:
            max_article_freq = 1
        else:
            max_article_freq = max(my_counts.values())

        # Wybieramy listę słów, które chcemy zbadać
        words_to_analyze = []

        if mode == 'article':
            # Sortujemy nasze słowa od najczęstszych (malejąco)
            sorted_my_words = sorted(my_counts.items(), key=lambda item: item[1], reverse=True)
            words_to_analyze = [w[0] for w in sorted_my_words[:count]]
        else:  # mode == 'language'
            # Bierzemy top N słów z ogólnego języka angielskiego
            words_to_analyze = lang_top_words[:count]

        # Tworzymy wiersze tabeli
        for word in words_to_analyze:
            # A. Nasza częstotliwość (znormalizowana: ilość / max_ilość)
            art_freq = my_counts.get(word, 0) / max_article_freq

            # B. Częstotliwość w języku (biblioteka wordfreq zwraca ułamek)
            # Dzielimy przez częstotliwość 'the', żeby też było w skali 0-1
            lang_freq_raw = word_frequency(word, 'en')
            lang_freq = lang_freq_raw / word_frequency('the', 'en')

            data.append({
                "word": word,
                "frequency in article": round(art_freq, 4),
                "frequency in wiki language": round(lang_freq, 4)
            })

        df = pd.DataFrame(data)

        # Wyświetlamy tabelę w konsoli
        print(f"\n--- ANALIZA (Tryb: {mode}, Słów: {count}) ---")
        print(df.to_string(index=False))

        # 2. Rysowanie wykresu (jeśli użytkownik podał ścieżkę)
        if chart_path:
            self.plot_chart(df, chart_path)
            print(f"\n[WYKRES] Zapisano wykres do: {chart_path}")

    def plot_chart(self, df, path):
        """Rysuje wykres słupkowy porównujący częstotliwości."""
        # Ustawienia wykresu
        fig, ax = plt.subplots(figsize=(10, 6))

        x = range(len(df["word"]))
        width = 0.35

        # Dwa słupki dla każdego słowa
        ax.bar([i - width / 2 for i in x], df["frequency in article"], width, label='Artykuł', color='skyblue')
        ax.bar([i + width / 2 for i in x], df["frequency in wiki language"], width, label='Język angielski',
               color='orange')

        # Opisy
        ax.set_ylabel('Znormalizowana częstotliwość')
        ax.set_title('Porównanie: Artykuł vs Język Angielski')
        ax.set_xticks(x)
        ax.set_xticklabels(df["word"], rotation=45)
        ax.legend()

        plt.tight_layout()  # Żeby napisy nie ucięło
        plt.savefig(path)
        plt.close()