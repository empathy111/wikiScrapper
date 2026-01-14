import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from io import StringIO
import re


class WikiScraper:
    def __init__(self, phrase, offline=False):
        self.base_url = "https://www.generasia.com/wiki/"
        self.phrase = phrase
        self.offline = offline
        self.soup = None

    def fetch(self):
        filename = f"{self.phrase.replace(' ', '_')}.html"

        if self.offline:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Brak pliku {filename}. Uruchom online.")
            with open(filename, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            url = self.base_url + self.phrase.replace(' ', '_')
            print(f"[SCRAPER] Pobieram: {url}")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Błąd HTTP: {response.status_code}")
            html = response.text
            # Zapisujemy kopię lokalną od razu
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

        self.soup = BeautifulSoup(html, 'html.parser')

    def get_summary(self):
        """Zwraca czysty tekst streszczenia."""
        if not self.soup:
            self.fetch()

        content = self.soup.find(id='bodyContent')
        if not content:
            return None

        for p in content.find_all('p'):
            text = p.get_text().strip()
            # Filtrowanie śmieci
            if len(text) > 30 and "Redirects here" not in text:
                return text
        return None

    def get_table_data(self, n=1):
        """Zwraca obiekt pandas DataFrame dla n-tej tabeli."""
        if not self.soup:
            self.fetch()

        tables = self.soup.find_all('table')
        idx = n - 1

        if not tables or idx >= len(tables):
            raise IndexError(f"Nie znaleziono tabeli nr {n}")

        html_str = str(tables[idx])
        dfs = pd.read_html(StringIO(html_str), header=0)

        if not dfs:
            raise ValueError("Pandas nie odczytał danych z tabeli")

        return dfs[0]  # Zwracamy DataFrame

    def get_all_words(self):
        """Zadanie 3: Wyciąga listę wszystkich słów z artykułu."""
        if not self.soup:
            self.fetch()

        content = self.soup.find(id='bodyContent')
        if not content:
            return []

        text = content.get_text(separator=' ', strip=True)
        # Regex wyciągający słowa (litery+cyfry)
        words = re.findall(r'\w+', text.lower())
        return words