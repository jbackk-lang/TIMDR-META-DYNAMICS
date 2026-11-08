# AIRP — adaptacyjna ochrona reprezentacji informacji

**Status:** propozycja architektury + prototyp rotacji klucza w Helix-Lock; brak niezależnego audytu bezpieczeństwa. To nie jest nowy aksjomat TIMDR.

## Cel

Zbadać, czy system może zmieniać kryptograficzną reprezentację danych i klucze przy zachowaniu niezmienności treści oraz jej odzyskiwalności przez uprawnionego odbiorcę.

## Rozdzielenie warstw

- Treść X: oryginalne bajty, których integralność jest weryfikowana.
- Reprezentacja E_k(X): ciphertext AES-GCM zależny od klucza i świeżego nonce.
- Stan dostępu: polityka uprawnień, aktywny identyfikator klucza, wersja obiektu i dziennik audytowy.
- Historia: identyfikatory wersji i skróty kryptograficzne; nie przechowujemy w logach plaintextu ani sekretów.

## Niezmiennik

Dla poprawnej rotacji z k₁ do k₂:

D_{k₂}(E_{k₂}(X))=X.

Równość treści nie implikuje równości ciphertextów:
E_{k₁}(X)≠E_{k₂}(X) z wysokim prawdopodobieństwem (świeży nonce).

## Prototyp w Helix-Lock

Moduł `helix_pro.adaptive_rotation.rotate_encrypted_blob`:
1. weryfikuje i odszyfrowuje blob starym kluczem AES-GCM;
2. szyfruje te same bajty nowym kluczem i świeżym nonce;
3. sprawdza, czy nowy blob odtwarza identyczną treść;
4. zwraca nowy blob oraz SHA-256 starego blobu, nowego blobu i treści.

Prototyp obsługuje blob `encrypt_bytes`, nie migruje automatycznie plików HLXP/HLXN ani CounterLock.

## Bezpieczeństwo i granice

- Błędny klucz, AAD lub uszkodzony ciphertext powoduje błąd uwierzytelnienia; system nie modyfikuje ani nie ujawnia treści.
- Rotacja nie unieważnia kopii starego ciphertextu, jeśli napastnik zachował także stary klucz.
- Potrzebne są: atomowe przełączenie aktywnej wersji, kontrola dostępu do kluczy, audyt, kopie zapasowe i procedura odzyskiwania.
- Nie należy celowo zwracać fałszywej/zmienionej treści w odpowiedzi na podejrzaną próbę. Odpowiedź bezpieczna to odmowa, ograniczenie dostępu, alert i zachowanie dowodów.
- Skrót SHA-256 plaintextu jest metadanym kontrolnym; w przypadku danych o małej entropii może umożliwiać zgadywanie treści. Nie publikować go w niezaufanym, jawnym logu. Prototyp zwraca go wywołującemu — produkcyjne logowanie wymaga decyzji threat-modelowej.
- To nie jest audytowany system kryptograficzny.

## Interfejs pojęciowy do META-DYNAMICS

Stan eksperymentalny Sₙ=(vₙ, rₙ, kₙ, aₙ, qₙ):
- vₙ — identyfikator wersji obiektu;
- rₙ — identyfikator/skrót reprezentacji ciphertextu;
- kₙ — identyfikator wersji klucza (nigdy sam klucz);
- aₙ — stan autoryzacji;
- qₙ — wynik weryfikacji integralności.

Tempo zmian opisuje przejścia wersji i zdarzenia, nie „ilość informacji”. Niezmiennikiem jest równość odzyskanych bajtów X oraz poprawny tag AEAD.

## Plan walidacji

1. Testy pozytywne: rotacja zachowuje bajty, nowy blob różni się od starego.
2. Testy negatywne: błędny stary klucz, AAD, tag lub ciphertext — odmowa bez zapisu nowej wersji.
3. Test awarii: przerwanie przed i po atomowym przełączeniu; brak utraty jedynej poprawnej kopii.
4. Test rollback: wykrywanie przywrócenia starej wersji przez zewnętrzny, chroniony rejestr wersji/liczników.
5. Audyt zarządzania kluczami, backupów i retencji.

Dopiero po testach integracyjnych i niezależnym przeglądzie bezpieczeństwa można rozważać wdrożenie produkcyjne.
