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
        self.soup = None  # Tu wyląduje sparsowany HTML po pobraniu

    def fetch(self):
        # Wiki w linkach używa podłogi zamiast spacji (np. Produce_48)
        filename = f"{self.phrase.replace(' ', '_')}.html"

        if self.offline:
            # TRYB OFFLINE: Czytamy z dysku, żeby nie męczyć serwera przy testach
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Brak pliku {filename}. Uruchom najpierw online, żeby go pobrać.")
            with open(filename, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            # TRYB ONLINE: Pobieramy z internetu
            url = self.base_url + self.phrase.replace(' ', '_')
            print(f"[SCRAPER] Pobieram: {url}")

            # Udajemy przeglądarkę (User-Agent), inaczej Wiki może nas zablokować (błąd 403)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Błąd HTTP: {response.status_code} (Strona nie istnieje?)")

            html = response.text
            # Zapisujemy kopię na dysk ("cache"), żeby mieć na przyszłość
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

        # Robimy "zupę" z HTMLa, żeby łatwo wyszukiwać w nim elementy
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_summary(self):
        """Szuka pierwszego sensownego akapitu tekstu."""
        if not self.soup:
            self.fetch()  # Leniwe ładowanie - jak ktoś zapomniał wywołać fetch, robimy to sami

        # Szukamy tylko w głównej treści (omijamy menu, stopki itp.)
        content = self.soup.find(id='bodyContent')
        if not content:
            return None

        for p in content.find_all('p'):
            text = p.get_text().strip()
            # Wiki często ma na początku puste akapity albo "Redirects here".
            # Bierzemy pierwszy tekst dłuższy niż 30 znaków, który nie jest śmieciem.
            if len(text) > 30 and "Redirects here" not in text:
                return text
        return None

    def get_table_data(self, n=1):
        """Wyciąga n-tą tabelę i zamienia ją na DataFrame Pandasa."""
        if not self.soup:
            self.fetch()

        tables = self.soup.find_all('table')
        idx = n - 1  # Ludzie liczą od 1, Python od 0

        if not tables or idx >= len(tables):
            raise IndexError(f"Nie znaleziono tabeli nr {n} (na stronie jest ich {len(tables)})")

        selected_table = tables[idx]

        # SMART DETEKCJA: Sprawdzamy czy tabela ma znaczniki <th> (nagłówki).
        # Jak ma -> mówimy Pandasowi "pierwszy wiersz to nagłówek" (header=0).
        # Jak nie ma -> mówimy "nie ma nagłówka, bierz wszystko jak dane" (header=None).
        has_headers = selected_table.find('th') is not None
        header_option = 0 if has_headers else None

        # Trik z StringIO: Pandas chce czytać plik, więc udajemy, że string z HTMLem to plik
        html_str = str(selected_table)
        dfs = pd.read_html(StringIO(html_str), header=header_option)

        if not dfs:
            raise ValueError("Pandas nie był w stanie odczytać tej tabeli (może być pusta/dziwna)")

        df = dfs[0]

        # SPRZĄTANIE: Czasem nagłówek wczytuje się podwójnie (jako nagłówek I jako wiersz danych).
        # Jeśli nazwa kolumny jest taka sama jak pierwsza komórka -> usuwamy pierwszy wiersz.
        if header_option == 0 and not df.empty and len(df) > 0:
            first_col_name = str(df.columns[0])
            first_cell_value = str(df.iloc[0, 0])

            if first_col_name == first_cell_value:
                df = df.iloc[1:]  # Odetnij wiersz 0 (duplikat)
                df = df.reset_index(drop=True)  # Napraw numerację wierszy (żeby znowu była od 0)

        return df

    def get_all_words(self):
        """Wyciąga wszystkie słowa z artykułu do listy."""
        if not self.soup:
            self.fetch()

        content = self.soup.find(id='bodyContent')
        if not content:
            return []

        # separator=' ' jest kluczowy! Inaczej "Koniec akapitu.</p><p>Początek" sklei się w "akapitu.Początek"
        text = content.get_text(separator=' ', strip=True)

        # Regex \w+ znajduje ciągi liter i cyfr (ignoruje kropki, przecinki, spacje)
        # .lower() zamienia wszystko na małe litery, żeby "Muzyka" i "muzyka" były tym samym.
        words = re.findall(r'\w+', text.lower())
        return words

