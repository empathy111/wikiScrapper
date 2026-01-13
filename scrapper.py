import requests
from bs4 import BeautifulSoup
import os


class WikiScraper:
    # param phrase: Czego szukamy?
    # param use_local_file: Czy szukamy w internecie czy bierzemy z dysku

    def __init__(self, phrase, use_local_file=False):
        # Adres bazowy dla Harry Potter Wiki
        self.base_url = "https://harrypotter.fandom.com/wiki/"
        self.phrase = phrase
        self.use_local_file = use_local_file
        self.soup = None  # Tu wyląduje pobrany kod strony

    def _get_url(self):
        # Zamienia spacje na _
        return f"{self.base_url}{self.phrase.replace(' ', '_')}"

    def fetch(self):
        #Pobiera stronę z sieci LUB wczytuje z pliku
        formatted_filename = self.phrase.replace(' ', '_') + ".html"

        if self.use_local_file:
            # Tryb OFFLINE
            print(f"[DEBUG] Próba wczytania pliku lokalnego: {formatted_filename}")
            if not os.path.exists(formatted_filename):
                raise FileNotFoundError(f"Nie masz pliku: {formatted_filename}. Uruchom raz z internetem!")
            #Otwarce pliku i zapis do zmiennej
            with open(formatted_filename, "r", encoding="utf-8") as f:
                html_content = f.read()
        else:
            # Tryb ONLINE
            url = self._get_url()
            print(f"[INFO] Pobieranie z sieci: {url}")
            # Udajemy przeglądarkę
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            # Jedziemy sobie po stronę
            response = requests.get(url, headers=headers)
            #Sparwdzamy czy jest błąd
            if response.status_code != 200:
                raise Exception(f"Błąd! Strona zwróciła kod: {response.status_code}")
            #Zapis do zmiennej
            html_content = response.text

            # Zapis na dysk
            with open(formatted_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
                print(f"[INFO] Zapisano kopię strony jako {formatted_filename}")

        # BeautifulSoup przetwarza tekst na obiekt
        self.soup = BeautifulSoup(html_content, 'html.parser')
        return True

    def get_summary(self):
        """TODO"""
        if not self.soup:
            self.fetch()
        return "STRESZCZENIE    "


# test
if __name__ == "__main__":
    # Testujemy, czy pobierze stronę o Harrym Potterze
    try:
        scraper = WikiScraper("Harry Potter")
        scraper.fetch()
        print("Sukces! Pobraliśmy Harry'ego!")
    except Exception as e:
        print(f"Coś poszło nie tak: {e}")