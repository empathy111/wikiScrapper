# Wiki Scraper

Projekt służący do pobierania, analizy i przetwarzania danych ze stron typu Wiki (domyślnie skonfigurowany pod *generasia.com*, ale działa na silniku MediaWiki). Narzędzie umożliwia pobieranie streszczeń, ekstrahowanie tabel do plików CSV, zliczanie słów oraz zawiera analizę statystyczną języka.

## Wymagania i instalacja

Projekt wymaga zainstalowanego Pythona (zalecana wersja 3.8 lub nowsza).

1. Sklonuj repozytorium lub pobierz pliki projektu.
2. Zainstaluj wymagane biblioteki, uruchamiając w terminalu:

```shell
pip install -r requirements.txt
```

## Struktura projektu

- `wiki_scraper.py` – Główny plik uruchomieniowy.
- `scraper.py` – Logika pobierania i parsowania HTML.
- `crawler.py` – Logika chodzenia po linkach (BFS).
- `analyzer.py` – Analiza statystyczna i generowanie wykresów.
- `manager.py` – Zarządzanie danymi (zapis CSV, JSON).
- `wiki_tests.py` – Testy jednostkowe.
- `wiki_scraper_integration_test.py` – Test integracyjny.

## Instrukcja użycia

Program uruchamiamy z linii poleceń. Poniżej znajdują się przykłady dla każdej funkcjonalności.

### 1. Pobieranie streszczenia

Wypisuje pierwszy merytoryczny akapit artykułu dla podanej frazy.

```shell
python wiki_scraper.py "Red Velvet" --summary
```

### 2. Pobieranie tabeli

Pobiera n-tą tabelę z artykułu i zapisuje ją do pliku CSV.

- `--number`: numer tabeli (domyślnie 1).
- `--first-row-is-header`: opcjonalna flaga, jeśli pierwszy wiersz to nagłówek.

```shell
python wiki_scraper.py "Aespa" --table --number 1
```

### 3. Zliczanie słów 

Zlicza wystąpienia wszystkich słów w danym artykule i aktualizuje globalną bazę `word-counts.json`.

```shell
python wiki_scraper.py "Twice" --count-words
```

### 4. Crawler

Zaczyna od podanej frazy i podąża za linkami wewnętrznymi do zadanej głębokości, zliczając słowa z każdego odwiedzonego artykułu.

- `--depth`: głębokość przeszukiwania.
- `--wait`: czas oczekiwania w sekundach między zapytaniami.

```shell
python wiki_scraper.py "Aespa" --auto-count-words --depth 2 --wait 1.5
```

### 5. Analiza i wykresy

Porównuje częstotliwość słów zebranych w bazie (`word-counts.json`) ze statystykami języka angielskiego.

- `--mode`: `article` (najczęstsze w artykule) lub `language` (najczęstsze w jęz. angielskim).
- `--count`: ile słów wziąć do analizy.
- `--chart`: ścieżka do zapisu pliku PNG z wykresem.

```shell
python wiki_scraper.py --analyze-relative-word-frequency --mode article --count 15 --chart wykres_statystyki.png
```

## Testowanie

Projekt posiada zestaw testów weryfikujących poprawność działania bez konieczności łączenia się z siecią.

Uruchomienie testów jednostkowych:

```shell
python wiki_tests.py
```

Uruchomienie testu integracyjnego:

```shell
python wiki_scraper_integration_test.py
```
## Motywacja
Projekt wykonany w ramach zadania akademickiego: WikiScraper.
