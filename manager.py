import os
import json
import pandas as pd


class DataManager:

    def __init__(self):
        self.json_file = "word-counts.json"

    def save_csv(self, dataframe, phrase, table_num):
        filename = f"{phrase.replace(' ', '_')}_tabela_{table_num}.csv"

        dataframe.to_csv(filename, index=False, encoding='utf-8')
        return filename

    def update_word_counts(self, new_words):

        current_counts = {}
        for w in new_words:
            current_counts[w] = current_counts.get(w, 0) + 1


        global_counts = {}
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    global_counts = json.load(f)
            except Exception:
                print("[MANAGER] Plik JSON był uszkodzony lub pusty. Tworzę nową bazę.")

        for word, count in current_counts.items():
            global_counts[word] = global_counts.get(word, 0) + count


        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(global_counts, f, ensure_ascii=False, indent=4)

        return len(new_words)