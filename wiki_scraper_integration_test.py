import sys
from scrapper import WikiScraper


def run_integration_test():
    print("Uruchamiam test integracyjny (Offline)...")

    # Tworzymy scrapera w trybie OFFLINE
    # On nie będzie pukał do internetu, tylko przeczyta plik Red_Velvet.html
    phrase = "Red Velvet"
    scraper = WikiScraper(phrase, offline=True)

    try:
        summary = scraper.get_summary()

        # Sprawdzamy czy streszczenie zaczyna się tak jak powinno
        expected_start = "Red Velvet"

        if summary and summary.startswith(expected_start):
            print("SUKCES: Streszczenie poprawnie odczytane z pliku!")
            sys.exit(0)  # Kod 0 oznacza sukces
        else:
            print(f"BŁĄD: Streszczenie nie pasuje! Zaczyna się od: {summary[:20]}...")
            sys.exit(1)  # Kod różny od 0 oznacza błąd (wymóg zadania!)

    except Exception as e:
        print(f"BŁĄD KRYTYCZNY: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_integration_test()