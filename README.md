# TIMDR-META-DYNAMICS

Cel: opisać ewolucję całego pola TIMDR w czasie (meta-poziom nad Λ–τ–ρ–J).

Hasło przewodnie: „Jak zmienia się struktura pola, nie tylko sygnał".

## Stan repo (uczciwie, po przeglądzie i poprawkach)

To był zarys/szkic: README opisywało architekturę, część plików istniała
jako pojedyncze klasy, ale całość nie łączyła się w działający pipeline.
Poniżej lista konkretnych rzeczy, które były zepsute, i co zrobiłem:

1. **`main.py` crashował na starcie.** Robił `from analizator3_core import
   load_market_series` na poziomie modułu. `analizator3_core` to osobny,
   zewnętrzny projekt (Analizator Giełdowy 3.0) — nie jest częścią tego
   repo. Efekt: `python gui.py` wywalał się `ModuleNotFoundError`, zanim
   okno zdążyło się pokazać. **Naprawione**: import jest teraz opcjonalny
   i leniwy — jeśli `analizator3_core` nie jest dostępny, `run_meta_analysis()`
   używa syntetycznej serii demo (`load_demo_series()`), więc repo
   uruchamia się i daje przetestować samodzielnie. Prawdziwa integracja z
   Analizatorem Giełdowym 3.0 działa dokładnie tak jak wcześniej, jeśli ten
   moduł jest na `PYTHONPATH`.

2. **`core_meta/meta_operator_M.py`, `analysis/meta_map.py`,
   `analysis/meta_predict.py`** używały `MetaState`/`MetaOperatorM` bez
   importu — `NameError` przy realnym użyciu tych plików osobno (błąd był
   niewidoczny, dopóki wszystko leżało zduplikowane w jednym pliku
   `timdr_meta_dynamics/__init__.py`). **Dodane brakujące importy.**

3. **`models/evolution_field.py` (`FieldEvolution`) i `analysis/meta_map.py`
   (`MetaMap`)** miały sygnatury konstruktorów niezgodne z tym, jak
   faktycznie wywołuje je `main.py` (`FieldEvolution(meta_operator)`,
   `MetaMap(meta_operator)` — operator do konstruktora, nie do metody).
   W oryginalnej postaci obie klasy rzucałyby `TypeError` przy pierwszym
   realnym użyciu z `main.py`. **Sygnatury poprawione**, żeby faktycznie
   pasowały.

4. **`analysis/meta_predict.py` (`MetaPredict`) nie miał w ogóle metody
   `simulate_future()`**, mimo że `main.py` ją wywołuje
   (`predictor.simulate_future(states[-1], M_series[-10:], dt)`). Metoda
   istniała tylko w zduplikowanej wersji w `timdr_meta_dynamics/__init__.py`.
   **Dodana** — wielokrokowa ekstrapolacja Eulera, kumulująca błąd z
   każdym krokiem (nie ma tłumienia w stronę średniej, w przeciwieństwie
   do np. `SynoptykV4.forecast()` w projekcie pogodowym).

5. **`visualization/meta_flow_3d.py` był wymieniony w README, ale nie
   istniał w repo** (sprawdzone bezpośrednio — plik zwracał 404).
   **Dodany od zera**: `plot_meta_flow(S_series)`, trajektoria 3D
   (Λ, τ, ρ) kolorowana po J, matplotlib. To jedyny plik w tym pakiecie,
   który nie jest naprawą, tylko nowym dodatkiem.

6. **Duplikacja logiki**: `timdr_meta_dynamics/__init__.py` definiował
   własną, kompletną kopię wszystkich klas — równolegle do plików pod
   `core_meta/`, `models/`, `analysis/`, `visualization/`, które README
   opisuje jako strukturę repo. Dwie kopie tej samej rzeczy to gotowy
   przepis na rozjazd (dokładnie to, co już raz naprawiałem w
   `synoptyk-f.py`/`synoptyk_f.py` w innym Twoim repo). **Ujednolicone**:
   jedno źródło prawdy w plikach pod `core_meta/models/analysis/visualization`,
   `timdr_meta_dynamics/__init__.py` tylko re-eksportuje pod płaskim
   importem, jakiego oczekuje `main.py`.

7. **`visualization/meta_phase_diagram.py`** mimo nazwy „diagram" jest
   wersją wyłącznie tekstową (drukuje listę faz, nie rysuje nic) — zostało
   bez zmian funkcjonalnych, ale nazwane wprost w komentarzu, żeby nie
   sugerować czegoś, czego kod nie robi. Prawdziwy wykres jest w
   `meta_flow_3d.py` (punkt 5).

8. **`gui.py` wymaga `tkinter`** (standardowa biblioteka, zwykle
   dołączona do desktopowego Pythona, ale nie zawsze obecna w
   minimalnych/headless środowiskach — potwierdzone: w środowisku, w
   którym pisałem i testowałem te poprawki, `tkinter` nie był
   zainstalowany). Testy automatyczne nie odpalają samego `gui.py`
   z tego powodu, ale pokrywają całą logikę pod spodem (`main.py`,
   którą `gui.py` tylko wywołuje).

**24 testy w `tests/test_meta_dynamics.py`** (pytest) — pokrywają każdą z
powyższych poprawek osobno (m.in. `test_field_evolution_simulate_uzywa_konstruktora`,
`test_meta_map_konstruktor_i_build`, `test_meta_predict_simulate_future_*`), plus
integracyjny `test_run_meta_analysis_pelny_pipeline_z_demo_seria`, który
uruchamia cały pipeline od zera bez `analizator3_core` — to jest test,
który w oryginalnym repo wywalałby się na starcie.

## Struktura katalogów

```
core_meta/
    meta_state.py       — MetaState: stan pola {Λ, τ, ρ, J}
    meta_time.py         — MetaTime: miara zmiany struktury (meta-czas)
    meta_operator_M.py    — MetaOperatorM: M = d/dt(Λ, τ, ρ, J) + klasyfikacja fazy
models/
    evolution_field.py    — FieldEvolution: seria M ze serii S
    evolution_helix.py     — HelixEvolution: cykl życia helis (na τ)
    evolution_defect.py    — DefectEvolution: ewolucja anomalii (na ρ)
analysis/
    meta_map.py             — MetaMap: mapa zmian + fazy per krok
    meta_predict.py          — MetaPredict: ekstrapolacja przyszłego stanu
visualization/
    meta_flow_3d.py           — DODANY: trajektoria 3D (matplotlib)
    meta_phase_diagram.py      — wersja tekstowa (patrz punkt 7 wyżej)
timdr_meta_dynamics/
    __init__.py                 — publiczne API (re-eksport z powyższych)
tests/
    test_meta_dynamics.py        — 24 testy (pytest)
main.py    — pipeline: dane -> MetaState -> M-seria -> mapa/fazy -> predykcja
gui.py     — Tkinter GUI nad main.run_meta_analysis()
run.bat    — uruchamia gui.py na Windows
```

## Definicja stanu meta

Stan pola `S_meta(t) = {Λ(t), τ(t), ρ(t), J(t)}`:

- **Λ** (Lambda) — struktura
- **τ** (tau) — transformacja
- **ρ** (rho) — anomalia
- **J** — operator punktowy

## Operator M i klasyfikacja fazy

`M = d/dt (Λ, τ, ρ, J)`, liczony jako różnica między kolejnymi stanami
podzielona przez `dt`. `classify_phase(M)` sumuje wartości bezwzględne
składowych M i klasyfikuje: `stabilna` (< 0.1), `przejsciowa` (0.1–1.0),
`krytyczna` (≥ 1.0).

**Progi 0.1/1.0 są arbitralne** — dobrane heurystycznie w oryginalnym
szkicu, nie skalibrowane na żadnych realnych danych. Skala Λ/τ/ρ/J
zależy całkowicie od tego, co podłączysz jako wejście (ceny akcji rzędu
tysięcy vs znormalizowane wskaźniki 0–1 dadzą zupełnie inny rozkład
magnitude). Przed użyciem produkcyjnym te progi trzeba przeliczyć na
własnych danych — tak jak `AdaptiveThresholds` w projekcie Synoptyk
kalibruje progi z okna danych zamiast trzymać je na sztywno.

## Realna integracja: Analizator Giełdowy v3 (`/api/meta`)

DODANE: zamiast osobnego okna Tkinter na syntetycznych danych demo,
prawdziwa integracja żyje teraz w repo `analizator-gieldowy-v3` (folder
obok tego, ten sam poziom katalogów) jako `meta_dynamics_module.py` +
endpoint `GET /api/meta?ticker=...&period=...` w jego `api.py`.

Ten moduł podłącza tę meta-warstwę do PRAWDZIWEGO `TimdrPacket` z v3
(mapowanie Λ=trm, τ=flow, ρ=resonance, J=volume - uzasadnienie w
docstringu `meta_dynamics_module.py` i w README v3), zamiast do
`analizator3_core`, którego `main.py` w tym repo zakładał, ale który
nigdy nie istniał (patrz punkt 1 wyżej - to był powód, dla którego
`gui.py` w ogóle się nie uruchamiał).

`gui.py`/`run.bat` w tym repo nadal działają (na syntetycznej serii
demo, patrz `load_demo_series()`) - przydatne do testowania samego
silnika `timdr_meta_dynamics` w izolacji, bez zależności od v3/yfinance -
ale to już NIE jest zalecana droga do realnej analizy. Do tego służy
`/api/meta` w `analizator-gieldowy-v3`.

## Użycie

```bash
pip install -r requirements.txt
python main.py          # uruchamia pipeline na syntetycznej serii demo
                          # (albo na realnych danych, jesli masz
                          # analizator3_core na PYTHONPATH - patrz tez
                          # sekcja o /api/meta wyzej, do realnych danych
                          # gieldowych)
python gui.py            # albo run.bat na Windows - GUI Tkinter, demo
pytest tests/ -q          # 24 testy
```

Programowo:

```python
from main import run_meta_analysis, load_demo_series

result = run_meta_analysis(series=load_demo_series(n=60))
result["phases"]          # lista faz per krok M-serii
result["future_states"]    # ekstrapolowane przyszle stany
```

## Integracja z innymi projektami TIMDR

- **Z GIA-TIMDR**: docelowo wspólne definicje Λ–τ–ρ–J (nie zweryfikowane
  tutaj — ten plik nie importuje niczego z GIA-TIMDR, to deklaracja
  zamiaru z oryginalnego szkicu, nie zaimplementowana integracja).
- **Z Analizatorem Giełdowym 3.0**: `main._load_market_series()` — patrz
  punkt 1 wyżej, opcjonalna zależność z fallbackiem na dane demo.
- **Z innymi analizatorami (finanse/astro/fusion)**: `build_meta_states_from_market()`
  oczekuje listy dictów z kluczami `price/trm/flow/volume` — dla innej
  domeny trzeba napisać analogiczną funkcję konwertującą własne S(t) na
  `MetaState`, tak jak `examples/accelerator/analyze_trajectory.py` w
  `universal-state-analyzer` robi to dla trajektorii lattice QCD.

## Czego to NIE jest

Nie jest to zwalidowany model fizyczny ani finansowy. `classify_phase()`
i progi ewolucji helis/defektów (`evolution_helix.py`, `evolution_defect.py`)
to arbitralne heurystyki ze szkicu, nie wyniki kalibracji na realnych
danych. `MetaPredict.simulate_future()` to prosta ekstrapolacja Eulera
pierwszego rzędu z kumulującym się błędem, nie model predykcyjny.
Trafność czegokolwiek tutaj zależy całkowicie od tego, co faktycznie
podłączysz jako dane wejściowe, i wymaga własnej weryfikacji.

## Licencja

MIT — patrz [LICENSE](LICENSE).
