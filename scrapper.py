import requests
from bs4 import BeautifulSoup
import os


class WikiScraper:
    def __init__(self, szukana_fraza, tryb_offline=False):
        self.url = "https://www.generasia.com/wiki/"
        self.fraza = szukana_fraza
        self.tryb_offline = tryb_offline  # True = czytamy z pliku, False = pobieramy z internetu
        self.zupa = None  # Tutaj bedzie obiekt BeautifulSoup

    def pobierz_strone(self):
        #zamieniamy spacje na podkreslniki, bo tak ma ta wiki w URLu
        nazwa_pliku = f"{self.fraza.replace(' ', '_')}.html"

        if self.tryb_offline:
            print(f"--- Tryb offline: szukam pliku {nazwa_pliku} ---")

            # Sprawdzamy czy plik fizycznie istnieje na dysku
            if not os.path.exists(nazwa_pliku):
                raise FileNotFoundError("Nie masz jeszcze tego pliku! Odpal najpierw z tryb_offline=False.")

            # Czytanie pliku
            with open(nazwa_pliku, "r", encoding="utf-8") as plik:
                tekst_strony = plik.read()
        else:
            # Budujemy pełny link
            pelny_url = self.url + self.fraza.replace(' ', '_')
            print(f"--- Pobieranie z sieci: {pelny_url} ---")

            # User-Agent żeby strona nie myslala ze jestesmy botem
            naglowki = {'User-Agent': 'Mozilla/5.0'}
            odpowiedz = requests.get(pelny_url, headers=naglowki)

            # 200 to znaczy ze wszystko ok
            if odpowiedz.status_code != 200:
                raise Exception(f"Cos poszlo nie tak, kod bledu: {odpowiedz.status_code}")

            tekst_strony = odpowiedz.text

            # Zapisujemy html na przyszlosc
            with open(nazwa_pliku, "w", encoding="utf-8") as plik:
                plik.write(tekst_strony)
                print("Zapisano plik HTML na dysku.")

        # Tworzymy obiekt BS do przeszukiwania
        self.zupa = BeautifulSoup(tekst_strony, 'html.parser')

    def znajdz_opis(self):
        # Jesli ktos zapomnial wywolac pobieranie wczesniej
        if self.zupa is None:
            self.pobierz_strone()

        # Szukamy glownego diva z trescia (na tej wiki ma id bodyContent)
        glowny_kontener = self.zupa.find(id='bodyContent')

        if not glowny_kontener:
            return "Blad: Nie znalazlem glownej tresci na stronie."

        # Wyciagamy wszystkie 'p' czyli paragrafy
        wszystkie_akapity = glowny_kontener.find_all('p')

        for akapit in wszystkie_akapity:
            czysty_tekst = akapit.get_text().strip()

            # Omijamy puste lub bardzo krotkie linijki
            if len(czysty_tekst) < 30:
                continue

            # Omijamy teksty techniczne typu "Redirects here"
            if "Redirects here" in czysty_tekst or "For other uses" in czysty_tekst:
                continue

            # Jak przeszlo filtry, to pewnie to jest to streszczenie
            return czysty_tekst

        return "Niestety nic nie znaleziono."


# test
if __name__ == "__main__":
    try:
        moj_scraper = WikiScraper("BTS", tryb_offline=False)

        print(f"Analizuje fraze: {moj_scraper.fraza}")
        wynik = moj_scraper.znajdz_opis()
        print("\nwynik:")
        print(wynik)

    except Exception as blad:
        print(f"Wystapil blad w programie: {blad}")