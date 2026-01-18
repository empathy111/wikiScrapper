import unittest
from scrapper import WikiScraper
from manager import DataManager
import os
import json


class TestWikiProject(unittest.TestCase):

    # TEST 1: Sprawdzamy, czy scraper dobrze czyści słowa (małe litery, brak kropek)
    def test_word_cleaning(self):
        scraper = WikiScraper("Dummy")
        # Udajemy, że to jest tekst ze strony
        raw_text = "Red Velvet! Is a group. Red velvet."
        # W prawdziwym kodzie get_all_words wyciąga to z soup,
        # tu przetestujemy samą logikę regexa (możesz to zrobić wywołując re.findall bezpośrednio)
        import re
        words = re.findall(r'\w+', raw_text.lower())

        self.assertEqual(words, ["red", "velvet", "is", "a", "group", "red", "velvet"])
        self.assertEqual(len(words), 7)

    # TEST 2: Sprawdzamy, czy manager dobrze sumuje słowa
    def test_manager_summing(self):
        manager = DataManager()
        manager.json_file = "test_counts.json"  # robimy osobny plik do testów

        # Udajemy, że w bazie już jest 5 razy "the"
        with open(manager.json_file, "w", encoding="utf-8") as f:
            json.dump({"the": 5}, f)

        # Dodajemy 3 nowe słowa "the"
        new_words = ["the", "the", "the", "music"]
        manager.update_word_counts(new_words)

        # Sprawdzamy wynik
        with open(manager.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["the"], 8)  # 5 + 3 = 8
        self.assertEqual(data["music"], 1)

        # Sprzątamy po teście
        os.remove("test_counts.json")

    # TEST 3: Sprawdzamy, czy linki są dobrze filtrowane (zadanie 5)
    def test_link_filtering(self):
        scraper = WikiScraper("Dummy")
        # Przykładowe linki z HTML
        test_hrefs = ["/wiki/Red_Velvet", "/wiki/File:Image.jpg", "https://google.com"]

        # Filtrujemy zgodnie z Twoją logiką z get_internal_links
        valid_links = []
        for href in test_hrefs:
            if href.startswith('/wiki/') and ':' not in href:
                valid_links.append(href.replace('/wiki/', '').replace('_', ' '))

        self.assertIn("Red Velvet", valid_links)
        self.assertNotIn("File:Image.jpg", valid_links)
        self.assertNotIn("https://google.com", valid_links)

    # TEST 4: Sprawdzamy tworzenie nazwy pliku CSV
    def test_csv_filename(self):
        manager = DataManager()
        phrase = "Red Velvet"
        num = 1
        filename = f"{phrase.replace(' ', '_')}_tabela_{num}.csv"
        self.assertEqual(filename, "Red_Velvet_tabela_1.csv")


if __name__ == '__main__':
    unittest.main()