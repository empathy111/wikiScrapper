import sys
import os
from scraper import WikiScraper


def run_integration_test():
    print("Uruchamiam test integracyjny")

    phrase = "Test_Integration_Dummy"
    filename = f"{phrase}.html"

    #jakiś html
    html_content = """
    <html>
        <body>
            <h1>Nagłówek strony</h1>
            <div id="bodyContent">
                <p>Krótki wstęp.</p>
                <p>Red Velvet (Korean: 레드벨벳) is a South Korean girl group.</p>
            </div>
        </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    try:
        scraper = WikiScraper(phrase, offline=True)
        summary = scraper.get_summary()

        print(f"Pobrane streszczenie: '{summary}'")

        # checkujemy
        expected_fragment = "Red Velvet (Korean: 레드벨벳) is a South Korean girl group."

        if summary and expected_fragment in summary:
            print("Streszczenie zostało poprawnie odczytane z pliku lokalnego!")
            exit_code = 0
        else:
            print("Streszczenie nie zgadza się z oczekiwaniami.")
            exit_code = 1

    except Exception as e:
        print(f"BŁĄD: {e}")
        exit_code = 1

    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print("Posprzątano plik testowy.")

    sys.exit(exit_code)


if __name__ == "__main__":
    run_integration_test()