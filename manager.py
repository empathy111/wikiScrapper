import os
import json
import pandas as pd


class DataManager:
    def __init__(self):
        self.json_file = "word-counts.json"

    def save_csv(self, dataframe, phrase, table_num):
        """Zapisuje DataFrame do pliku CSV."""
        filename = f"{phrase.replace(' ', '_')}_tabela_{table_num}.csv"
        dataframe.to_csv(filename, index=False, encoding='utf-8')
        return filename

    def update_word_counts(self, new_words):
        """
        Zadanie 3: Aktualizuje plik JSON o nowe słowa.
        Działa przyrostowo (dodaje do istniejących wartości).
        """
        #Policz słowa z obecnego artykułu
        current_counts = {}
        for w in new_words:
            current_counts[w] = current_counts.get(w, 0) + 1

        #Wczytaj istniejącą bazę (jeśli jest)
        global_counts = {}
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    global_counts = json.load(f)
            except Exception:
                print("[MANAGER] Błąd pliku JSON, tworzę nowy.")

        # Zsumuj wyniki
        for word, count in current_counts.items():
            global_counts[word] = global_counts.get(word, 0) + count

        #Zapisz
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(global_counts, f, ensure_ascii=False, indent=4)

        return len(new_words)