"""core_meta/meta_operator_M.py

Operator ewolucji pola: M = d/dt (Λ, τ, ρ, J).

NAPRAWIONE: oryginalny plik używał `MetaState(...)` wewnątrz compute()
bez importu tej klasy - NameError przy pierwszym użyciu, gdyby ktoś
faktycznie zaimportował ten plik osobno (a nie przez
timdr_meta_dynamics, gdzie wszystko siedziało w jednym pliku i błąd
był niewidoczny). Dodany brakujący import.
"""
from __future__ import annotations

from core_meta.meta_state import MetaState


class MetaOperatorM:
    """Operator ewolucji pola: M = d/dt (Λ, τ, ρ, J)."""

    def compute(self, prev_state: MetaState, next_state: MetaState, dt: float) -> MetaState:
        if dt == 0:
            # NAPRAWIONE: oryginał dzielił przez dt bez zabezpieczenia -
            # dt=0 dawało ZeroDivisionError zamiast czytelnego błędu.
            raise ValueError("dt musi być różne od zera")

        delta = prev_state.delta(next_state)

        return MetaState(
            Lambda=delta.Lambda / dt,
            tau=delta.tau / dt,
            rho=delta.rho / dt,
            J=delta.J / dt,
        )

    def magnitude(self, M_state: MetaState) -> float:
        """Suma wartości bezwzględnych składowych M - używana przez classify_phase()
        i wydzielona osobno (DODANE), żeby nie liczyć jej dwa razy w różnych miejscach."""
        return (
            abs(M_state.Lambda)
            + abs(M_state.tau)
            + abs(M_state.rho)
            + abs(M_state.J)
        )

    def classify_phase(self, M_state: MetaState) -> str:
        """Klasyfikacja fazy pola na podstawie wielkości M:
        - "stabilna"    magnitude < 0.1
        - "przejsciowa" 0.1 <= magnitude < 1.0
        - "krytyczna"   magnitude >= 1.0

        UWAGA: progi (0.1 / 1.0) są dobrane arbitralnie/heurystycznie w
        oryginalnym szkicu, nie skalibrowane na żadnych realnych danych
        pola. Skala Λ/τ/ρ/J zależy całkowicie od tego, co podłączysz jako
        wejście (ceny akcji rzędu tysięcy vs znormalizowane wskaźniki
        0-1 dadzą zupełnie inny rozkład magnitude) - przed użyciem w
        praktyce te progi trzeba przeliczyć na własnych danych, tak jak
        AdaptiveThresholds w projekcie Synoptyk kalibruje progi z okna
        danych zamiast trzymać je na sztywno.
        """
        magnitude = self.magnitude(M_state)

        if magnitude < 0.1:
            return "stabilna"
        elif magnitude < 1.0:
            return "przejsciowa"
        else:
            return "krytyczna"
