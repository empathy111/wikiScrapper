import unittest
import os
import json
from bs4 import BeautifulSoup
from scraper import WikiScraper
from manager import DataManager


class TestWikiProject(unittest.TestCase):

    # TEST 1: Weryfikacja metody get_all_words
    def test_word_cleaning(self):
        scraper = WikiScraper("Dummy", offline=True)
        html_content = """
           <div id="bodyContent">
               Red Velvet! Is the group. Red velvet.
           </div>
           """
        scraper.soup = BeautifulSoup(html_content, 'html.parser')

        words = scraper.get_all_words()
        expected = ["red", "velvet", "is", "the", "group", "red", "velvet"]

        self.assertEqual(words, expected)

    # TEST 2: Weryfikacja sumowania słów w DataManager
    def test_manager_summing(self):
        manager = DataManager()
        manager.json_file = "test_counts_temp.json"

        try:
            # Stan początkowy
            with open(manager.json_file, "w", encoding="utf-8") as f:
                json.dump({"the": 5}, f)

            new_words = ["the", "the", "the", "music"]
            manager.update_word_counts(new_words)

            # Sprawdzenie wyniku
            with open(manager.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data["the"], 8)
            self.assertEqual(data["music"], 1)

        finally:
            if os.path.exists(manager.json_file):
                os.remove(manager.json_file)

    # TEST 3: Weryfikacja filtrowania linków
    def test_link_filtering(self):
        scraper = WikiScraper("Dummy", offline=True)
        html_content = """
        <div id="bodyContent">
            <a href="/wiki/Red_Velvet">Link ok</a>
            <a href="/wiki/File:Image.jpg">Zły link (plik)</a>
            <a href="https://google.com">Zły link (zewnętrzny)</a>
            <a href="/wiki/Aespa">Link ok 2</a>
        </div>
        """
        scraper.soup = BeautifulSoup(html_content, 'html.parser')

        links = scraper.get_internal_links()

        self.assertIn("Red Velvet", links)
        self.assertIn("Aespa", links)
        self.assertNotIn("File:Image.jpg", links)
        self.assertNotIn("https://google.com", links)
        self.assertEqual(len(links), 2)

    # TEST 4: Weryfikacja generowania nazw plików CSV
    def test_csv_filename(self):
        manager = DataManager()
        # Import wewnątrz testu, aby nie zaśmiecać globalnych importów jeśli niepotrzebne
        import pandas as pd
        df = pd.DataFrame({'Col1': [1, 2]})

        phrase = "AC/DC Rock"
        generated_filename = manager.save_csv(df, phrase, 1)

        expected_filename = "AC-DC_Rock_tabela_1.csv"
        self.assertEqual(generated_filename, expected_filename)

        if os.path.exists(generated_filename):
            os.remove(generated_filename)


if __name__ == '__main__':
    unittest.main()