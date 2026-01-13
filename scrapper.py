import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from io import StringIO

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
            print(f"Pobieranie z sieci: {pelny_url}")

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

    def zapisz_tabele(self, numer_tabeli=1):
        """Zadanie 2: Pobiera tabelę, zapisuje do CSV i liczy wystąpienia wartości."""
        if self.zupa is None:
            self.pobierz_strone()

        # Szukamy wszystkich tabel <table>
        wszystkie_tabele = self.zupa.find_all('table')

        if not wszystkie_tabele:
            return "Brak tabel na tej stronie."

        # Sprawdzamy czy tabela o takim numerze istnieje
        indeks = numer_tabeli - 1
        if indeks >= len(wszystkie_tabele):
            return f"Nie ma tabeli nr {numer_tabeli}. Jest ich {len(wszystkie_tabele)}."

        # Wybieramy konkretną tabelę
        wybrana_tabela = wszystkie_tabele[indeks]

        try:
            #Zamieniamy na ramke
            html_string = str(wybrana_tabela)
            dfs = pd.read_html(StringIO(html_string), header=0)

            if not dfs:
                return "Blad: Pandas nie odczytal tabeli."

            dane_tabeli = dfs[0]  # To nasza glowna tabela

           #zapis do pliku
            nazwa_pliku = f"{self.fraza.replace(' ', '_')}_tabela_{numer_tabeli}.csv"

            dane_tabeli.to_csv(nazwa_pliku, index=False, encoding='utf-8')
            print(f"Zapisano plik: {nazwa_pliku}")

            #statystyki
            print(f"\nStatystyka wystąpień w tabeli nr {numer_tabeli}")

            liczniki = dane_tabeli.stack().value_counts()

            # Wypisujemy top 10 najczestszych wartosci (zeby nie zasmiecic ekranu caloscia)
            #MAYBE FIXME HERE bo chyba do zadania trzeba wypisać po prostu wszystko :(
            print(liczniki.head(10))

            return "Operacja zakonczona."

        except Exception as e:
            return f"Problem z przetwarzaniem tabeli: {e}"

#test
if __name__ == "__main__":
    print("ROZPOCZYNAM PRACĘ SKRAPERA")

    try:
        temat = "Produce 48"
        moj_scraper = WikiScraper(temat, tryb_offline=False)

        print(f"\nPobieram streszczenie dla: {temat}")
        streszczenie = moj_scraper.znajdz_opis()
        print(streszczenie)


        numer_tabeli = 3

        print(f"\nPobieram tabelę numer {numer_tabeli}...")
        wynik_tabeli = moj_scraper.zapisz_tabele(numer_tabeli)

        print(f"STATUS: {wynik_tabeli}")

    except Exception as blad:
        print(f"\nBłąd: {blad}")
        print("Problem z przetwarzaniem.")