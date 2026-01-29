import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO


class WikiScraper:
    def __init__(self, phrase, offline=False):
        self.base_url = "https://www.generasia.com/wiki/"
        self.phrase = phrase
        self.offline = offline
        self.soup = None
        # Generujemy nazwę pliku na podstawie frazy (zamiana spacji na podkreślenia)
        self.filename = f"{self.phrase.replace(' ', '_')}.html"

    def fetch(self):
        """Pobiera kod strony (z pliku lub z sieci) i parsuje go do BeautifulSoup."""
        if self.offline and os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            url = self.base_url + self.phrase.replace(' ', '_')
            headers = {'User-Agent': 'Mozilla/5.0'}

            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    raise Exception(f"Błąd HTTP: {response.status_code}. Strona '{self.phrase}' nie istnieje.")
                html = response.text

                # Zapisujemy cache dla trybu offline
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(html)
            except requests.RequestException as e:
                if self.offline:
                    raise FileNotFoundError(f"Brak pliku lokalnego {self.filename} i brak dostępu do sieci.")
                raise e

        self.soup = BeautifulSoup(html, 'html.parser')

    def get_summary(self):
        """Pobiera pierwszy sensowny akapit tekstu."""
        if not self.soup:
            self.fetch()

        content = self.soup.find(id='bodyContent')
        if not content:
            return None

        for p in content.find_all('p'):
            text = p.get_text().strip()
            # Warunek filtrujący:
            # 1. len > 30: Odrzucamy puste linie i krótkie metadane.
            # 2. "Redirects here": Odrzucamy informacje o przekierowaniach typowe dla wiki.
            if len(text) > 30 and "Redirects here" not in text:
                return text
        return None

    def get_table_data(self, n=1, force_header=False):
        """Wyciąga n-tą tabelę ze strony jako DataFrame."""
        if not self.soup:
            self.fetch()

        tables = self.soup.find_all('table')
        idx = n - 1
        if not tables or idx >= len(tables):
            raise IndexError(f"Nie znaleziono tabeli nr {n}.")

        selected_table = tables[idx]

        # Wykrywanie nagłówka
        header_option = 0 if (force_header or selected_table.find('th')) else None

        html_str = str(selected_table)
        try:
            dfs = pd.read_html(StringIO(html_str), header=header_option)
            if not dfs:
                raise ValueError("Pandas nie znalazł danych w tabeli.")
            df = dfs[0]
        except Exception as e:
            raise ValueError(f"Błąd parsowania tabeli: {e}")

        # Czyszczenie nagłówków, jeśli zostały zduplikowane w danych
        if header_option == 0 and not df.empty:
            if all(str(c) == str(v) for c, v in zip(df.columns, df.iloc[0])):
                df = df.iloc[1:].reset_index(drop=True)

        return df

    def get_all_words(self):
        """Zwraca listę wszystkich słów z treści artykułu."""
        if not self.soup:
            self.fetch()

        content = self.soup.find(id='bodyContent')
        if not content:
            return []

        text = content.get_text(separator=' ', strip=True)
        # Znajdź słowa (litery co najmniej 2 znaki), zamień na małe
        return re.findall(r'[a-z]{2,}', text.lower())

    def get_internal_links(self):
        """Wyciąga nazwy artykułów z linków wewnętrznych."""
        if not self.soup:
            self.fetch()

        links = set()
        content = self.soup.find(id='bodyContent')
        if not content:
            return []

        for a_tag in content.find_all('a', href=True):
            href = a_tag['href']
            # Specyfika mediawiki/generasia
            if href.startswith('/wiki/') and ':' not in href:
                phrase = href.replace('/wiki/', '').replace('_', ' ')
                links.add(phrase)

        return list(links)