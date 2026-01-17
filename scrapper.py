import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from io import StringIO
import re


class WikiScraper:
    def __init__(self, phrase, offline=False):
        self.base_url = "https://www.generasia.com/wiki/"  # Możesz zmienić na dowolną inną
        self.phrase = phrase
        self.offline = offline
        self.soup = None

    def fetch(self):
        filename = f"{self.phrase.replace(' ', '_')}.html"
        if self.offline:
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Brak pliku {filename}. Pobierz go najpierw online.")
            with open(filename, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            url = self.base_url + self.phrase.replace(' ', '_')
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Błąd HTTP: {response.status_code}. Strona '{self.phrase}' nie istnieje.")
            html = response.text
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

        self.soup = BeautifulSoup(html, 'html.parser')

    def get_summary(self):
        if not self.soup: self.fetch()
        content = self.soup.find(id='bodyContent')
        if not content: return None
        for p in content.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 30 and "Redirects here" not in text:
                return text
        return None

    def get_table_data(self, n=1, force_header=False):
        """Wyciąga tabelę. force_header wymusza traktowanie 1. wiersza jako nagłówek."""
        if not self.soup: self.fetch()
        tables = self.soup.find_all('table')
        idx = n - 1
        if not tables or idx >= len(tables):
            raise IndexError(f"Nie znaleziono tabeli nr {n}.")

        selected_table = tables[idx]

        # Jeśli użytkownik wymusił nagłówek lub BS go wykrył
        header_option = 0 if (force_header or selected_table.find('th')) else None

        html_str = str(selected_table)
        dfs = pd.read_html(StringIO(html_str), header=header_option)
        df = dfs[0]

        # Jeśli mamy nagłówki, usuwamy ewentualne duplikaty w pierwszym wierszu
        if header_option == 0 and not df.empty:
            if str(df.columns[0]) == str(df.iloc[0, 0]):
                df = df.iloc[1:].reset_index(drop=True)

        return df

    def get_all_words(self):
        if not self.soup: self.fetch()
        content = self.soup.find(id='bodyContent')
        if not content: return []
        text = content.get_text(separator=' ', strip=True)
        return re.findall(r'\w+', text.lower())

    def get_internal_links(self):
        if not self.soup: self.fetch()
        links = set()
        content = self.soup.find(id='bodyContent')
        if not content: return []
        for a_tag in content.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('/wiki/') and ':' not in href:
                phrase = href.replace('/wiki/', '').replace('_', ' ')
                links.add(phrase)
        return list(links)