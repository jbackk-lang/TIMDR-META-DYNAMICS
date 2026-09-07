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
        damping: float = 1.0,
    ) -> List[MetaState]:
        """Wielokrokowa ekstrapolacja: dla każdego M w M_series liczy kolejny
        stan na bazie POPRZEDNIO wyekstrapolowanego (nie zawsze current_state).

        NAPRAWIONE (tłumienie, `damping`): oryginalnie to była czysta,
        nietłumiona ekstrapolacja Eulera - błąd kumulował się bez
        ograniczeń krok po kroku, w przeciwieństwie np. do
        SynoptykV4.forecast() w projekcie pogodowym, który tłumi
        ekstrapolację w stronę lokalnej średniej na dłuższym horyzoncie
        (patrz analyzer/synoptyk_v4.py w synoptyk-v2.0). Ten sam wzorzec
        zastosowany tutaj: krok i miesza czystą (nietłumioną) ekstrapolację
        Eulera E_i z kotwicą - ostatnim realnie zaobserwowanym stanem
        (`current_state`, jedyny "realny" punkt jaki ta funkcja dostaje,
        bo M_series to już same delty, nie surowa historia S):

            E_i = S_{i-1} + M_i * dt                 (czysta ekstrapolacja)
            w   = damping ** i
            S_i = w * E_i + (1 - w) * current_state    (tłumienie do kotwicy)

        Krótki horyzont (małe i) -> blisko czystej ekstrapolacji Eulera.
        Długi horyzont (duże i) -> tłumione w stronę current_state zamiast
        ekstrapolować trend w nieskończoność.

        `damping=1.0` (DOMYŚLNE) odtwarza dokładnie stare, nietłumione
        zachowanie - zachowane jako domyślne świadomie, żeby nie zmieniać
        cicho wyniku main.py/istniejących testów. Dla realnego użycia na
        dłuższym horyzoncie sensowne jest `damping` w okolicach 0.85 (ta
        sama domyślna wartość co w SynoptykV4.forecast()), ale to trzeba
        by skalibrować na realnych danych, tak samo jak progi w
        evolution_helix.py/classify_phase() - nie ma tu jednej uniwersalnej
        stałej.
        """
        states: List[MetaState] = [current_state]
        extrapolated = current_state

        for i, M in enumerate(M_series, start=1):
            extrapolated = self.predict_next(extrapolated, M, dt)
            w = damping ** i
            blended = MetaState(
                Lambda=w * extrapolated.Lambda + (1 - w) * current_state.Lambda,
                tau=w * extrapolated.tau + (1 - w) * current_state.tau,
                rho=w * extrapolated.rho + (1 - w) * current_state.rho,
                J=w * extrapolated.J + (1 - w) * current_state.J,
            )
            states.append(blended)

        return states
