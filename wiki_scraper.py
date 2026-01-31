import argparse
import sys
import logging
from scraper import WikiScraper
from manager import DataManager
from analyzer import WordAnalyzer
from crawler import WikiCrawler

# Konfiguracja loggowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WikiApp:
    def __init__(self, args):
        self.args = args
        self.manager = DataManager()
        self.analyzer = WordAnalyzer()
        self.crawler = WikiCrawler(self.manager)

    def run(self):
        # Tryb analizy, który nie wymaga frazy wejściowej
        if self.args.mode == 'analyze':
            self.analyzer.analyze(
                mode=self.args.analyze_mode,
                count=self.args.count,
                chart_path=self.args.chart
            )
            return

        # Dla pozostałych trybów fraza jest wymagana
        if not self.args.phrase:
            logger.error("Błąd: Musisz podać frazę dla wybranego trybu!")
            sys.exit(1)

        # Tryb crawlera
        if self.args.mode == 'auto_count':
            self.crawler.crawl(
                start_phrase=self.args.phrase,
                max_depth=self.args.depth,
                wait_time=self.args.wait
            )
            return

        # Inicjalizacja scrapera dla pojedynczej strony
        scraper = WikiScraper(self.args.phrase, offline=False)

        try:
            if self.args.mode == 'summary':
                text = scraper.get_summary()
                print(f"\nSTRESZCZENIE: {self.args.phrase}")
                print("-" * 40)
                print(text if text else 'Nie znaleziono odpowiedniego tekstu.')

            elif self.args.mode == 'table':
                df = scraper.get_table_data(
                    self.args.number,
                    force_header=self.args.first_row_is_header
                )
                filename = self.manager.save_csv(df, self.args.phrase, self.args.number)

                print(f"\nDANE TABELI (Zapisano do: {filename}):")
                # Opcja pandas, żeby tabelki ładniej wyglądały w terminalu
                import pandas as pd
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', 1000)
                print(df.to_string(index=False))

                print("\nSTATYSTYKA WARTOŚCI:")
                stats = df.stack().value_counts().reset_index()
                stats.columns = ['Wartość', 'Ilość']
                print(stats.to_string(index=False))

            elif self.args.mode == 'count_words':
                words = scraper.get_all_words()
                if words:
                    count = self.manager.update_word_counts(words)
                    logger.info(f"Zaktualizowano word-counts.json o {count} słów z artykułu '{self.args.phrase}'.")
                else:
                    logger.warning("Nie znaleziono słów w artykule.")

        except Exception as e:
            logger.error(f"Wystąpił błąd podczas działania programu: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Scraper Project")
    parser.add_argument("phrase", nargs='?', help="Fraza do wyszukania")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary", action="store_const", const="summary", dest="mode", help="Pobierz streszczenie")
    group.add_argument("--table", action="store_const", const="table", dest="mode", help="Pobierz tabelę")
    group.add_argument("--count-words", action="store_const", const="count_words", dest="mode", help="Policz słowa")
    group.add_argument("--analyze-relative-word-frequency", action="store_const", const="analyze", dest="mode",
                       help="Analizuj statystyki")
    group.add_argument("--auto-count-words", action="store_const", const="auto_count", dest="mode", help="Crawler")

    parser.add_argument("--number", type=int, default=1, help="Numer tabeli do pobrania")
    parser.add_argument("--first-row-is-header", action="store_true", help="Traktuj pierwszy wiersz jako nagłówek")
    parser.add_argument("--mode", dest="analyze_mode", default="article", choices=['article', 'language'],
                        help="Tryb analizy (wymaga --analyze...)")
    parser.add_argument("--count", type=int, default=10, help="Liczba słów do analizy")
    parser.add_argument("--chart", help="Ścieżka do zapisu wykresu (png)")
    parser.add_argument("--depth", type=int, default=1, help="Głębokość crawlera")
    parser.add_argument("--wait", type=float, default=1.0, help="Czas oczekiwania crawlera")

    args = parser.parse_args()
    WikiApp(args).run()