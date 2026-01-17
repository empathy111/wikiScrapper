import time
from scrapper import WikiScraper


class WikiCrawler:
    def __init__(self, manager):
        self.manager = manager
        self.visited = set()

    def crawl(self, start_phrase, max_depth, wait_time):
        # Kolejka do odwiedzenia: (fraza, poziom_głębokości)
        queue = [(start_phrase, 0)]

        print(f"[CRAWLER] Startujemy od: '{start_phrase}' z głębokością {max_depth}")

        while queue:
            # Pobieramy pierwszy element z kolejki
            current_phrase, current_depth = queue.pop(0)

            # Jeśli już tu byliśmy -> pomijamy
            if current_phrase in self.visited:
                continue

            # Oznaczamy jako odwiedzone
            self.visited.add(current_phrase)

            print(f"\n[CRAWLER] Przetwarzam: '{current_phrase}' (Poziom: {current_depth})")

            try:
                # 1. Tworzymy scrapera dla danej frazy
                scraper = WikiScraper(current_phrase, offline=False)

                # 2. Pobieramy słowa i aktualizujemy bazę (to samo co --count-words)
                words = scraper.get_all_words()
                self.manager.update_word_counts(words)
                print(f"   -> Zaktualizowano bazę ({len(words)} słów).")

                # 3. Jeśli nie osiągnęliśmy limitu głębokości, szukamy nowych linków
                if current_depth < max_depth:
                    new_links = scraper.get_internal_links()
                    print(f"   -> Znaleziono {len(new_links)} nowych linków.")

                    for link in new_links:
                        if link not in self.visited:
                            # Dodajemy do kolejki z poziomem +1
                            queue.append((link, current_depth + 1))

                # 4. czekamy żeby nie zablokować serwera
                if wait_time > 0:
                    print(f"   -> Czekam {wait_time}s...")
                    time.sleep(wait_time)

            except Exception as e:
                print(f"   [!] Błąd przy '{current_phrase}': {e}")