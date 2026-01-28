import time
from scraper import WikiScraper


class WikiCrawler:
    def __init__(self, manager):
        self.manager = manager
        self.visited = set()

    def crawl(self, start_phrase, max_depth, wait_time):
        queue = [(start_phrase, 0)]

        print(f"[CRAWLER] Startujemy od: '{start_phrase}' z głębokością {max_depth}")

        while queue:
            current_phrase, current_depth = queue.pop(0)

            if current_phrase in self.visited:
                continue

            self.visited.add(current_phrase)
            print(f"\n[CRAWLER] Przetwarzam: '{current_phrase}' (Poziom: {current_depth})")

            try:
                # Scraper działa online
                scraper = WikiScraper(current_phrase, offline=False)
                words = scraper.get_all_words()

                if not words:
                    print("   -> Pusty artykuł lub błąd pobierania.")
                    continue

                self.manager.update_word_counts(words)
                print(f"   -> Zaktualizowano bazę ({len(words)} słów).")

                if current_depth < max_depth:
                    new_links = scraper.get_internal_links()
                    print(f"   -> Znaleziono {len(new_links)} linków wewnętrznych.")

                    count_added = 0
                    for link in new_links:
                        if link not in self.visited:
                            queue.append((link, current_depth + 1))
                            count_added += 1
                    print(f"   -> Dodano {count_added} nowych fraz do kolejki.")

                if wait_time > 0:
                    print(f"   -> Czekam {wait_time}s...")
                    time.sleep(wait_time)

            except Exception as e:
                print(f" Błąd przy '{current_phrase}': {e}")