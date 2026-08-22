"""analysis/meta_predict.py

Predykcja przyszłego stanu pola TIMDR: S_future = S_now + M_now * dt
(prosta ekstrapolacja Eulera pierwszego rzędu, NIE model NWP/ML).

NAPRAWIONE (dwa błędy):
1. Oryginał nie importował MetaState (NameError przy realnym użyciu
   poza timdr_meta_dynamics/__init__.py).
2. Brakowało metody `simulate_future()` w całości - main.py wywołuje
   `predictor.simulate_future(states[-1], M_series[-10:], dt)`, a
   oryginalny plik miał tylko `predict_next()` (pojedynczy krok).
   simulate_future() dodana tutaj: wielokrokowa ekstrapolacja, krok po
   kroku, karmiąca własny wynik z powrotem jako wejście do następnego
   kroku (dokładnie tak jak w timdr_meta_dynamics/__init__.py, skąd
   main.py najwyraźniej było pisane).
"""
from __future__ import annotations

from typing import List

from core_meta.meta_state import MetaState


class MetaPredict:
    """Predykcja przyszłego stanu pola TIMDR."""

    def predict_next(self, current_state: MetaState, M_state: MetaState, dt: float) -> MetaState:
        """Jeden krok ekstrapolacji: S(t+dt) = S(t) + M(t) * dt."""
        return MetaState(
            Lambda=current_state.Lambda + M_state.Lambda * dt,
            tau=current_state.tau + M_state.tau * dt,
            rho=current_state.rho + M_state.rho * dt,
            J=current_state.J + M_state.J * dt,
        )

    def simulate_future(
        self,
        current_state: MetaState,
        M_series: List[MetaState],
        dt: float,
    ) -> List[MetaState]:
        """Wielokrokowa ekstrapolacja: dla każdego M w M_series liczy kolejny
        stan na bazie POPRZEDNIO wyekstrapolowanego (nie zawsze current_state).

        UWAGA: to jest prosta, deterministyczna ekstrapolacja Eulera - błąd
        kumuluje się z każdym krokiem (brak żadnego tłumienia w stronę
        średniej, w przeciwieństwie np. do SynoptykV4.forecast() w projekcie
        pogodowym, który tłumi ekstrapolację na dłuższym horyzoncie). Im
        dłuższe M_series, tym mniej wiarygodny ostatni punkt.
        """
        states: List[MetaState] = [current_state]

        for M in M_series:
            next_state = self.predict_next(states[-1], M, dt)
            states.append(next_state)

        return states
