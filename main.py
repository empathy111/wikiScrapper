import argparse
from scrapper import WikiScraper
from manager import DataManager
from analyzer import WordAnalyzer
from crawler import WikiCrawler
import pandas as pd


class WikiApp:
    def __init__(self, args):
        self.args = args
        self.manager = DataManager()
        self.analyzer = WordAnalyzer()
        self.crawler = WikiCrawler(self.manager)


    def run(self):
        if self.args.mode == 'analyze':
            self.analyzer.analyze(mode=self.args.analyze_mode, count=self.args.count, chart_path=self.args.chart)
            return

        if not self.args.phrase:
            print("Błąd: Musisz podać frazę!")
            return


        if self.args.mode == 'auto_count':
            self.crawler.crawl(start_phrase=self.args.phrase, max_depth=self.args.depth, wait_time=self.args.wait)
            return

        scraper = WikiScraper(self.args.phrase, offline=False)

        try:
            if self.args.mode == 'summary':
                text = scraper.get_summary()
                print(f"\n--- STRESZCZENIE: {self.args.phrase} ---\n{text if text else 'Nie znaleziono.'}")

            elif self.args.mode == 'table':
                df = scraper.get_table_data(self.args.number, force_header=self.args.first_row_is_header)
                filename = self.manager.save_csv(df, self.args.phrase, self.args.number)
                print(f"Zapisano do: {filename}")
                print("\n--- DANE TABELI ---")
                print(df.to_string(index=False))

                print("\n--- STATYSTYKA WARTOŚCI (Ile razy wystąpiły) ---")
                # Liczymy wystąpienia każdej wartości w całej tabeli
                stats = df.stack().value_counts().reset_index()
                stats.columns = ['Wartość', 'Ilość']
                print(stats.to_string(index=False))

            elif self.args.mode == 'count_words':
                words = scraper.get_all_words()
                self.manager.update_word_counts(words)
                print(f"Zaktualizowano word-counts.json o {len(words)} słów z artykułu '{self.args.phrase}'.")

        except Exception as e:
            print(f"Wystąpił błąd: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wiki Scraper Project")
    parser.add_argument("phrase", nargs='?', help="Fraza do wyszukania")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary", action="store_const", const="summary", dest="mode")
    group.add_argument("--table", action="store_const", const="table", dest="mode")
    group.add_argument("--count-words", action="store_const", const="count_words", dest="mode")
    group.add_argument("--analyze-relative-word-frequency", action="store_const", const="analyze", dest="mode")
    group.add_argument("--auto-count-words", action="store_const", const="auto_count", dest="mode")

    # Dodatkowe opcje
    parser.add_argument("--number", type=int, default=1)
    parser.add_argument("--first-row-is-header", action="store_true")  # DODANE
    parser.add_argument("--mode", dest="analyze_mode", default="article", choices=['article', 'language'])
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--chart")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--wait", type=float, default=1.0)

    args = parser.parse_args()
    WikiApp(args).run()