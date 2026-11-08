# IDR — wyniki eksperymentu zagnieżdżonej kompresji zlib

**Data:** 2026-11-08. **Status:** lokalny eksperyment syntetyczny, odtwarzalny skryptem; nie jest walidacją empiryczną TIMDR ani dowodem okresowości.

## Metoda

- Python, biblioteka standardowa `zlib`, poziom kompresji 9.
- Cztery próbki: 4096 zer; tekst okresowy 4096 B; 4096 bajtów pseudolosowych (seed 20261108); dane pseudolosowe skompresowane raz wcześniej (seed 20261109; wejście 4107 B).
- W każdej próbce wykonano 20 warstw zagnieżdżonej kompresji: Zₙ₊₁=zlib.compress(Zₙ).
- Dekodowanie wykonano 20 razy, w kolejności odwrotnej; porównano bajty wejściowe i odzyskane.
- Skrypt: [compression_idr_experiment.py](../experiments/compression_idr_experiment.py). Uruchomienie: `python experiments/compression_idr_experiment.py --rounds 20 --output compression_idr_results.json`.

## Wyniki zbiorcze

| Próbka | Wejście | Po 1 warstwie | Po 20 warstwach | Odzyskanie dokładne |
|---|---:|---:|---:|---|
| Zera | 4096 B | 26 B | 220 B | TAK |
| Tekst okresowy | 4096 B | 79 B | 281 B | TAK |
| Pseudolosowe | 4096 B | 4107 B | 4314 B | TAK |
| Wcześniej skompresowane pseudolosowe | 4107 B | 4118 B | 4325 B | TAK |

Empiryczna entropia histogramu bajtów (bitów/bajt):

| Próbka | Oryginał | Warstwa 20 |
|---|---:|---:|
| Zera | 0.000 | 6.958 |
| Tekst okresowy | 4.187 | 6.969 |
| Pseudolosowe | 7.960 | 7.957 |
| Wcześniej skompresowane pseudolosowe | 7.956 | 7.953 |

## Interpretacja ograniczona do danych

1. Pierwsza warstwa silnie zmniejszyła reprezentację dwóch źródeł o dużej redundancji.
2. Dalsze zagnieżdżanie zwiększało rozmiar wszystkich czterech reprezentacji; kolejne kontenery dodają narzut.
3. W czterech próbach 20-krotne odwinięcie warstw odzyskało dokładnie oryginalne bajty.
4. Entropia histogramu pojedynczych bajtów zmieniła się znacząco dla danych redundantnych. Nie jest to miara całej informacji ani semantyki; nie wolno z tego wnioskować, że „informacji przybyło”.
5. Nie badano tu wielokrotnego kodowania odtworzonej treści z nowymi parametrami, kompresorów innych niż zlib, ani sygnałów rzeczywistych. Nie wykazano okresowości.

## Wniosek dla TIMDR

Dane wspierają użyteczność rozdzielenia **tożsamości treści** od **statystyki reprezentacji**. Dla tej próbki zachowanie treści potwierdza niezmiennik dekodowania, podczas gdy rozmiar i histogram bajtów ewoluują. To uzasadnia dalsze testowanie obserwabli IDR, ale nie dodanie nowego aksjomatu ani twierdzenia o fizycznym zachowaniu informacji.
