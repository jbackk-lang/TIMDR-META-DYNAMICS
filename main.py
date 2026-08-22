"""main.py

Cel: przekonwertować serię danych (Λ, τ, ρ, J) na M-serię, wykryć fazy,
zbudować mapę i przewidzieć przyszły stan pola.

NAPRAWIONE: oryginał robił `from analizator3_core import load_market_series`
na poziomie modułu. analizator3_core to osobny, zewnętrzny projekt
(Analizator Giełdowy 3.0) - NIE JEST częścią tego repo i nigdzie tu nie
istnieje. Efekt: samo `import main` (a więc i `python gui.py`, bo
gui.py importuje main na starcie) wywalało się natychmiast
ModuleNotFoundError, zanim jakikolwiek kod zdążył się wykonać - GUI nie
zdążyło się nawet otworzyć.

Naprawa: import analizator3_core jest teraz OPCJONALNY i leniwy (w
funkcji, nie na szczycie pliku). Jeśli modułu nie ma, run_meta_analysis()
używa syntetycznej serii demo (load_demo_series()), żeby to repo dało
się uruchomić i przetestować samodzielnie, bez zależności od drugiego
projektu. Prawdziwa integracja z Analizatorem Giełdowym 3.0 działa
dokładnie tak jak wcześniej, jeśli ten moduł jest dostępny na
PYTHONPATH - to zachowanie się nie zmieniło, przestało być tylko
twardym wymaganiem do samego uruchomienia repo.
"""
from __future__ import annotations

import math
import random
from typing import List, Optional

from timdr_meta_dynamics import (
    MetaState,
    MetaOperatorM,
    FieldEvolution,
    MetaMap,
    MetaPredict,
)


def load_demo_series(n: int = 60, seed: int = 42) -> List[dict]:
    """Syntetyczna seria demo (Λ=cena, τ=TRM, ρ=flow, J=wolumen).

    NIE są to prawdziwe dane rynkowe - to tylko fala sinusoidalna + szum
    + jeden wstrzyknięty skok w połowie serii, żeby pipeline dało się
    uruchomić i zweryfikować bez zależności od analizator3_core, i żeby
    faza "krytyczna" faktycznie kiedyś wystąpiła (nie tylko "stabilna"/
    "przejsciowa" na gładkim sygnale).
    """
    rng = random.Random(seed)
    series = []
    for i in range(n):
        price = 100 + 5 * math.sin(i / 5) + rng.uniform(-0.5, 0.5)
        trm = 50 + 3 * math.sin(i / 5 + 1)
        flow = math.sin(i / 3) * 0.5
        volume = 1000 + rng.uniform(-50, 50)
        if i == n // 2:
            # wstrzykniety skok - testuje sciezke "krytyczna" w classify_phase()
            price += 30
            volume += 800
        series.append({"price": price, "volume": volume, "trm": trm, "flow": flow})
    return series


def _load_market_series(path: str) -> List[dict]:
    """Prawdziwe dane z analizator3_core, jeśli dostępny; inaczej demo."""
    try:
        from analizator3_core import load_market_series  # type: ignore
    except ImportError:
        print(
            "[UWAGA] analizator3_core niedostepny (osobny projekt, nie jest "
            "czescia tego repo) - uzywam syntetycznej serii demo zamiast "
            f"realnych danych z '{path}'."
        )
        return load_demo_series()

    return load_market_series(path)


def build_meta_states_from_market(series: List[dict]) -> List[MetaState]:
    """Konwersja danych giełdowych (lub demo) na MetaState.

    Oczekuje listy dictów z kluczami: price, trm, flow, volume.
    Mapowanie Λ=price / τ=trm / ρ=flow / J=volume to JEDEN konkretny
    wybór (jak podłączyć dane giełdowe do 4 wymiarów pola), nie jedyny
    możliwy - dla innej domeny niż giełda trzeba by to przemyśleć od
    nowa (dokładnie tak jak accelerator/analyze_trajectory.py w innym
    Twoim repo dobiera własne 3 kanały zamiast tych czterech).
    """
    meta_states = []
    for point in series:
        state = MetaState(
            Lambda=point["price"],
            tau=point["trm"],
            rho=point["flow"],
            J=point["volume"],
        )
        meta_states.append(state)
    return meta_states


def run_meta_analysis(
    data_path: str = "data/market_series.csv",
    series: Optional[List[dict]] = None,
    dt: float = 1.0,
) -> dict:
    """Pełny pipeline: dane -> MetaState -> M-seria -> mapa/fazy -> predykcja.

    `series`, jeśli podane, pomija wczytywanie z pliku/analizator3_core
    całkowicie - używane w testach (patrz tests/test_meta_dynamics.py),
    żeby testy nie zależały od żadnych zewnętrznych plików/modułów.
    """
    if series is None:
        series = _load_market_series(data_path)

    if len(series) < 2:
        raise ValueError(
            f"Za malo punktow w serii ({len(series)}) - potrzeba co najmniej "
            "2, zeby policzyc chocby jeden krok M-serii."
        )

    states = build_meta_states_from_market(series)

    meta_operator = MetaOperatorM()
    field_evolution = FieldEvolution(meta_operator)
    M_series = field_evolution.simulate(states, dt)

    meta_map = MetaMap(meta_operator)
    map_data = meta_map.build(states, M_series)
    phases = meta_map.detect_transitions(M_series)

    predictor = MetaPredict()
    future_states = predictor.simulate_future(states[-1], M_series[-10:], dt)

    return {
        "states": states,
        "M_series": M_series,
        "phases": phases,
        "future_states": future_states,
        "map_data": map_data,
    }


if __name__ == "__main__":
    result = run_meta_analysis()
    print("Fazy meta-pola:", result["phases"][-20:])
