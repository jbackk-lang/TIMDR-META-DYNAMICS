# Dynamika reprezentacji informacji pod wpływem kompresji (IDR)

**Status:** hipoteza badawcza i protokół eksperymentalny. Nie jest aksjomatem TIMDR ani dowodem fizycznej zmiany informacji. **Przypisanie:** META-DYNAMICS; powiązania: Helix-Lock i GIA-TIMDR.

## 1. Pytanie badawcze

Czy kolejne transformacje kompresji zmieniają mierzalną strukturę reprezentacji danych, mimo że bezstratny cykl kompresja–dekompresja zachowuje dokładnie oryginalną treść?

Rozdzielamy: (1) treść źródłową, (2) reprezentację zakodowaną, (3) stan algorytmu i metadane, (4) wynik dekodowania. Równość treści nie oznacza równości reprezentacji.

## 2. Operatory

Niech X₀ będzie skończonym ciągiem bajtów, C koderem, D dekoderem. Z₁=C(X₀). Bezstratność oznacza:

D(C(X))=X.

Dla n poprawnie zagnieżdżonych warstw, dekodowanych w odwrotnej kolejności, Dⁿ(Cⁿ(X))=X. Nie wynika stąd Cⁿ(X)=X ani okresowość kodera. Kolejna kompresja kontenera gzip/zlib jest kompresją strumienia bajtów poprzedniego kontenera, nie ponownym kodowaniem semantycznie odzyskanej treści.

## 3. Obserwable

Dla reprezentacji Zₙ rejestrujemy:
- Lₙ=|Zₙ| — długość w bajtach;
- Kₙ=|X₀|/Lₙ — współczynnik rozmiaru, nie uniwersalna miara informacji;
- H₁(Zₙ)=−Σ_b pₙ(b)log₂pₙ(b) — empiryczna entropia histogramu bajtów;
- Uₙ — liczba różnych wartości bajtu;
- dₙ=½Σ_b|pₙ(b)−pₙ₋₁(b)| — odległość całkowitej wariacji histogramów;
- Qₙ — dokładny test odzyskania: Dⁿ(Zₙ)==X₀.

H₁ opisuje rozkład symboli, nie pełną entropię źródła ani semantyczną zawartość. Histogram ignoruje kolejność i zależności wyższego rzędu. Wysoka H₁ nie dowodzi większej ilości informacji.

## 4. Hipotezy falsyfikowalne

- H0: zmiany Lₙ, H₁ i dₙ wynikają z narzutu formatu i nie wykazują stabilnej struktury poza tym, co przewiduje model kontrolny.
- H1: dla określonych klas źródeł występują powtarzalne profile obserwabli, odróżnialne od kontroli.
- H2: wektor Vₙ=(Lₙ,H₁,dₙ,Uₙ) wykazuje okres p>1 według kryterium tolerancji ustalonego przed analizą.
- H3: Qₙ=false wskazuje błąd, uszkodzenie, błędne zagnieżdżenie lub użycie kodera stratnego, a nie oczekiwany skutek poprawnej kompresji bezstratnej.

## 5. Protokół

1. Zahashować oryginał SHA-256 i zachować go bez zmian.
2. Przygotować tekst UTF-8, dane okresowe, losowe z ustalonym seedem, pliki już skompresowane oraz rzeczywiste sygnały z jednostkami.
3. Zapisać koder, wersję biblioteki i parametry.
4. Dla n=1…N jawnie zagnieżdżać strumienie; po każdej rundzie zapisać Lₙ,H₁,Uₙ,dₙ i SHA-256.
5. Dekodować N razy w odwrotnej kolejności; porównać bajty i hash z oryginałem.
6. Powtórzyć próby dla wielu rozmiarów i seedów; kontrolować timestampy i metadane kontenerów.
7. Opublikować kod, surowe wyniki, środowisko i kryteria analizy. Nie dobierać okresu po obejrzeniu wykresu bez korekty wielokrotnych porównań.

## 6. Interfejs do META-DYNAMICS

Stan Sₙ=(Lₙ,H₁(Zₙ),dₙ,Uₙ,Qₙ). Tempo zmian xₙ=(Sₙ−Sₙ₋₁)/Δn, liczone składowo z zachowaniem jednostek. Indeks rund n jest osią eksperymentalną, nie automatycznie czasem fizycznym. Zdarzenia przejścia muszą mieć kryterium zdefiniowane przed analizą.

To opis dynamiki reprezentacji, nie dowód zmiany semantycznej treści. Zachowanie treści przez kompresję bezstratną wynika z D∘C=Id.

## 7. Powiązanie z Helix-Lock

W helix_pro/cipher.py funkcja pack_named_payload() próbuje gzip przed szyfrowaniem i wybiera skompresowaną postać tylko wtedy, gdy jest krótsza. Szyfrowanie AES-GCM jest osobną transformacją kryptograficzną; losowego nonce i ciphertextu nie należy traktować jako dalszej rundy kompresji.

Dla Helix-Lock warto badać próg opłacalności, narzut formatu, czas, pamięć i dokładność odzyskania, a nie szukać liczby kompresji, po której dane same wrócą.

## 8. Status formalny

Dokument pozostaje hipotezą i protokołem, dopóki eksperyment nie zostanie uruchomiony z kodem i surowymi wynikami. Powtarzalne, prerejestrowane wyniki mogą uzasadnić dodanie obserwabli do formalizmu META-DYNAMICS. Nie zmieniać istniejących aksjomatów i nie utożsamiać rund kompresji z obiegami Möbiusa.
