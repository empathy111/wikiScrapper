import argparse
from scrapper import WikiScraper
from manager import DataManager


class WikiApp:
    def __init__(self, args):
        self.args = args
        self.manager = DataManager()
        # Tworzymy scrapera z podanymi parametrami
        # Tutaj decydujemy czy offline czy online.
        # Na razie daję offline=False (pobieramy z neta), ale możemy to dodać do argumentów.
        self.scraper = WikiScraper(self.args.phrase, offline=False)

    def run(self):
        print(f"START: {self.args.phrase}")

        try:
            #Obsługa --summary
            if self.args.mode == 'summary':
                text = self.scraper.get_summary()
                if text:
                    print("\n--- STRESZCZENIE ---")
                    print(text)
                else:
                    print("Nie znaleziono streszczenia.")

            #Obsługa --table
            elif self.args.mode == 'table':
                print(f"\n--- TABELA NR {self.args.number} ---")
                try:
                    df = self.scraper.get_table_data(self.args.number)

                    # Zlecenie Managerowi zapisu
                    file_saved = self.manager.save_csv(df, self.args.phrase, self.args.number)
                    print(f"Zapisano plik: {file_saved}")

                    # Statystyka w konsoli
                    print("\nStatystyka (Top 10):")
                    print(df.stack().value_counts().head(10))

                except Exception as e:
                    print(f"Błąd tabeli: {e}")

            #Obsługa --count-words
            elif self.args.mode == 'count_words':
                print("\n--- LICZENIE SŁÓW ---")
                words = self.scraper.get_all_words()
                print(f"Pobrano {len(words)} słów z artykułu.")

                # Zlecenie Managerowi aktualizacji bazy JSON
                self.manager.update_word_counts(words)
                print("Zaktualizowano plik 'word-counts.json'.")

        except Exception as e:
            print(f"[CRITICAL ERROR] {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Scraper")

    # Główny argument: Fraza
    parser.add_argument("phrase", help="Szukana fraza (np. 'Produce 48')")

    # Flagi trybów (wybieramy jeden z nich)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary", action="store_const", const="summary", dest="mode", help="Pobierz streszczenie")
    group.add_argument("--table", action="store_const", const="table", dest="mode", help="Pobierz tabelę")
    group.add_argument("--count-words", action="store_const", const="count_words", dest="mode", help="Policz słowa")

    # Opcje dodatkowe
    parser.add_argument("--number", type=int, default=1, help="Numer tabeli (dla --table)")

    args = parser.parse_args()

    # Uruchomienie aplikacji
    app = WikiApp(args)
    app.run()