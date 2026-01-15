import os
import json
import pandas as pd


class DataManager:
    """
    Klasa 'Magazynier'. Odpowiada za operacje na plikach (zapisywanie CSV,
    aktualizowanie bazy JSON). Nie pobiera danych z internetu.
    """

    def __init__(self):
        # Tu trzymamy nazwę naszej bazy danych ze słowami
        self.json_file = "word-counts.json"

    def save_csv(self, dataframe, phrase, table_num):
        """
        Bierze tabelkę (DataFrame) i zapisuje ją na dysku jako plik .csv.
        """
        # Tworzymy ładną nazwę pliku, np. "Produce_48_tabela_1.csv"
        # Zamieniamy spacje na podłogi, żeby system operacyjny nie marudził.
        filename = f"{phrase.replace(' ', '_')}_tabela_{table_num}.csv"

        # index=False -> Nie zapisuj numerów wierszy (0, 1, 2...), bo to tylko śmieci w pliku.
        # encoding='utf-8' -> Żeby polskie/koreańskie znaki się nie popsuły.
        dataframe.to_csv(filename, index=False, encoding='utf-8')
        return filename

    def update_word_counts(self, new_words):
        """
        Zadanie 3: Kluczowa funkcja.
        1. Liczy słowa z obecnego artykułu.
        2. Wczytuje stare wyniki z pliku JSON (jeśli istnieją).
        3. Sumuje stare i nowe wyniki.
        4. Zapisuje zaktualizowaną bazę na dysk.
        """

        # 1. Najpierw policzmy to, co właśnie pobraliśmy (lokalnie)
        current_counts = {}
        for w in new_words:
            # get(w, 0) oznacza: weź wartość dla słowa 'w', a jak go nie ma, to daj 0.
            current_counts[w] = current_counts.get(w, 0) + 1

        # 2. Teraz musimy pobrać "historię" z dysku
        global_counts = {}
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    global_counts = json.load(f)
            except Exception:
                # Jeśli plik jest uszkodzony, trudno - zaczynamy od zera, żeby nie wywalić programu.
                print("[MANAGER] Plik JSON był uszkodzony lub pusty. Tworzę nową bazę.")

        # 3. Sumowanie: Dodajemy nasze nowe znaleziska do głównego magazynu
        for word, count in current_counts.items():
            # Stara liczba + nowa liczba
            global_counts[word] = global_counts.get(word, 0) + count

        # 4. Zapisujemy wszystko z powrotem do pliku
        with open(self.json_file, "w", encoding="utf-8") as f:
            # ensure_ascii=False sprawia, że w pliku widzimy "ąę" zamiast dziwnych kodów.
            # indent=4 sprawia, że plik jest ładnie sformatowany (czytelny dla człowieka).
            json.dump(global_counts, f, ensure_ascii=False, indent=4)

        return len(new_words)