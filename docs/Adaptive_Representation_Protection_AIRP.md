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


## Rozszerzenie implementacyjne: trwały rejestr i CounterLock

Helix-Lock zawiera teraz również prototyp:
- `helix_pro.counter_lock.rotate_counter_blob()` — rotuje klucz blobu CounterLock, zachowując odszyfrowany payload i licznik;
- `helix_pro.airp_store.AIRPStore` — trwały rejestr SQLite z wersją, key ID, SHA-256 ciphertextu, transakcyjnym compare-and-swap oraz historią zdarzeń.

Rejestr odrzuca zatwierdzenie rotacji, gdy wersja lub hash poprzedniej reprezentacji nie zgadza się z oczekiwanym stanem. Jest to ochrona przed przypadkowym/starym zapisem i konkurencyjnymi aktualizacjami w granicach zaufanej bazy.

**Ograniczenie threat modelu:** lokalna baza SQLite nie chroni przed napastnikiem, który może podmienić zarówno plik danych, jak i bazę/rejestr oraz backupy. Odporność na rollback wymaga niezależnego, chronionego rejestru (np. usługi transakcyjnej/append-only z oddzielnymi uprawnieniami). Zapis ciphertextu i metadanych SQLite nie jest jedną transakcją; aplikacja musi obsłużyć staging, atomowe przełączenie i odzyskiwanie po awarii.

README Helix-Lock zawiera instrukcję „gdzie co jest i jak używać”, przykłady rotacji, rejestru, CounterLock oraz komendy testowe.


##  Implementation status: Helix-Lock GUI integration (2026-11)

W repozytorium `jbackk-lang/Helix-Lock` podłączono lokalny rejestr AIRP do GUI dla formatów HLXN i HLXP:

- po szyfrowaniu GUI rejestruje hash szyfrogramu, wersję i losowy key ID w `~/.helix_lock/airp.sqlite3` (Windows: katalog profilu użytkownika);
- przed odszyfrowaniem sprawdza zgodność bieżącego pliku z rejestrem i odmawia, gdy wpis nie istnieje albo hash jest inny;
- ponowne szyfrowanie do tej samej ścieżki przesuwa wersję rejestru transakcyjnie;
- checkbox AIRP jest domyślnie włączony; świadome wyłączenie umożliwia obsługę starszych/przeniesionych plików, ale omija kontrolę rejestru;
- format CounterLock (HLXC) jest na razie wyłączony z tej integracji, ponieważ jego dotychczasowy przepływ odszyfrowania nadpisuje plik i wymaga koordynacji transakcyjnej licznika z rejestrem.

Pliki implementacji: `helix_pro/airp_store.py`, `helix_pro_gui.py`; testy: `tests/test_airp_store.py`, `tests/test_helix_pro_gui.py`; workflow: `.github/workflows/airp-tests.yml`.

**Granica gwarancji:** SQLite zapewnia lokalną trwałość i ochronę przed podmianą pliku przy zachowanej, zaufanej bazie. Nie zabezpiecza przed rollbackiem, jeśli atakujący może podmienić jednocześnie szyfrogram, bazę i backup. Rejestr jest przypisany do lokalnej ścieżki; przenoszenie pliku wymaga kontrolowanej migracji wpisu. Testy zostały dodane do GitHub Actions, ale ich wynik należy potwierdzić w zakładce Actions po uruchomieniu workflow.


## AIRP — transakcje plikowe i odzyskiwanie po awarii

W Helix-Lock dodano `AIRPFileTransaction` (`helix_pro/airp_transaction.py`) jako warstwę koordynującą trwały rejestr SQLite z plikiem szyfrogramu. Ponieważ system plików i SQLite nie współdzielą jednej transakcji, protokół wykorzystuje dziennik boczny i staging:

1. Sprawdź, czy plik docelowy odpowiada zarejestrowanej starej wersji.
2. Zapisz dziennik transakcji z hashami starej i nowej reprezentacji oraz ścieżką stagingu.
3. Zapisz nowy szyfrogram do pliku stagingowego w tym samym katalogu i wymuś zapis na dysk.
4. Zatwierdź nową wersję w SQLite przez compare-and-swap.
5. Atomowo podmień plik docelowy i usuń dziennik.

Procedura odzyskiwania rozpoznaje trzy stany:
- **stara wersja w rejestrze:** transakcja nie została zatwierdzona — staging jest odrzucany;
- **nowa wersja w rejestrze:** transakcja została zatwierdzona — podmiana jest dokańczana ze stagingu;
- **stan niejednoznaczny:** operacja jest zatrzymywana, pliki pozostają do ręcznej analizy.

To zabezpiecza przed typowymi przerwami procesu pomiędzy zatwierdzeniem rejestru a podmianą pliku. Nie zapewnia odporności na napastnika mogącego jednocześnie podmienić bazę, dziennik i staging. Nie przechowuje kluczy ani plaintextu; wejściowy nowy szyfrogram musi być wcześniej poprawnie utworzony i zweryfikowany przez warstwę kryptograficzną.

Testy protokołu: `tests/test_airp_transaction.py` (normalny commit, awaria przed podmianą, odrzucenie niezatwierdzonej transakcji, wykrycie stanu niejednoznacznego).


## Niezależny łańcuch zaufania AIRP — implementacja Helix-Lock

W Helix-Lock dodano następujące elementy wykonawcze:

- `helix_pro.airp_ledger.AIRPIntegrityLedger`: globalnie sekwencjonowany łańcuch zdarzeń SHA-256 z odwołaniem każdego wpisu do poprzedniego.
- Punkty kontrolne podpisywane Ed25519; weryfikator wymaga przypiętego klucza publicznego.
- Kontrakt `TrustAnchor`: zewnętrzny rejestr ma atomowo odrzucać cofnięcie numeru sekwencji oraz rozwidlenie tego samego numeru.
- Weryfikacja wykrywa uszkodzenie łańcucha, cofnięcie lokalnej bazy poniżej zewnętrznego checkpointu i rozbieżność historii.
- `helix_pro.airp_counter.AIRPCounterLock`: wiąże zaakceptowany licznik CounterLock z historią zdarzeń; powtórzony lub niższy licznik jest odrzucany.
- `helix_pro.airp_recovery`: koperta klucza danych AES-256-GCM pod niezależnym 256-bitowym kluczem odzyskiwania; identyfikator obiektu i klucza są uwierzytelnionym AAD.

**Warunek bezpieczeństwa:** sam lokalny łańcuch i lokalny podpis nie dają odporności na cofnięcie całej bazy. Funkcja pełnej weryfikacji zewnętrznej działa dopiero po podłączeniu niezależnie administrowanego `TrustAnchor`, zachowującego ostatni checkpoint poza hostem. Repozytorium udostępnia kontrakt i testowy adapter pamięciowy, nie deklaruje jeszcze wdrożonej usługi zewnętrznej.

Testy: `tests/test_airp_ledger.py` oraz `tests/test_airp_recovery.py`. Aktualny CI dla Pythona 3.11 i 3.12: 86 testów na każdej wersji, zakończonych powodzeniem.
