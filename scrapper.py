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
        """Zwraca obiekt pandas DataFrame dla n-tej tabeli z autowykrywaniem nagłówków."""
        if not self.soup:
            self.fetch()

        tables = self.soup.find_all('table')
        idx = n - 1

        if not tables or idx >= len(tables):
            raise IndexError(f"Nie znaleziono tabeli nr {n}")

        selected_table = tables[idx]

        # Jeśli tabela ma znaczniki <th>, to znaczy, że ma nagłówek.
        # Wtedy header=0. Jeśli nie ma, header=None.
        has_headers = selected_table.find('th') is not None
        header_option = 0 if has_headers else None

        html_str = str(selected_table)
        dfs = pd.read_html(StringIO(html_str), header=header_option)

        if not dfs:
            raise ValueError("Pandas nie odczytał danych z tabeli")

        df = dfs[0]

        # Czyszczenie duplikatów jesli sa nagłówki
        if header_option == 0 and not df.empty and len(df) > 0:
            first_col_name = str(df.columns[0])
            first_cell_value = str(df.iloc[0, 0])

            # Jeśli nazwa kolumny i pierwsza komórka są identyczne
            if first_col_name == first_cell_value:
                df = df.iloc[1:]  # Odetnij wiersz 0
                df = df.reset_index(drop=True)  # Napraw numerację wierszy

        return df

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