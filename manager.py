import os
import json


class DataManager:
    def __init__(self):
        self.json_file = "word-counts.json"

    def save_csv(self, dataframe, phrase, table_num):
        #nazwa pliku
        safe_phrase = phrase.replace(' ', '_').replace('/', '-')
        filename = f"{safe_phrase}_tabela_{table_num}.csv"
        dataframe.to_csv(filename, index=False, encoding='utf-8')
        return filename

    def update_word_counts(self, new_words):
        # Zliczanie w bieżącym artykule
        current_counts = {}
        for w in new_words:
            current_counts[w] = current_counts.get(w, 0) + 1

        global_counts = {}

        # Ładowanie istniejącej bazy
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        global_counts = json.loads(content)
            except Exception as e:
                print(f"[MANAGER] Błąd odczytu JSON ({e}). Tworzę nową bazę.")

        # Aktualizacja bazy
        for word, count in current_counts.items():
            global_counts[word] = global_counts.get(word, 0) + count

        # Zapis
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(global_counts, f, ensure_ascii=False, indent=4)

        return len(new_words)