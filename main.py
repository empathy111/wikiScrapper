import argparse
from scrapper import WikiScraper  # Scraper: od chodzenia po internecie
from manager import DataManager  # Manager: od plików (CSV, JSON)
from analyzer import WordAnalyzer  # Analyzer: od wykresów i statystyki


class WikiApp:
    """
    Główna klasa sterująca (Kontroler).
    Łączy to, co wpisał użytkownik w terminalu, z odpowiednimi modułami programu.
    """

    def __init__(self, args):
        self.args = args

        # Zatrudniamy pomocników
        self.manager = DataManager()
        self.analyzer = WordAnalyzer()

        # Scraper wymaga podania frazy w konstruktorze.
        # Ale przy trybie --analyze użytkownik może nie podać frazy.
        # Wtedy wstawiamy "Dummy", żeby Scraper się nie wywalił przy tworzeniu,
        # mimo że i tak go nie użyjemy.
        phrase = self.args.phrase if self.args.phrase else "Dummy"

        # Tworzymy scrapera (offline=False oznacza, że pobieramy z sieci)
        self.scraper = WikiScraper(phrase, offline=False)

    def run(self):
        """Główna pętla decyzyjna programu."""

        # 1. ŚCIEŻKA ANALITYCZNA
        # Jeśli użytkownik chce tylko wykres, nie potrzebujemy frazy ani łączenia z Wiki.
        # Działamy na pliku JSON, który już mamy.
        if self.args.mode == 'analyze':
            self.analyzer.analyze(
                mode=self.args.analyze_mode,  # 'article' lub 'language'
                count=self.args.count,  # Ile słów pokazać
                chart_path=self.args.chart  # Gdzie zapisać obrazek (jeśli podano)
            )
            return  # Koniec pracy

        # 2. ŚCIEŻKA POBIERANIA (Scrapowania)
        # Jeśli to nie analiza, to musimy wiedzieć, CZEGO szukamy.
        if not self.args.phrase:
            print("Błąd: W tym trybie musisz podać frazę (np. python main.py 'Produce 48' --summary)")
            return

        print(f"--- START: Przetwarzam temat '{self.args.phrase}' ---")

        try:
            # TRYB: Streszczenie
            if self.args.mode == 'summary':
                text = self.scraper.get_summary()
                if text:
                    print("\n--- STRESZCZENIE ---")
                    print(text)
                else:
                    print("Nie znaleziono sensownego tekstu (lub to przekierowanie).")

            # TRYB: Tabela
            elif self.args.mode == 'table':
                print(f"\n--- TABELA NR {self.args.number} ---")
                try:
                    # Krok 1: Scraper wyciąga dane
                    df = self.scraper.get_table_data(self.args.number)

                    # Krok 2: Manager zapisuje je na dysk
                    file_saved = self.manager.save_csv(df, self.args.phrase, self.args.number)
                    print(f"Sukces! Zapisano plik: {file_saved}")

                    # Podgląd w konsoli
                    print("\nSzybka statystyka (Top 10 wartości):")
                    print(df.stack().value_counts().head(10))
                except Exception as e:
                    print(f"Nie udało się pobrać tabeli: {e}")

            # TRYB: Liczenie słów (zbieranie danych do bazy)
            elif self.args.mode == 'count_words':
                print("\n--- LICZENIE SŁÓW ---")
                # Krok 1: Scraper daje listę wszystkich słów
                words = self.scraper.get_all_words()
                print(f"Pobrano {len(words)} słów z artykułu.")

                # Krok 2: Manager aktualizuje naszą bazę wiedzy (plik JSON)
                self.manager.update_word_counts(words)
                print("Zaktualizowano plik 'word-counts.json'. Możesz teraz użyć --analyze.")

        except Exception as e:
            # Siatka bezpieczeństwa - jak coś wybuchnie, powiedz co, zamiast sypać błędami Pythona
            print(f"[CRITICAL ERROR] Wystąpił nieoczekiwany błąd: {e}")


if __name__ == "__main__":
    # To jest konfiguracja "Menu" w terminalu
    parser = argparse.ArgumentParser(description="Wiki Scraper - Pobieracz i Analityk")

    # Fraza jest opcjonalna (nargs='?'), bo --analyze jej nie potrzebuje
    parser.add_argument("phrase", nargs='?', help="Szukana fraza (np. 'Produce 48')")

    # GRUPA WYKLUCZAJĄCA SIĘ: Musisz wybrać jedną z głównych akcji
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary", action="store_const", const="summary", dest="mode", help="Pobierz streszczenie")
    group.add_argument("--table", action="store_const", const="table", dest="mode", help="Pobierz tabelę CSV")
    group.add_argument("--count-words", action="store_const", const="count_words", dest="mode",
                       help="Policz słowa i zapisz do bazy")

    # Ta flaga ma długą nazwę, bo tak chciał prowadzący w zadaniu
    group.add_argument("--analyze-relative-word-frequency", action="store_const", const="analyze", dest="mode",
                       help="Analizuj i rysuj wykresy")

    # Opcje dodatkowe (szczegóły)
    parser.add_argument("--number", type=int, default=1, help="Numer tabeli do pobrania (dla --table)")

    # Opcje tylko dla analizy
    parser.add_argument("--mode", dest="analyze_mode", default="article", choices=['article', 'language'],
                        help="Sortowanie: wg artykułu czy języka?")
    parser.add_argument("--count", type=int, default=10, help="Ile słów pokazać na wykresie")
    parser.add_argument("--chart", help="Ścieżka do pliku, gdzie zapisać wykres (np. wykres.png)")

    # Parsowanie (odczytanie) tego, co użytkownik wpisał i uruchomienie apki
    args = parser.parse_args()
    app = WikiApp(args)
    app.run()